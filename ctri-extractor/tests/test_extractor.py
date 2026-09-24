"""Offline unit tests for CTRI Extractor components using local fixtures."""

import os
import sys
import pytest

# Ensure ctri-extractor is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.deduplicator import CTRIDeduplicator
from src.fetcher import CTRIFetcher
from src.normalizer import (
    normalize_date,
    normalize_status,
    normalize_state,
    normalize_phase,
    compute_ayurveda_relevance,
    normalize_trial_record
)
from src.parser import CTRIHTMLParser
from src.pdf_parser import CTRIPDFParser
from src.validator import validate_trial_record

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

@pytest.fixture
def sample_ayurveda_html():
    with open(os.path.join(FIXTURES_DIR, "sample_ayurveda_trial.html"), "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def sample_blocked_html():
    with open(os.path.join(FIXTURES_DIR, "sample_blocked_captcha.html"), "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def sample_minimal_html():
    with open(os.path.join(FIXTURES_DIR, "sample_minimal_trial.html"), "r", encoding="utf-8") as f:
        return f.read()

def test_ctri_number_extraction(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    res = parser.parse(sample_ayurveda_html, "http://test/trial", "123")
    assert res["ctri_number"] == "CTRI/2021/05/033838"
    assert res["trial_id"] == "123"
    assert res["ctri_registration_status"] == "Registered"

def test_title_extraction(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    res = parser.parse(sample_ayurveda_html, "http://test/trial")
    assert "Ayurvedic Formulation in Patients with Mild Osteoarthritis" in res["public_title"]
    assert "A prospective randomized double-blind" in res["scientific_title"]

def test_condition_extraction(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    res = parser.parse(sample_ayurveda_html, "http://test/trial")
    assert "Osteoarthritis of Knee" in res["condition"]
    assert res["health_condition"] == res["condition"]

def test_intervention_extraction(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    res = parser.parse(sample_ayurveda_html, "http://test/trial")
    assert "Ayurvedic Polyherbal Formulation Tablet" in res["intervention_name"]
    assert "500 mg twice daily" in res["intervention_description"]
    assert "Placebo Tablet" in res["comparator"]

def test_investigator_extraction(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    res = parser.parse(sample_ayurveda_html, "http://test/trial")
    assert res["principal_investigator"] == "Dr. Ramesh Sharma"
    assert "All India Institute of Ayurveda" in res["investigator_affiliation"]
    assert "011-29995555" in res["investigator_contact"]

def test_site_and_location_extraction(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    res = parser.parse(sample_ayurveda_html, "http://test/trial")
    assert "All India Institute of Ayurveda Hospital" in res["site_name"]
    assert "Sarita Vihar" in res["site_address"]
    assert res["city"] == "Delhi"
    assert res["state"] == "Delhi"
    assert res["country"] == "India"

def test_date_normalization():
    assert normalize_date("12/05/2021") == "2021-05-12"
    assert normalize_date("2021-05-12") == "2021-05-12"
    assert normalize_date("15-08-2021") == "2021-08-15"
    assert normalize_date("05/2021") == "2021-05"
    assert normalize_date("2021") == "2021"
    assert normalize_date("No Date Specified") is None
    assert normalize_date("//") is None
    assert normalize_date(None) is None

def test_status_normalization():
    assert normalize_status("Currently Recruiting") == "RECRUITING"
    assert normalize_status("Recruiting") == "RECRUITING"
    assert normalize_status("Completed") == "COMPLETED"
    assert normalize_status("Not Yet Recruiting") == "NOT_YET_RECRUITING"
    assert normalize_status("Other (Terminated)") == "TERMINATED"
    assert normalize_status(None) is None

def test_state_and_phase_normalization():
    assert normalize_state("MAHARASHTRA") == "Maharashtra"
    assert normalize_state("NEW DELHI") == "Delhi"
    assert normalize_state("kerala") == "Kerala"
    assert normalize_phase("Phase 2 / Phase 3") == "Phase 2 / Phase 3"
    assert normalize_phase("Phase II") == "Phase 2"

def test_ayurveda_relevance_scoring(sample_ayurveda_html):
    parser = CTRIHTMLParser()
    raw = parser.parse(sample_ayurveda_html, "http://test/trial")
    norm = normalize_trial_record(raw)
    
    # Title has "Ayurvedic" (+3), intervention has "Ayurvedic" (+2), AYUSH sponsor (+2), summary (+1)
    assert norm["ayurveda_relevance_score"] >= 6
    assert "+3 Ayurveda in public title" in norm["ayurveda_relevance_reason"]
    assert norm["trial_category"] in ("AYURVEDA", "INTEGRATIVE")

def test_human_verification_detection(sample_blocked_html):
    fetcher = CTRIFetcher(raw_html_dir="tmp/html", raw_pdf_dir="tmp/pdf", progress_path="tmp/progress.json")
    is_blocked, reason = fetcher.check_access_blocked(sample_blocked_html)
    assert is_blocked is True
    assert "CAPTCHA" in reason or "Security code" in reason

def test_deduplication():
    dedup = CTRIDeduplicator()
    rec1 = {
        "ctri_number": "CTRI/2021/01/000001",
        "public_title": "Trial for Ayurveda Treatment",
        "principal_investigator": "Dr. Sharma",
        "date_first_enrolment": "2021-01-01"
    }
    rec2_same_ctri = {
        "ctri_number": "CTRI/2021/01/000001",
        "public_title": "Different Title",
        "principal_investigator": "Dr. Different",
        "date_first_enrolment": "2021-05-01"
    }
    rec3_secondary_dup = {
        "ctri_number": "CTRI/2021/01/000999",
        "public_title": "Trial for Ayurveda Treatment",
        "principal_investigator": "Dr. Sharma",
        "date_first_enrolment": "2021-01-01"
    }
    rec4_distinct = {
        "ctri_number": "CTRI/2021/01/000002",
        "public_title": "Another Study",
        "principal_investigator": "Dr. Verma",
        "date_first_enrolment": "2021-02-01"
    }

    records = [rec1, rec2_same_ctri, rec3_secondary_dup, rec4_distinct]
    unique, dup_count, dups = dedup.deduplicate(records)
    assert len(unique) == 2
    assert dup_count == 2
    assert unique[0]["ctri_number"] == "CTRI/2021/01/000001"
    assert unique[1]["ctri_number"] == "CTRI/2021/01/000002"

def test_missing_value_handling_and_validation(sample_minimal_html):
    parser = CTRIHTMLParser()
    raw = parser.parse(sample_minimal_html, "http://test/minimal")
    norm = normalize_trial_record(raw)
    
    assert norm["ctri_number"] == "CTRI/2023/01/048899"
    assert norm["scientific_title"] is None
    assert norm["intervention_name"] is None
    assert norm["state"] is None
    
    val_status, errors = validate_trial_record(norm, seen_ctri_numbers=set())
    # Should not be INVALID since ctri_number, source_url, public_title are present
    assert val_status in ("VALID", "WARNING")

def test_pdf_fallback_merge():
    html_record = {
        "ctri_number": "CTRI/2021/01/000100",
        "public_title": "HTML Title",
        "condition": None,
        "principal_investigator": None
    }
    pdf_record = {
        "ctri_number": "CTRI/2021/01/000100",
        "public_title": "PDF Title",  # Should NOT overwrite HTML Title
        "condition": "Knee Osteoarthritis",
        "principal_investigator": "Dr. Gupta"
    }
    merged = CTRIPDFParser.merge_with_html(html_record, pdf_record)
    assert merged["public_title"] == "HTML Title"  # HTML priority maintained
    assert merged["condition"] == "Knee Osteoarthritis"  # Missing filled from PDF
    assert merged["principal_investigator"] == "Dr. Gupta"
