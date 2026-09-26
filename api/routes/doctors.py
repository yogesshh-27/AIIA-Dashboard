"""Doctor Directory routes."""

from fastapi import APIRouter
import urllib.parse

from . import db_service

router = APIRouter()


@router.get("/ayur/doctors")
async def get_ayur_doctors(
    site: str = "", specialization: str = "", status: str = "", search: str = ""
):
    return db_service.get_ayur_doctors(
        site=site, specialization=specialization, status=status, search=search
    )


@router.get("/ayur/doctors/{doctor_id:path}")
async def get_ayur_doctor_detail(doctor_id: str):
    return db_service.get_ayur_doctor_detail(urllib.parse.unquote(doctor_id))
