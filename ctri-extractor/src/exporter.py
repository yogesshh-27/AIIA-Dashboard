"""Exporter module for generating CTRI dataset deliverables, logs, and quality reports."""

import csv
import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger("ctri_extractor.exporter")

FIELDNAMES = [
    "trial_id",
    "ctri_number",
    "public_title",
    "scientific_title",
    "study_type",
    "study_design",
    "trial_phase",
    "study_category",
    "condition",
    "health_condition",
    "disease_category",
    "intervention_name",
    "intervention_type",
    "intervention_description",
    "comparator",
    "principal_investigator",
    "investigator_affiliation",
    "investigator_contact",
    "primary_sponsor",
    "secondary_sponsor",
    "sponsor_type",
    "country",
    "state",
    "district",
    "city",
    "site_name",
    "site_address",
    "ethics_committee",
    "ethics_approval_status",
    "dcgi_approval_status",
    "regulatory_status",
    "ctri_registration_status",
    "recruitment_status",
    "raw_recruitment_status",
    "date_first_enrolment",
    "estimated_duration",
    "target_sample_size",
    "final_enrolment",
    "actual_completion_date",
    "primary_outcome",
    "secondary_outcome",
    "inclusion_criteria",
    "exclusion_criteria",
    "brief_summary",
    "study_description",
    "trial_category",
    "ayurveda_relevance_score",
    "ayurveda_relevance_reason",
    "source_url",
    "source_pdf_url",
    "extraction_timestamp",
    "parser_version",
    "record_hash",
    "validation_status",
    "validation_errors"
]

def export_csv(records: List[Dict[str, Any]], filepath: str = "output/ctri_trials.csv"):
    """Export dataset to UTF-8 CSV matching Section 24 schema."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            # Map None/empty to empty string or clean string
            row = {}
            for k in FIELDNAMES:
                val = r.get(k)
                row[k] = "" if val is None else str(val)
            writer.writerow(row)
    logger.info(f"Saved {len(records)} records to CSV: {filepath}")

def export_json(records: List[Dict[str, Any]], filepath: str = "output/ctri_trials.json"):
    """Export dataset to formatted UTF-8 JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(records)} records to JSON: {filepath}")

def log_extraction_event(
    filepath: str,
    timestamp: str,
    ctri_number: str,
    source_url: str,
    status: str,
    http_status: int,
    fields_extracted: int,
    retry_count: int,
    error: str,
    parser_version: str
):
    """Log an extraction event to output/extraction_log.csv."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "ctri_number", "source_url", "status", "http_status",
                "fields_extracted", "retry_count", "error", "parser_version"
            ])
        writer.writerow([
            timestamp, ctri_number, source_url, status, http_status,
            fields_extracted, retry_count, error or "", parser_version
        ])

def generate_quality_report(
    records: List[Dict[str, Any]],
    total_discovered: int,
    duplicates_removed: int,
    access_blocked_count: int,
    failed_count: int,
    manual_review_count: int,
    output_path: str = "output/quality_report.txt"
) -> str:
    """Generate quality report detailing completeness and pipeline statistics."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    total_unique = len(records)
    successful = len(records)

    # Completeness calculation
    fields_to_measure = [
        ("CTRI Number", "ctri_number"),
        ("Public Title", "public_title"),
        ("Condition", "condition"),
        ("Intervention", "intervention_name"),
        ("Investigator", "principal_investigator"),
        ("Location", "site_name"),
        ("Recruitment Status", "recruitment_status"),
        ("Sample Size", "target_sample_size"),
        ("Ethics Status", "ethics_approval_status"),
        ("Regulatory Status", "regulatory_status")
    ]

    completeness_lines = []
    for label, key in fields_to_measure:
        if total_unique > 0:
            count = sum(1 for r in records if r.get(key) not in (None, "", "NULL", "None"))
            pct = (count / total_unique) * 100
        else:
            pct = 0.0
        completeness_lines.append(f"{label}: {pct:.1f}%")

    report = f"""============================================================
AYURCTMS - CTRI CLINICAL TRIAL DATA EXTRACTOR QUALITY REPORT
============================================================

Total discovered: {total_discovered}
Total unique trials: {total_unique}
Duplicates removed: {duplicates_removed}

Pipeline Results:
Successfully extracted: {successful}
Access blocked: {access_blocked_count}
Manual review: {manual_review_count}
Failed: {failed_count}

------------------------------------------------------------
Field Completeness:
------------------------------------------------------------
""" + "\n".join(completeness_lines) + f"""

------------------------------------------------------------
Validation Breakdown:
------------------------------------------------------------
VALID: {sum(1 for r in records if r.get('validation_status') == 'VALID')}
WARNING: {sum(1 for r in records if r.get('validation_status') == 'WARNING')}
INVALID: {sum(1 for r in records if r.get('validation_status') == 'INVALID')}

Ayurveda / AYUSH Categories:
AYURVEDA: {sum(1 for r in records if r.get('trial_category') == 'AYURVEDA')}
AYUSH: {sum(1 for r in records if r.get('trial_category') == 'AYUSH')}
INTEGRATIVE: {sum(1 for r in records if r.get('trial_category') == 'INTEGRATIVE')}
OTHER: {sum(1 for r in records if r.get('trial_category') == 'OTHER')}

Deliverables Generated:
- output/ctri_trials.csv (Primary Dataset)
- output/ctri_trials.json
- output/extraction_log.csv
- output/manual_review.csv
============================================================
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    logger.info(f"Generated quality report at {output_path}")
    return report
