"""Trial Management routes."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import urllib.parse

from . import db_service

router = APIRouter()


class CreateTrialRequest(BaseModel, extra="allow"):
    """Flexible model for trial creation — accepts any fields from the frontend."""
    pass


@router.get("/ayur/trials")
async def get_ayur_trials(
    status: str = "", condition: str = "", location: str = "", search: str = ""
):
    return db_service.get_ayur_trials(
        status=status, condition=condition, location=location, search=search
    )


@router.get("/ayur/trials/{trial_id:path}")
async def get_ayur_trial_detail(trial_id: str):
    return db_service.get_ayur_trial_detail(urllib.parse.unquote(trial_id))


@router.post("/ayur/trials/create")
async def create_ayur_trial(body: CreateTrialRequest):
    return db_service.create_ayur_trial(body.model_dump())


@router.get("/trials")
async def get_trials(
    scope: str = "aiia", search: str = "", status: str = "",
    phase: str = "", trial_type: str = "", sponsor: str = "",
    thesis: str = "", year: str = "", date_from: str = "", date_to: str = "",
    sort_by: str = "registered_on", sort_dir: str = "desc",
    page: int = 1, limit: int = 15,
):
    return db_service.get_trials(
        scope=scope, search=search, status=status,
        phase=phase, trial_type=trial_type, sponsor=sponsor,
        thesis=thesis, year=year, date_from=date_from, date_to=date_to,
        sort_by=sort_by, sort_dir=sort_dir, page=page, limit=limit,
    )


@router.get("/trials/{trial_id}")
async def get_trial_detail(trial_id: int):
    trial_data = db_service.get_trial_detail(trial_id)
    if trial_data:
        return trial_data
    return JSONResponse({"error": "Trial not found"}, status_code=404)


@router.get("/ayur/sites")
async def get_ayur_sites(city: str = ""):
    if city:
        return db_service.get_ayur_sites(city=city)
    return db_service.get_ayur_sites()


@router.get("/ayur/sites/{city}")
async def get_ayur_site_detail(city: str):
    return db_service.get_ayur_sites(city=urllib.parse.unquote(city))


@router.get("/app/trials")
async def get_app_trials(
    scope: str = "aiia", search: str = "", status: str = "",
    page: int = 1, limit: int = 15,
):
    return db_service.get_app_trials(
        scope=scope, search=search, status=status, page=page, limit=limit
    )
