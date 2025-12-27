-- 001_lock_dq_issue_code.sql
-- purpose: lock Data Quality issue_code & severity contract

-- 1. evforce issue_severity values
alter table dq_issues
drop constraint if exists dq_issues_issue_severity_check;

alter table dq_issues
add constraint dq_issues_issue_severity_check
check (
    issue_severity in (
        'ERROR',
        'WARNING'
    )
);

-- 2. enforce issue_code values
alter table dq_issues
drop constraint if exists dq_issues_issue_code_check;

alter table dq_issues
add constraint dq_issues_issue_code_check
check (
    issue_code in (
        'MISSING_INVOICE_ID',
        'INVALID_NUMERIC',
        'INVALID_DATE',
        'FALLBACK_EVENT_DATE',
        'TEST_DQ'
    )
);
