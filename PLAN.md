# PLAN (Milestones)

## M0 — Foundation (Repo + DB)
- [x] Create repo structure
- [x] Create docker-compose for PostgreSQL
- [x] Bring DB up + verify connection (host port 5433)
- [x] Add .gitignore + .env.example + README skeleton (clean + complete)

## M1 — RAW Layer (Layer 0)
- [x] Design RAW table schema (raw_karamad_sales + indexes)
- [x] Apply ddl_raw.sql to DB
- [x] Implement load_raw.py (CSV -> RAW)
- [x] Idempotency: re-run same file inserts 0 new rows

## M2 — Canonical Layer (Layer 1)
- [x] Define CORE columns (20–25)
- [x] Create mapping_karamad.yml (FA->EN + types)
- [x] Create canonical tables (ddl_canonical.sql)
- [x] Implement normalize_karamad.py (RAW -> Canonical)
- [x] Sale vs Return handling (transaction_type + sign)
- [x] Date handling (jalali keep + gregorian)

## M3 — Data Quality
- [x] Define DQ rules
- [x] Implement DQ report (dq_issues table + export)
- [x] Logging (counts/errors per run)

## M4 — KPI Views
- [x] net_sales_daily
- [x] return_rate_by_product
- [x] top_customers_month
- [x] salesperson_performance (optional)

## M5 — Optional API
- [x] FastAPI skeleton + DB connection
- [x] Endpoints for KPIs/insights
- [x] Dockerize API

## Hard Rules
- No legacy data until M4 is done.
- No API until M3 is done.
- Work-in-progress limit: max 2 tasks at a time.
