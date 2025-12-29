# Sales & Customer Insight Engine

## Overview
This repository contains a data engineering project built around a **real-world sales dataset** from a distribution company.

The project starts from raw monthly CSV exports and ends with **reliable, analytics-ready KPIs**, while keeping the full data lineage intact.  
The focus is not on dashboards or UI, but on building a **correct and auditable data pipeline**.

This is a hands-on portfolio project that reflects how sales data is typically handled (and mishandled) in practice.

---

## Background & Problem
Sales data is exported periodically from operational systems (e.g. *Karamad*) as CSV files. In reality, these files include:

- Persian column names  
- mixed numeric formats (commas, negatives, strings)  
- sales and returns in the same dataset  
- multiple date fields with unclear semantics  
- missing or inconsistent values  

In many organizations, this data is cleaned “just enough” for reporting, which makes historical analysis unreliable and hard to debug.

This project takes the opposite approach: **nothing is hidden, nothing is silently fixed**.

---

## Design Goals
The pipeline was designed with the following goals in mind:

- Preserve raw source data exactly as received  
- Normalize data into a stable, source-agnostic sales fact model  
- Explicitly detect and record data quality issues  
- Keep business logic out of ingestion scripts  
- Build KPIs only on top of canonical data  

---

## High-Level Architecture

```
Raw CSV files
    ↓
RAW tables (immutable, idempotent)
    ↓
Canonical sales facts
    ↓
Data quality tracking
    ↓
KPI views
    ↓
(Optional) Read-only API
```

---

## Core Principles

- RAW data is immutable and reprocessable  
- Canonical tables represent business events, not reports  
- Sales and returns are unified using explicit sign logic  
- Data quality is measured and logged, not assumed  
- KPIs live in SQL views, not application code  
- Historical correctness is preferred over convenience  

---

## Tech Stack

- PostgreSQL (Dockerized)
- Python (batch ingestion and transformation)
- YAML (schema and mapping contracts)
- Docker Compose
- FastAPI (optional, read-only KPI exposure)

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
│   └── samples/        # sanitized examples
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
│   └── api/
│       └── read-only FastAPI endpoints
```

---

## Pipeline Layers

### RAW Layer
Stores incoming CSV data exactly as received.  
No parsing, no casting, no business rules.

### Canonical Layer
Transforms raw rows into a unified sales fact table with:
- explicit SALE / RETURN handling  
- signed numeric values  
- consistent date semantics  

### Data Quality Layer
Tracks:
- row-level issues (e.g. invalid numeric, missing invoice)
- run-level statistics for each pipeline execution

### KPI Layer
Provides analytics-ready SQL views such as:
- daily net sales
- return rate by product and month
- top customers per month

### Optional API
A thin, read-only FastAPI layer that exposes KPI views without duplicating logic.

---

## Milestones
The project was implemented incrementally:

- M0 — Repository & database setup  
- M1 — RAW ingestion  
- M2 — Canonical modeling  
- M3 — Data quality tracking  
- M4 — KPI views  
- M5 — Optional API layer  

---

## Local Setup

```bash
docker compose up -d
docker exec -it sales_engine_db psql -U postgres -d sales_engine -c "select 1;"
```

Batch ingestion and normalization are executed as standalone scripts.

---

## Data Privacy
Real company data is never committed to this repository.  
Only sanitized samples may be included for demonstration purposes.

---

## License
Personal / portfolio project
