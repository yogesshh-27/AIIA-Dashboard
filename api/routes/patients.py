"""Patient Management routes."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import urllib.parse

from . import db_service

router = APIRouter()


class PatientMatchRequest(BaseModel):
    condition: str = ""
    accessible_locations: List[str] = []
    distance_pref: str = ""
    age: Optional[int] = None
    gender: Optional[str] = None


@router.get("/ayur/patients")
async def get_ayur_patients(
    condition: str = "", site: str = "", status: str = "", search: str = ""
):
    return db_service.get_ayur_patients(
        condition=condition, site=site, status=status, search=search
    )


@router.get("/ayur/patients/{patient_id:path}")
async def get_ayur_patient_detail(patient_id: str):
    return db_service.get_ayur_patient_detail(urllib.parse.unquote(patient_id))


@router.post("/ayur/patient/match")
async def match_patient_trial(body: PatientMatchRequest):
    return db_service.match_patient_trials(
        condition=body.condition,
        accessible_locations=body.accessible_locations,
        distance_pref=body.distance_pref,
        age=body.age,
        gender=body.gender,
    )
