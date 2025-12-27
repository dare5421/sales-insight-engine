# Sales & Customer Insight Engine

## Overview
This repository contains a **production-grade data engineering pipeline** for sales analytics in a distribution company.

The pipeline ingests raw monthly sales CSV exports (with Persian headers), stores them **immutably for traceability**, normalizes them into a **canonical, source-agnostic sales fact model**, applies **explicit data quality controls**, and produces **analytics-ready KPI views**.

The project is designed as a **realistic data engineering portfolio**, following industry practices in data modeling, idempotent ingestion, data quality enforcement, and analytical layer separation.

---

## Problem Statement
Sales data is exported monthly from operational systems (e.g. *Karamad*) as large CSV files that contain:

- Persian headers
- Mixed numeric and date formats
- Sales and returns interleaved
- Business events mixed with organizational attributes
- Inconsistent data quality

The goals of this project are to:

- Preserve raw source data for auditability and reprocessing
- Build a clean, stable **canonical sales fact layer**
- Explicitly track data quality issues
- Enable reliable historical KPIs without leaking business logic into ingestion

---

## High-Level Architecture

```
Raw CSV Files
    ↓
RAW Tables (immutable, traceable)
    ↓
Canonical Sales Facts (SALE / RETURN unified)
    ↓
Data Quality Layer (row-level + run-level)
    ↓
KPI Views (analytics-ready)
    ↓
(Optional) API
```

---

## Core Design Principles

- **RAW is immutable**
  - No parsing, no casting, no business logic
- **Canonical represents business events**
  - Not organizational structure
- **Fact vs Dimension separation**
  - Strictly enforced
- **Historical correctness > convenience**
- **No KPI logic in Canonical**
- Canonical schema is **source-agnostic and stable over time**
- Data quality is **measured, not assumed**

---

## Tech Stack

- PostgreSQL (Dockerized)
- Python (ingestion, normalization, data quality)
- YAML (schema & mapping contracts)
- Docker Compose
- (Optional, later) FastAPI for KPI exposure

---

## Repository Structure

```
sales-insight-engine/
├── README.md
├── PLAN.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── config/
│   └── mapping_karamad.yml
│
├── data/
│   ├── karamad/        # real monthly CSVs (git-ignored)
│   └── samples/        # sanitized samples for testing
│
├── src/
│   ├── db/
│   │   ├── ddl_raw.sql
│   │   ├── ddl_canonical.sql
│   │   └── migrations/
│   │       └── 002_add_dq_run_stats.sql
│   │
│   ├── ingestion/
│   │   └── load_raw.py
│   │
│   ├── transform/
│   │   ├── normalize_karamad.py
│   │   ├── dq.py
│   │   └── dq_contract.py
│   │
│   └── quality/
│       └── (future extensions)
```

---

## Pipeline Layers

### Layer 0 — RAW (Traceability Layer)
Preserves source data exactly as received. Immutable, idempotent, and audit-friendly.

### Layer 1 — Canonical (Sales Fact Layer)
Unified SALE / RETURN facts with stable schema and signed metrics.

### Layer 2 — Data Quality
Row-level issue logging and run-level quality summaries (`dq_issues`, `dq_run_stats`).

### Layer 3 — KPI Views
Analytics-ready SQL views for business metrics.

### Layer 4 — Optional API
Read-only FastAPI layer for external consumption.

---

## Milestones

- **M0 — Foundation**
- **M1 — RAW Layer**
- **M2 — Canonical Layer**
- **M3 — Data Quality**
- **M4 — KPI Views**
- **M5 — Optional API**

---

## Local Development

```bash
docker compose up -d
docker exec -it sales_engine_db psql -U postgres -d sales_engine -c "select 1;"
```

---

## Data Privacy
Real company data is never committed. Only sanitized samples may exist.

---

## License
Internal / personal portfolio project
