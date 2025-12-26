# Sales & Customer Insight Engine

## Overview
This project builds a **production-style data engineering pipeline** for sales analytics in a distribution company.

The pipeline ingests raw monthly sales CSV exports (with Persian headers), stores them immutably for traceability, normalizes them into a **canonical, source-agnostic sales fact model**, applies data-quality checks, and produces **decision-ready KPIs**.
An optional API layer can later expose KPI views.

This project is designed as a **data engineer portfolio project**, following real-world modeling and pipeline principles.

---

## Problem Statement
Sales data is exported monthly from operational systems (e.g. *Karamad*) as large CSV files with:
- Persian headers
- Mixed data quality
- Sales and returns interleaved
- Operational and organizational attributes mixed together

The goal is to:
- Preserve raw source data for audit and reprocessing
- Create a clean, stable **canonical sales fact layer**
- Enable accurate historical analysis (sales, returns, trends)
- Prevent business logic leakage into ingestion and modeling layers

---

## Architecture

Raw CSV Files  
↓  
RAW Tables (immutable, traceable)  
↓  
Canonical Fact Tables (invoice-line sales & returns)  
↓  
KPI Views (analytics-ready)  
↓  
(Optional) API  

---

## Design Principles
- **RAW is immutable**: no parsing, no business logic
- **Canonical represents events**, not organizational structure
- **Fact vs Dimension separation** is strictly enforced
- **Historical correctness** is prioritized over convenience
- **No aggregation or KPI logic** is allowed in the Canonical layer
- Canonical schema is **source-agnostic and stable over time**

---

## Tech Stack
- PostgreSQL (Dockerized)
- Python (CSV ingestion, normalization, data quality)
- YAML (schema and mapping contracts)
- (Optional later) FastAPI (serving KPI views)

---

## Repository Structure

sales-insight-engine/
  README.md
  PLAN.md
  .gitignore
  .env.example
  docker-compose.yml

  data/
    karamad/        # monthly CSV exports (ignored in git)
    mabna/          # future: legacy system exports
    samples/        # sanitized small samples for testing

  config/
    mapping_karamad.yml
    mapping_mabna.yml

  docs/
    glossary.yml    # FA → EN column meanings and business terms

  src/
    common/
      config.py
      utils.py

    db/
      ddl_raw.sql
      ddl_canonical.sql
      views_kpi.sql

    ingestion/
      load_raw.py   # CSV → RAW loader (idempotent)

    transform/
      normalize_current.py   # RAW → Canonical (source-agnostic)

    quality/
      checks.py     # data quality rules and reporting

---

## Pipeline Layers

### Layer 0 — RAW (Traceability)
**Goal:** Preserve source data exactly as received.

- One row per CSV row
- All business columns stored as TEXT
- No type casting or interpretation
- Metadata columns:
  - source_file
  - load_batch_id
  - ingested_at
  - row_hash
- Idempotent ingestion (duplicate rows are ignored)

This layer enables:
- Auditing
- Reprocessing
- Debugging source issues

---

### Layer 1 — Canonical (Sales Fact)
**Goal:** Create a clean, stable **invoice-line sales fact table**.

Canonical rules:
- Each record represents **one sales or return transaction**
- Sales and returns are kept together using:
  - transaction_type (SALE / RETURN)
  - Signed numeric values
- Canonical schema is **independent of source system structure**
- Organizational attributes are intentionally excluded:
  - line, route, supervisor, city, brand, supplier, etc.

Date handling:
- invoice_date_jalali represents the **actual sales visit date**
- Gregorian date is derived during normalization

Discount handling:
- Multiple source discount columns are combined into a single discount_amount
- No promotion or campaign logic exists at this layer

---

### Layer 2 — Data Quality
**Goal:** Make data reliability explicit.

- Rule-based checks on Canonical data
- Examples:
  - Missing required fields
  - Negative quantities where invalid
  - Net amount inconsistencies
- Issues recorded in a dq_issues table
- Metrics per pipeline run

---

### Layer 3 — KPI Views
**Goal:** Provide analytics-ready, stable outputs.

Examples:
- Net sales per day (signed sales + returns)
- Return rate by product
- Top customers per month
- Salesperson performance (optional)

All KPI logic lives **only in views**, never in Canonical tables.

---

### Layer 4 — Optional API
**Goal:** Expose KPIs for dashboards or external tools.

- FastAPI skeleton
- Read-only endpoints
- Dockerized deployment

---

## Milestones

- **M0 — Foundation**
  - Repo structure
  - Dockerized PostgreSQL
  - Environment setup

- **M1 — RAW Layer**
  - RAW schema
  - CSV → RAW ingestion
  - Idempotency

- **M2 — Canonical Layer**
  - Canonical contract definition
  - Mapping configuration
  - Normalization logic

- **M3 — Data Quality**
  - DQ rules
  - Issue reporting

- **M4 — KPI Views**
  - Core business metrics

- **M5 — Optional API**
  - FastAPI endpoints

---

## Local Setup

### Start PostgreSQL
docker compose up -d

### Verify DB connection
docker exec -it sales_engine_db psql -U postgres -d sales_engine -c "select 1;"

Connection details (local dev):
- Host: localhost
- Port: 5433
- Database: sales_engine
- User: postgres
- Password: postgres

---

## Data Privacy
- Real company data is **never committed**
- data/karamad/ and data/mabna/ are ignored via .gitignore
- Only sanitized samples may be stored under data/samples/

---

## License
Internal / personal portfolio project
