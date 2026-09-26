"""Dashboard & Analytics routes."""

from fastapi import APIRouter

from . import db_service

router = APIRouter()


@router.get("/ayur/dashboard/stats")
async def ayur_dashboard_stats():
    return db_service.get_ayur_dashboard_stats()


@router.get("/dashboard/portfolio")
async def dashboard_portfolio():
    return db_service.get_dashboard_portfolio()


@router.get("/stats")
async def get_kpis():
    return db_service.get_kpis()


@router.get("/analytics")
async def get_analytics(scope: str = "aiia"):
    return db_service.get_analytics_deep_dive(scope=scope)


@router.get("/app/stats")
async def app_db_stats():
    return db_service.get_app_db_stats()
