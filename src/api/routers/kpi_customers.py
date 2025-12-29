from fastapi import APIRouter
from src.api.db import get_conn

router = APIRouter()
@router.get("/top-customers-month")
def top_customers_month(limit: int = 50):
    sql = """
        SELECT *
        from kpi_top_customers_month
        ORDER BY month DESC, net_sales_amount DESC
        LIMIT %s;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()