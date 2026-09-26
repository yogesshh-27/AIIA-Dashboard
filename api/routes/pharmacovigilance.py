"""Pharmacovigilance & Safety Monitoring routes."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional

from . import db_service

router = APIRouter()


class AdverseEventReport(BaseModel, extra="allow"):
    """Flexible model for AE reporting — accepts any fields from the frontend."""
    pass


@router.get("/ayur/pv/summary")
async def get_ayur_pv_summary():
    return db_service.get_ayur_pv_summary()


@router.get("/ayur/pv/events")
async def get_ayur_adverse_events(
    trial_id: str = "", severity: str = "", status: str = "", search: str = ""
):
    return db_service.get_ayur_adverse_events(
        trial_id=trial_id, severity=severity, status=status, search=search
    )


@router.get("/ayur/pv/signals")
async def get_ayur_safety_signals():
    return db_service.get_ayur_safety_signals()


@router.post("/ayur/pv/report")
async def report_adverse_event(body: AdverseEventReport):
    return db_service.report_ayur_adverse_event(body.model_dump())


# Legacy PV routes
@router.get("/pv/overview")
async def get_pv_overview():
    return db_service.get_pv_overview()


@router.get("/pv/adverse-events")
async def get_pv_adverse_events(
    search: str = "", severity: str = "", serious_only: bool = False,
    status: str = "", page: int = 1, limit: int = 20,
):
    return db_service.get_pv_adverse_events(
        search=search, severity=severity, serious_only=serious_only,
        status=status, page=page, limit=limit,
    )


@router.get("/pv/signals")
async def get_pv_safety_signals(
    search: str = "", severity: str = "", page: int = 1, limit: int = 20,
):
    return db_service.get_pv_safety_signals(
        search=search, severity=severity, page=page, limit=limit,
    )


@router.get("/pv/reporting")
async def get_pv_reporting_deadlines(
    search: str = "", status: str = "", page: int = 1, limit: int = 20,
):
    return db_service.get_pv_reporting_deadlines(
        search=search, status=status, page=page, limit=limit,
    )
