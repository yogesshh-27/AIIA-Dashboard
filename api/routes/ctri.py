"""CTRI Registry & Extractor routes."""

import os
import json
import urllib.parse

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from . import db_service

router = APIRouter()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@router.get("/ctri-extractor/trials")
@router.get("/ctri/dataset")
async def get_ctri_extractor_trials(search: str = "", limit: int = 100):
    json_candidates = [
        os.path.join(ROOT_DIR, "output", "ctri_trials.json"),
        os.path.join(ROOT_DIR, "ctri-extractor", "output", "ctri_trials.json"),
        os.path.join(ROOT_DIR, "dist", "output", "ctri_trials.json"),
    ]
    trials = []
    for j_path in json_candidates:
        if os.path.exists(j_path):
            try:
                with open(j_path, "r", encoding="utf-8") as f:
                    trials = json.load(f)
                if trials:
                    break
            except Exception:
                pass
        # Fix CTRI source URLs
        for t in trials:
            c_num = t.get("ctri_number", "")
            s_url = t.get("source_url", "")
            if s_url and "showallp.php" in s_url and c_num:
                if "userName=" in s_url:
                    base = s_url.split("userName=")[0]
                    t["source_url"] = f"{base}userName={urllib.parse.quote(c_num)}"
                else:
                    sep = "&" if "?" in s_url else "?"
                    t["source_url"] = f"{s_url}{sep}userName={urllib.parse.quote(c_num)}"
    else:
        trials = []

    if search:
        search_lower = search.lower()
        trials = [
            t for t in trials
            if search_lower in (t.get("public_title", "") or "").lower()
            or search_lower in (t.get("ctri_number", "") or "").lower()
            or search_lower in (t.get("condition", "") or "").lower()
            or search_lower in (t.get("intervention_name", "") or "").lower()
            or search_lower in (t.get("principal_investigator", "") or "").lower()
        ]

    return {"total": len(trials), "trials": trials[:limit]}


@router.get("/ctri-extractor/quality-report")
async def get_ctri_quality_report():
    report_file = os.path.join(ROOT_DIR, "ctri-extractor", "output", "quality_report.txt")
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "Quality report not found."
    return {"report": content}
