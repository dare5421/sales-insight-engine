-- Canonical Sales Fact Table
-- Source-agnostic, invoice-line level sales & returns
-- No KPI logic, no aggregation

create table if not exists canonical_sales (
  canonical_id bigserial primary key,

  -- Source & lineage
  source_system text not null,
  source_file text not null,
  load_batch_id text not null,
  raw_row_hash text not null,

  -- Business identifiers (event actors)
  invoice_id text not null,
  customer_id text not null,
  product_id text not null,
  salesperson_id text not null,

  -- Event date (actual sales visit date)
  invoice_date_jalali text not null,
  invoice_date_gregorian date not null,

  -- Transaction semantics
  transaction_type text not null check (transaction_type in ('SALE', 'RETURN')),
  sign smallint not null check (sign in (1, -1)),

  -- Measures
  quantity numeric not null,
  unit_price numeric not null,
  gross_amount numeric not null,
  discount_amount numeric not null default 0,
  net_amount numeric not null,

  -- Timestamps
  ingested_at timestamptz not null,
  canonical_loaded_at timestamptz not null default now(),

  -- Idempotency at canonical level
  unique (source_system, raw_row_hash)
);

-- Helpful indexes
create index if not exists ix_canonical__invoice_date_gregorian
  on canonical_sales (invoice_date_gregorian);

create index if not exists ix_canonical_sales__customer_id
  on canonical_sales (customer_id);

create index if not exists ix_canonical_sales__product_id
  on canonical_sales (product_id);

create index if not exists ix_canonical_sales__salesperson_id
  on canonical_sales (salesperson_id);
