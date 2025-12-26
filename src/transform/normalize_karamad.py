import os
from decimal import Decimal
import psycopg2
import yaml
import jdatetime


# =========================
# DB connection
# =========================
def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        dbname=os.getenv("DB_NAME", "sales_engine"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


# =========================
# Mapping loader (contract only)
# =========================
def load_mapping(path="config/mapping_karamad.yml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# =========================
# Helpers
# =========================
def parse_numeric(value):
    """
    Convert numeric-like strings such as '764,463' to Decimal.
    """
    if value is None:
        return None

    if isinstance(value, (int, float, Decimal)):
        return Decimal(value)

    value = str(value).replace(",", "").strip()
    if value == "":
        return None

    try:
        return Decimal(value)
    except Exception:
        return None


def jalali_to_gregorian(jalali_str):
    """
    Convert Jalali date YYYY/MM/DD to datetime.date
    """
    if jalali_str is None:
        return None

    jalali_str = jalali_str.strip()
    if jalali_str == "":
        return None

    try:
        y, m, d = map(int, jalali_str.split("/"))
        return jdatetime.date(y, m, d).togregorian()
    except Exception:
        return None


# =========================
# Normalize logic
# =========================
def normalize():
    # mapping is a documented contract (not dynamic yet)
    mapping = load_mapping()

    processed = 0
    inserted = 0
    skipped = 0

    skipped_rows = []

    with connect() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                select
                    source_system,
                    source_file,
                    load_batch_id,
                    row_hash,

                    c03, -- salesperson_id
                    c05, -- product_id
                    c29, -- transaction_type_raw (فارسی/انگلیسی)

                    c39, -- invoice_id
                    c42, -- customer_id

                    c38, -- system_date_jalali
                    c54, -- reference_date_jalali

                    c46, -- quantity
                    c47, -- unit_price
                    c48, -- gross_amount
                    c49, -- discount_volume
                    c50, -- discount_cash
                    c52, -- net_amount

                    ingested_at
                from raw_karamad_sales
            """)

            for r in cur.fetchall():
                processed += 1

                (
                    source_system,
                    source_file,
                    load_batch_id,
                    raw_row_hash,

                    salesperson_id,
                    product_id,
                    transaction_type_raw,

                    invoice_id,
                    customer_id,

                    system_date_jalali,
                    reference_date_jalali,

                    quantity,
                    unit_price,
                    gross_amount,
                    discount_volume,
                    discount_cash,
                    net_amount,

                    ingested_at,
                ) = r

                # -------------------------
                # Numeric cleanup (truth source)
                # -------------------------
                quantity = parse_numeric(quantity)
                unit_price = parse_numeric(unit_price)
                gross_amount = parse_numeric(gross_amount)
                discount_volume = parse_numeric(discount_volume) or Decimal(0)
                discount_cash = parse_numeric(discount_cash) or Decimal(0)
                net_amount = parse_numeric(net_amount)

                if None in (quantity, unit_price, gross_amount, net_amount):
                    skipped += 1
                    skipped_rows.append({
                        "row_hash": raw_row_hash,
                        "invoice_id": invoice_id,
                        "reason": "invalid_numeric",
                    })
                    continue

                discount_amount = discount_volume + discount_cash

                # -------------------------
                # Robust transaction type detection
                # -------------------------
                is_return = False

                if net_amount is not None and quantity is not None:
                    if net_amount < 0 or quantity < 0:
                        is_return = True
                elif transaction_type_raw and "برگشت" in transaction_type_raw:
                    is_return = True


                if is_return:
                    transaction_type = "RETURN"
                    sign = -1
                    event_date_jalali = system_date_jalali
                else:
                    transaction_type = "SALE"
                    sign = 1
                    # fallback: اگر تاریخ مرجع نبود، تاریخ سیستم
                    event_date_jalali = reference_date_jalali or system_date_jalali

                # -------------------------
                # Date handling
                # -------------------------
                invoice_date_gregorian = jalali_to_gregorian(event_date_jalali)
                if invoice_date_gregorian is None:
                    skipped += 1
                    skipped_rows.append({
                        "row_hash": raw_row_hash,
                        "invoice_id": invoice_id,
                        "transaction_type": transaction_type,
                        "system_date_jalali": system_date_jalali,
                        "reference_date_jalali": reference_date_jalali,
                        "reason": "missing_event_date",
                    })
                    continue

                # -------------------------
                # Insert canonical (idempotent)
                # -------------------------
                cur.execute("""
                    insert into canonical_sales (
                        source_system,
                        source_file,
                        load_batch_id,
                        raw_row_hash,

                        invoice_id,
                        customer_id,
                        product_id,
                        salesperson_id,

                        invoice_date_jalali,
                        invoice_date_gregorian,

                        transaction_type,
                        sign,

                        quantity,
                        unit_price,
                        gross_amount,
                        discount_amount,
                        net_amount,

                        ingested_at
                    )
                    values (
                        %s,%s,%s,%s,
                        %s,%s,%s,%s,
                        %s,%s,
                        %s,%s,
                        %s,%s,%s,%s,%s,
                        %s
                    )
                    on conflict (source_system, raw_row_hash) do nothing
                """, (
                    source_system,
                    source_file,
                    load_batch_id,
                    raw_row_hash,

                    invoice_id,
                    customer_id,
                    product_id,
                    salesperson_id,

                    event_date_jalali,
                    invoice_date_gregorian,

                    transaction_type,
                    sign,

                    quantity,
                    unit_price,
                    gross_amount,
                    discount_amount,
                    net_amount,

                    ingested_at
                ))

                inserted += 1

    # -------------------------
    # Reporting
    # -------------------------
    print(f"Processed: {processed}")
    print(f"Inserted (attempted): {inserted}")
    print(f"Skipped: {skipped}")

    if skipped_rows:
        import csv
        with open("skipped_rows.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=skipped_rows[0].keys())
            writer.writeheader()
            writer.writerows(skipped_rows)

        print(f"Skipped rows written to skipped_rows.csv ({len(skipped_rows)})")


# =========================
# Entry point
# =========================
def main():
    normalize()


if __name__ == "__main__":
    main()
