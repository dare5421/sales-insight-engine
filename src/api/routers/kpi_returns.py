from fastapi import APIRouter
from src.api.db import get_conn

router = APIRouter()
@router.get("/return-rate-by-product-month")
def return_rate_by_product_month(limit: int = 50):
    sql = """
        SELECT *
        from kpi_return_rate_by_product_month
        ORDER BY return_rate DESC
        LIMIT %s;
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()