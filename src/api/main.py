from fastapi import FastAPI
from src.api.routers import (
    health, 
    kpi_sales,
    kpi_customers,
    kpi_returns,
)

app = FastAPI(
    title="Sales Insight Engine API",
    version="1.0.0",
)

app.include_router(health.router, prefix="/health")
app.include_router(kpi_sales.router, prefix="/kpi")
app.include_router(kpi_customers.router, prefix="/kpi")
app.include_router(kpi_returns.router, prefix="/kpi")