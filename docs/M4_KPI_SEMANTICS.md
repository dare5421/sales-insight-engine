# 📄 M4_KPI_SEMANTICS.md

## Milestone M4 — KPI Semantics Definition

### Purpose
Define **clear, unambiguous semantics** for KPI views derived from the canonical layer.
This document locks:
- grain
- metrics
- formulas
- filters
- edge-case handling

All KPIs are implemented **only as SQL views**.
No KPI logic is allowed in Python.

---

## Source of Truth
- **Primary source:** `canonical_sales`
- **Excluded from calculations:** `dq_issues`, `dq_run_stats`
- Records with `ERROR` DQ severity are not present in canonical and therefore implicitly excluded.
- Records with `WARNING` severity are included.

---

## Common Definitions

### Canonical Grain
- **Input grain:** invoice-line (`invoice_id + product_id`)

### Transaction Semantics
- `transaction_type ∈ {SALE, RETURN}`
- `sign`:
  - SALE → `+1`
  - RETURN → `-1`

### Amount Semantics
- `net_amount`: absolute monetary value per line
- **Signed amount:** `net_amount * sign`

### Date Semantics
- All KPIs use:
  - `event_date_gregorian`
- Derived columns:
  - `day = event_date_gregorian::date`
  - `month = date_trunc('month', event_date_gregorian)::date`

---

## KPI 1 — Net Sales Daily

### View Name
`kpi_net_sales_daily`

### Business Question
“How much did we sell per day, after returns?”

### Grain
- **One row per day**

### Metrics
| Column | Definition |
|---|---|
| day | Gregorian calendar date |
| net_sales_amount | SUM(net_amount * sign) |
| gross_sales_amount | SUM(net_amount) WHERE transaction_type='SALE' |
| returns_amount | SUM(net_amount) WHERE transaction_type='RETURN' |
| invoice_count | COUNT(DISTINCT invoice_id) |
| line_count | COUNT(*) |

### Edge Cases
- Days with only returns → `net_sales_amount` may be negative (allowed).
- No artificial zero-filling for missing days.

---

## KPI 2 — Return Rate by Product (Monthly)

### View Name
`kpi_return_rate_by_product_month`

### Business Question
“Which products have a high return rate over time?”

### Grain
- **One row per (product_id, month)**

### Metrics
| Column | Definition |
|---|---|
| product_id | Product identifier |
| month | Gregorian month |
| gross_sales_amount | SUM(net_amount) WHERE SALE |
| returns_amount | SUM(net_amount) WHERE RETURN |
| return_rate_amount | returns_amount / gross_sales_amount |
| sale_line_count | COUNT(*) WHERE SALE |
| return_line_count | COUNT(*) WHERE RETURN |
| return_rate_lines | return_line_count / sale_line_count |

### Edge Cases
- If `gross_sales_amount = 0` → `return_rate_amount = NULL`
- If `sale_line_count = 0` → `return_rate_lines = NULL`
- Products with only returns are retained (rates = NULL)

---

## KPI 3 — Top Customers (Monthly)

### View Name
`kpi_top_customers_month`

### Business Question
“Who are our most valuable customers per month (net of returns)?”

### Grain
- **One row per (customer_id, month)**

### Metrics
| Column | Definition |
|---|---|
| customer_id | Customer identifier |
| month | Gregorian month |
| net_sales_amount | SUM(net_amount * sign) |
| gross_sales_amount | SUM(net_amount) WHERE SALE |
| returns_amount | SUM(net_amount) WHERE RETURN |
| invoice_count | COUNT(DISTINCT invoice_id) |
| active_days | COUNT(DISTINCT event_date_gregorian::date) |
| customer_rank | RANK() over (month order by net_sales_amount desc) |

### Edge Cases
- Customers with negative net sales are ranked normally.
- No hard-coded TOP N inside the view.

---

## Optional KPI — Salesperson Performance (Monthly)

### View Name
`kpi_salesperson_performance_month`

### Status
Optional. Implement only if `salesperson_id` is reliable in canonical data.

### Grain
- **One row per (salesperson_id, month)**

### Metrics
| Column | Definition |
|---|---|
| salesperson_id | Salesperson identifier |
| month | Gregorian month |
| net_sales_amount | SUM(net_amount * sign) |
| gross_sales_amount | SUM(net_amount) WHERE SALE |
| returns_amount | SUM(net_amount) WHERE RETURN |
| invoice_count | COUNT(DISTINCT invoice_id) |
| unique_customers | COUNT(DISTINCT customer_id) |
| avg_invoice_value | net_sales_amount / NULLIF(invoice_count,0) |

---

## Naming Conventions
- Views: `kpi_<metric>_<grain>`
- Monetary columns end with `_amount`
- Date columns: `day`, `month`

---

## Non-Goals
- No KPI persistence tables
- No parameterized logic
- No backfilling logic
- No DQ joins inside KPIs

---

## Completion Criteria for M4
- All KPI views implemented in `src/db/views_kpi.sql`
- Semantics unchanged from this document
- Views are idempotent and replaceable
- README updated with KPI descriptions
