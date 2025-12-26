from typing import Optional 

def log_dq_issue(
    cur,
    *,
    source_system: str,
    source_file: Optional[str],
    load_batch_id: Optional[str],
    table_stage: str,
    issue_code: str,
    issue_severity: str,
    record_business_key: Optional[str] = None,
    column_name: Optional[str] = None,
    raw_value: Optional[str] = None,
    issue_description: Optional[str] = None,
):
    """ 
    Insert a datat quality issue into dq_issue table.
    
    This function MUST NOT conatain any business logic.
    It only records what went wrong.
    """

    cur.execute(
        """
        insert into dq_issues (
            source_system,
            source_file,
            load_batch_id,
            table_stage,
            record_business_key,
            issue_code,
            issue_severity,
            issue_description,
            column_name,
            raw_value
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            source_system,
            source_file,
            load_batch_id,
            table_stage,
            record_business_key,
            issue_code,
            issue_severity,
            issue_description,
            column_name,
            raw_value,
        ),
    )
