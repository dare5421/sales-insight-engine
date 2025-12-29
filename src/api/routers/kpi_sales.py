from fastapi import APIRouter
from src.api.db import get_conn

router = APIRouter()

@router.get("/net-sales-daily")
def net_sales_daily(limit: int = 30):
    sql = """
        SELECT *
        from kpi_net_sales_daily
        ORDER BY day DESC
        LIMIT %s;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()