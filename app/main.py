from fastapi import FastAPI
from app.core.logging_config import setup_logging
from app.routers import convert, generate, calculate

setup_logging()

app = FastAPI(title="Geospatial API Service")

app.include_router(convert, prefix="/convert", tags=["convert"])
app.include_router(generate, prefix="/generate", tags=["generate"])
app.include_router(calculate, prefix="/calculate", tags=["calculate"])
