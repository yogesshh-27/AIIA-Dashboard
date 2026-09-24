"""Normalization module for CTRI trial records."""

import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from dateutil import parser as date_parser

logger = logging.getLogger("ctri_extractor.normalizer")

STATE_MAP = {
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "west bengal": "West Bengal",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "chandigarh": "Chandigarh",
    "jammu and kashmir": "Jammu and Kashmir",
    "jammu & kashmir": "Jammu and Kashmir",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "ladakh": "Ladakh"
}

STATUS_RULES = [
    ("not yet recruiting", "NOT_YET_RECRUITING"),
    ("closed to recruitment & follow up complete", "COMPLETED"),
    ("closed to recruitment of participants", "CLOSED_TO_RECRUITMENT"),
    ("closed to recruitment", "CLOSED_TO_RECRUITMENT"),
    ("currently recruiting", "RECRUITING"),
    ("open to recruitment of participants", "RECRUITING"),
    ("open to recruitment", "RECRUITING"),
    ("recruiting", "RECRUITING"),
    ("completed", "COMPLETED"),
    ("study completed", "COMPLETED"),
    ("suspended", "SUSPENDED"),
    ("temporarily halted", "SUSPENDED"),
    ("other (terminated)", "TERMINATED"),
    ("terminated", "TERMINATED"),
    ("withdrawn", "WITHDRAWN"),
    ("enrolling by invitation", "ENROLLING_BY_INVITATION"),
    ("active, not recruiting", "ACTIVE_NOT_RECRUITING"),
    ("pending", "PENDING")
]

def clean_whitespace(val: Optional[str]) -> Optional[str]:
    """Clean redundant spaces and newlines."""
    if not val or not str(val).strip():
        return None
    s = str(val).strip()
    if s.upper() in ("NIL", "NONE", "NULL", "NA", "N/A", "CHARACTER(0)"):
        return None
    cleaned = re.sub(r'[\r\n\t]+', ' ', s)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned or None

