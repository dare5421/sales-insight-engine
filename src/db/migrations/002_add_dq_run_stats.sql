-- 002_add_dq_run_stats.sql
-- purpose: store per-run Data Quality summary

create table if not EXISTS dq_run_stats(
    
    run_id bigserial primary key,
    
    -- lineage info
    source_system text not null,
    source_file text,
    load_batch_id text not null,

    -- summary stats
    processed_count integer not null,
    inserted_count integer not null,
    skipped_count integer not null,

    -- dq stats
    error_count integer not null,
    warning_count integer not null,

    -- timestamps
    started_at timestamptz not null,
    finished_at timestamptz not null
);

create index if not exists ix_dq_run_stats__load_batch_id
    on dq_run_stats(load_batch_id);

create index if not exists ix_dq_run_stats__finished_at
    on dq_run_stats(finished_at);