"""Validation module for CTRI trial records."""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger("ctri_extractor.validator")

VALID_STATUSES = {
    "RECRUITING", "COMPLETED", "NOT_YET_RECRUITING", "CLOSED_TO_RECRUITMENT",
    "SUSPENDED", "TERMINATED", "WITHDRAWN", "ENROLLING_BY_INVITATION",
    "ACTIVE_NOT_RECRUITING", "PENDING"
}

def validate_trial_record(record: Dict[str, Any], seen_ctri_numbers: Set[str]) -> Tuple[str, str]:
    """Validate a normalized trial record.
    
    Returns:
        (validation_status, validation_errors)
        validation_status: VALID, WARNING, or INVALID
        validation_errors: semicolon-delimited string of error/warning messages
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Required fields
    ctri_number = record.get("ctri_number")
    source_url = record.get("source_url")
    public_title = record.get("public_title")

    if not ctri_number or not str(ctri_number).strip() or str(ctri_number).strip().upper() in ("NONE", "NULL"):
        errors.append("Missing required field: ctri_number")
    else:
        # Check CTRI format: CTRI/YYYY/MM/XXXXXX or CTRI/YYYY/MMM/XXXXXX
        if not re.match(r"^CTRI/\d{4}/\d{2,3}/\d+$", str(ctri_number).strip()):
            warnings.append(f"CTRI number '{ctri_number}' does not strictly match CTRI/YYYY/MM/XXXXXX pattern")
        
        # Check for duplicates in the current dataset
        if str(ctri_number).strip() in seen_ctri_numbers:
            errors.append(f"Duplicate CTRI number: {ctri_number}")

    if not source_url or not str(source_url).strip():
        errors.append("Missing required field: source_url")

    if not public_title or not str(public_title).strip() or str(public_title).strip().upper() in ("NONE", "NULL"):
        errors.append("Missing required field: public_title")

    # Optional fields validation
    # Sample Size Numeric
    sample_size = record.get("target_sample_size")
    if sample_size is not None and str(sample_size).strip():
        try:
            val = int(str(sample_size).strip())
            if val <= 0:
                warnings.append(f"Target sample size is non-positive: {val}")
        except ValueError:
            warnings.append(f"Target sample size is not a valid integer: {sample_size}")

    # Date format checks
    date_enrol = record.get("date_first_enrolment")
    if date_enrol and not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", str(date_enrol).strip()):
        warnings.append(f"date_first_enrolment not in valid YYYY-MM-DD format: {date_enrol}")

    comp_date = record.get("actual_completion_date")
    if comp_date and not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", str(comp_date).strip()):
        warnings.append(f"actual_completion_date not in valid YYYY-MM-DD format: {comp_date}")

    # Recruitment status recognized
    rec_status = record.get("recruitment_status")
    if rec_status and rec_status not in VALID_STATUSES:
        warnings.append(f"Unrecognized recruitment status: {rec_status}")

    # Determine validation status
    if errors:
        status = "INVALID"
        all_msgs = errors + warnings
    elif warnings:
        status = "WARNING"
        all_msgs = warnings
    else:
        status = "VALID"
        all_msgs = []

    err_str = "; ".join(all_msgs) if all_msgs else ""
    return status, err_str
