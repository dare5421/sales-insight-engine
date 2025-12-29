-- ===============================
-- KPI VIEWS
-- source: canonical_sales
-- Semantics: docs/M4_KPI_SEMANTICS.md
-- ===============================

-- =========================================================
-- KPI: net_sales_daily
--
-- Grain:
--   Each row represents one calendar day.
--
-- Time semantics:
--   Day is derived from invoice_date_gregorian (event date).
--   Sales and returns are attributed to the day they are recorded.
--
-- Metrics:
--   - gross_sales_amount:
--       Total sales amount for the day
--       (transaction_type = 'SALE')
--
--   - returns_amount:
--       Total returned amount for the day
--       (transaction_type = 'RETURN')
--       Returned amounts are stored as negative values in canonical,
--       so ABS(net_amount) is used to represent magnitude.
--
--   - net_sales_amount:
--       Net sales after returns
--       Calculated as SUM(net_amount * sign)
--
-- Additional counters:
--   - invoice_count:
--       Number of distinct invoices recorded on the day
--
--   - line_count:
--       Number of invoice lines recorded on the day
--       (sanity / volume indicator, not a business KPI)
-- =========================================================

CREATE OR REPLACE VIEW kpi_net_sales_daily AS
SELECT
    invoice_date_gregorian AS day,

    -- Net sales after returns
    SUM(net_amount * sign) AS net_sales_amount,

    -- Gross sales (sales only)
    SUM(net_amount)
        FILTER (WHERE transaction_type = 'SALE')
        AS gross_sales_amount,

    -- Total returned amount (absolute value)
    SUM(ABS(net_amount))
        FILTER (WHERE transaction_type = 'RETURN')
        AS returns_amount,

    COUNT(DISTINCT invoice_id) AS invoice_count,
    COUNT(*) AS line_count

FROM canonical_sales
GROUP BY invoice_date_gregorian;

-- =========================================================
-- KPI: return_rate_by_product_month
--
-- Grain:
--   Each row represents one (product_id, calendar month)
--
-- Time semantics:
--   Month is derived from invoice_date_gregorian (event date).
--   Sales and returns are attributed to the month they are recorded.
--
-- Numerator:
--   Total returned quantity in the month
--   - transaction_type = 'RETURN'
--   - quantity is negative in canonical, so ABS(quantity) is used
--
-- Denominator:
--   Total sold quantity in the month
--   - transaction_type = 'SALE'
--   - quantity is positive
--
-- Edge cases:
--   - If sale_quantity = 0, return_rate is set to NULL
--     (division by zero avoided via NULLIF)
-- =========================================================

CREATE OR REPLACE VIEW kpi_return_rate_by_product_month AS
SELECT
    product_id,

    -- Calendar month derived from event date
    DATE_TRUNC('month', invoice_date_gregorian)::date AS month,

    -- Total quantity sold in the month (denominator)
    SUM(quantity)
        FILTER (WHERE transaction_type = 'SALE')
        AS sale_quantity,

    -- Total quantity returned in the month (numerator)
    SUM(ABS(quantity))
        FILTER (WHERE transaction_type = 'RETURN')
        AS return_quantity,

    -- Return rate: returned units / sold units
    SUM(ABS(quantity))
        FILTER (WHERE transaction_type = 'RETURN')
    /
    NULLIF(
        SUM(quantity)
            FILTER (WHERE transaction_type = 'SALE'),
        0
    ) AS return_rate

FROM canonical_sales
GROUP BY
    product_id,
    DATE_TRUNC('month', invoice_date_gregorian);
