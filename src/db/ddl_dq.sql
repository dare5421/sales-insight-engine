create table if not exists dq_issues(
    dq_id bigserial primary key,

    -- linage info
    source_system text not null,
    source_file text,
    load_batch_id text,

    -- where did it happen
    table_stage text not null
        check (table_stage in ('RAW', 'CANONICAL') ),

    -- which record
    record_business_key text,

    -- what went wrong
    issue_code text not null,
    issue_severity text not null
        check (issue_severity in ('ERROR', 'WARNING') ),

    issue_description text,
    column_name text,
    raw_value text,

    detected_at timestamptz not null default now()
);

create index if not exists ix_dq_issues__table_stage
    on dq_issues(table_stage);
create index if not exists ix_dq_issues__issue_code
    on dq_issues(issue_code);
create index if not exists ix_dq_issues__issue_severity
    on dq_issues(issue_severity);