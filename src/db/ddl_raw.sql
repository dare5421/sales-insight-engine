create table if not exists raw_karamad_sales (
  raw_id bigserial primary key,
  source_system text not null default 'karamad',
  source_file text not null,
  load_batch_id text not null,
  ingested_at timestamptz not null default now(),
  row_hash text not null,

  c01 text, c02 text, c03 text, c04 text, c05 text, c06 text, c07 text, c08 text, c09 text, c10 text,
  c11 text, c12 text, c13 text, c14 text, c15 text, c16 text, c17 text, c18 text, c19 text, c20 text,
  c21 text, c22 text, c23 text, c24 text, c25 text, c26 text, c27 text, c28 text, c29 text, c30 text,
  c31 text, c32 text, c33 text, c34 text, c35 text, c36 text, c37 text, c38 text, c39 text, c40 text,
  c41 text, c42 text, c43 text, c44 text, c45 text, c46 text, c47 text, c48 text, c49 text, c50 text,
  c51 text, c52 text, c53 text, c54 text, c55 text, c56 text, c57 text, c58 text, c59 text, c60 text,
  c61 text
);

create unique index if not exists ux_raw_karamad_sales__source_system_row_hash
  on raw_karamad_sales (source_system, row_hash);

create index if not exists ix_raw_karamad_sales__load_batch_id_ingested_at
  on raw_karamad_sales (load_batch_id, ingested_at);