def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Normalize date strings to YYYY-MM-DD, YYYY-MM, YYYY, or None."""
    if not date_str or not str(date_str).strip():
        return None
    s = str(date_str).strip()
    if s.upper() in ("NIL", "NONE", "NULL", "NA", "N/A", "NO DATE SPECIFIED", "//", "-"):
        return None

    # Common format in CTRI: DD/MM/YYYY
    m1 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m1:
        try:
            d, m, y = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format: YYYY-MM-DD
    m2 = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m2:
        try:
            y, m, d = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format: DD-MM-YYYY
    m3 = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s)
    if m3:
        try:
            d, m, y = int(m3.group(1)), int(m3.group(2)), int(m3.group(3))
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format: MM/YYYY or MM-YYYY
    m4 = re.match(r"^(\d{1,2})[/-](\d{4})$", s)
    if m4:
        m, y = int(m4.group(1)), int(m4.group(2))
        if 1 <= m <= 12:
            return f"{y:04d}-{m:02d}"

    # Format: YYYY
    m5 = re.match(r"^(\d{4})$", s)
    if m5:
        return m5.group(1)

    # General parser fallback
    try:
        dt = date_parser.parse(s, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def normalize_status(status_str: Optional[str]) -> Optional[str]:
    """Normalize recruitment status values while preserving original."""
    if not status_str or not str(status_str).strip():
        return None
    cleaned = str(status_str).strip().lower()
    for raw_pattern, norm_val in STATUS_RULES:
        if raw_pattern in cleaned:
            return norm_val
    return re.sub(r'[^A-Z0-9_]', '_', cleaned.upper())

def normalize_state(state_str: Optional[str]) -> Optional[str]:
    """Normalize Indian state name."""
    if not state_str or not str(state_str).strip():
        return None
    s = str(state_str).strip().lower()
    for key, val in STATE_MAP.items():
        if key in s:
            return val
    return state_str.strip().title()

def normalize_phase(phase_str: Optional[str]) -> Optional[str]:
    """Normalize trial phase string."""
    if not phase_str:
        return None
    p = phase_str.strip().lower()
    if "not applicable" in p:
        return "Not Applicable"
    if re.search(r'\bphase\s*(?:1|i)\s*/\s*phase\s*(?:2|ii)\b', p) or "phase i/ii" in p:
        return "Phase 1 / Phase 2"
    if re.search(r'\bphase\s*(?:2|ii)\s*/\s*phase\s*(?:3|iii)\b', p) or "phase ii/iii" in p:
        return "Phase 2 / Phase 3"
    if re.search(r'\bphase\s*(?:4|iv)\b', p):
        return "Phase 4"
    if re.search(r'\bphase\s*(?:3|iii)\b', p):
        return "Phase 3"
    if re.search(r'\bphase\s*(?:2|ii)\b', p):
        return "Phase 2"
    if re.search(r'\bphase\s*(?:1|i)\b', p):
        return "Phase 1"
    return clean_whitespace(phase_str)

def compute_ayurveda_relevance(record: Dict[str, Any]) -> Tuple[int, str, str]:
    """Calculate ayurveda_relevance_score, reason, and trial_category."""
    score = 0
    reasons = []

    title = (record.get("public_title") or "").lower()
    sc_title = (record.get("scientific_title") or "").lower()
    interv_name = (record.get("intervention_name") or "").lower()
    interv_desc = (record.get("intervention_description") or "").lower()
    summary = (record.get("brief_summary") or "").lower()
    sponsor = (record.get("primary_sponsor") or "").lower()
    comparator = (record.get("comparator") or "").lower()
    full_text = f"{title} {sc_title} {interv_name} {interv_desc} {summary} {sponsor} {comparator}"

    if "ayurved" in title:
        score += 3
        reasons.append("+3 Ayurveda in public title")

    if "ayurved" in interv_name:
        score += 2
        reasons.append("+2 Ayurveda/Ayurvedic in intervention name")

    if "ayush" in full_text:
        score += 2
        reasons.append("+2 AYUSH explicitly mentioned")

    if "ayurved" in summary:
        score += 1
        reasons.append("+1 Ayurveda in summary")

    if "ayurved" in interv_desc:
        score += 1
        reasons.append("+1 Ayurveda in intervention description")

    reason_str = "; ".join(reasons) if reasons else "No explicit Ayurveda/AYUSH keywords found"

    has_ayurveda = "ayurved" in full_text
    has_ayush = any(term in full_text for term in ("ayush", "yoga", "unani", "siddha", "homeopath"))
    has_conventional = any(term in comparator or term in interv_name for term in ("allopath", "conventional", "placebo", "standard care", "metformin", "atorvastatin"))
    
    if has_ayurveda and has_conventional:
        category = "INTEGRATIVE"
    elif has_ayurveda:
        category = "AYURVEDA"
    elif has_ayush:
        category = "AYUSH"
    elif "integrat" in full_text:
        category = "INTEGRATIVE"
    else:
        category = "OTHER"

    return score, reason_str, category

def normalize_trial_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize all fields of an extracted trial record."""
    norm = dict(raw)

    for k, v in norm.items():
        if isinstance(v, str):
            norm[k] = clean_whitespace(v)

    norm["raw_recruitment_status"] = raw.get("raw_recruitment_status") or raw.get("recruitment_status")
    norm["date_first_enrolment"] = normalize_date(raw.get("date_first_enrolment"))
    norm["actual_completion_date"] = normalize_date(raw.get("actual_completion_date"))
    norm["recruitment_status"] = normalize_status(norm["raw_recruitment_status"])

    norm["state"] = normalize_state(raw.get("state"))
    norm["district"] = clean_whitespace(raw.get("district"))
    norm["city"] = clean_whitespace(raw.get("city"))
    norm["country"] = clean_whitespace(raw.get("country")) or "India"

    norm["trial_phase"] = normalize_phase(raw.get("trial_phase"))
    norm["study_type"] = clean_whitespace(raw.get("study_type"))
    norm["study_design"] = clean_whitespace(raw.get("study_design"))

    sz = raw.get("target_sample_size")
    if sz:
        m_sz = re.search(r'(\d+)', str(sz))
        norm["target_sample_size"] = m_sz.group(1) if m_sz else None
    else:
        norm["target_sample_size"] = None

    score, reason, cat = compute_ayurveda_relevance(norm)
    norm["ayurveda_relevance_score"] = score
    norm["ayurveda_relevance_reason"] = reason
    norm["trial_category"] = cat

    return norm
