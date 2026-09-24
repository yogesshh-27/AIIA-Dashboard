# AYURCTMS CTRI Clinical Trial Data Extractor

A robust, resilient Python-based clinical trial data extractor specifically developed for the **AYURCTMS** (Ayurveda Clinical Trial Management System) platform. It extracts publicly accessible clinical trial records from the official **Clinical Trials Registry - India (CTRI)** website and produces a clean, standardized, deduplicated dataset focused on Ayurveda and AYUSH research.

---

## Official Sources & Reference

- **CTRI Portal**: [https://ctri.nic.in/](https://ctri.nic.in/)
- **CTRI Advanced Search**: [https://ctri.nic.in/Clinicaltrials/advancesearchmain.php](https://ctri.nic.in/Clinicaltrials/advancesearchmain.php)
- **CTRI Dataset & Description**: [https://www.ctri.nic.in/Clinicaltrials/CTRI_Dataset_and_Description.pdf](https://www.ctri.nic.in/Clinicaltrials/CTRI_Dataset_and_Description.pdf)

---

## Core Objectives & Priorities

1. **Accuracy**: Precise semantic extraction without hallucinating or fabricating information. Missing values remain `NULL`.
2. **Traceability**: Every record stores its exact `source_url`, `extraction_timestamp`, `parser_version`, and SHA-256 `record_hash`.
3. **Data Quality & Validation**: Multi-stage validation categorizing records into `VALID`, `WARNING`, or `INVALID` with transparent error logging.
4. **Deduplication**: Strict primary (`ctri_number`) and secondary composite key (`normalized_title + PI + date_first_enrolment`) deduplication.
5. **Respectful Access (Rule 2 Compliance)**:
   - Configurable polite request delay (default 3 seconds).
   - Exponential backoff retries (3s, 6s, 12s).
   - **Zero CAPTCHA / Bot Bypass**: Never bypasses CAPTCHAs, Cloudflare, or "Verify you are human". If challenged, execution immediately stops for that record and logs `ACCESS_BLOCKED` to `manual_review.csv`.

---

## Project Structure

```
ctri-extractor/
├── README.md
├── requirements.txt
├── config.yaml
│
├── src/
│   ├── __init__.py
│   ├── discovery.py       # Identifies trial records matching target keywords
│   ├── fetcher.py         # Polite, rate-limited HTTP fetcher with CAPTCHA detection
│   ├── parser.py          # Semantic HTML table and field parser
│   ├── pdf_parser.py      # PDF fallback extraction via pdfplumber
│   ├── normalizer.py      # Standardization of dates, statuses, states, Ayurveda relevance
│   ├── validator.py       # Record validation and error detection
│   ├── deduplicator.py    # Primary and secondary deduplication
│   ├── exporter.py        # CSV/JSON generation, logs, and quality reporting
│   └── main.py            # CLI entry point and orchestration pipeline
│
├── data/
│   ├── raw/
│   │   ├── html/          # Unmodified original HTML files (e.g. CTRI_2021_05_033838.html)
│   │   └── pdf/           # Public trial PDFs
│   └── processed/
│       ├── discovered_trials.csv
│       └── progress.json  # Resume state checkpoint
│
├── output/
│   ├── ctri_trials.csv    # Primary AYURCTMS dataset (UTF-8, 55 columns)
│   ├── ctri_trials.json   # JSON formatted records
│   ├── extraction_log.csv # Extraction event log
│   ├── manual_review.csv  # Access blocked or review-needed records
│   └── quality_report.txt # Field completeness and pipeline statistics
│
└── tests/
    ├── __init__.py
    ├── test_extractor.py  # 14 offline unit tests
    └── fixtures/          # Local HTML fixtures (no live CTRI hits in tests)
```

---

## Configuration (`config.yaml`)

```yaml
source:
  base_url: "https://ctri.nic.in/"
  delay_seconds: 3
  timeout_seconds: 30
  max_retries: 3
  user_agent: "AYURCTMS-CTRI-Extractor/1.0"

search:
  keywords:
    - "Ayurveda"
    - "Ayurvedic"
    - "AYUSH"
    - "Ayurvedic medicine"
    - "Ayurvedic intervention"
    - "Ayurvedic formulation"
    - "Ayurvedic therapy"
    - "Ayurveda treatment"
  max_trials: 100

output:
  csv: "output/ctri_trials.csv"
  json: "output/ctri_trials.json"
  extraction_log: "output/extraction_log.csv"
  manual_review: "output/manual_review.csv"
  quality_report: "output/quality_report.txt"

behavior:
  download_pdf: true
  save_raw_html: true
  continue_on_error: true
  manual_review_on_block: true
  resume: true
```

---

## Installation & Setup

Ensure Python 3.11+ is installed.

```bash
cd ctri-extractor
pip install -r requirements.txt
```

---

## Running the Extractor

### 1. Default Extraction (~50–100 trials)
```bash
python -m src.main
```

### 2. Specify Trial Limit
```bash
python -m src.main --max-trials 50
```

### 3. Specify Target Keywords
```bash
python -m src.main --keyword Ayurveda --keyword AYUSH
```

### 4. Force Re-download
```bash
python -m src.main --force-refresh
```

### 5. Custom Config or Database
```bash
python -m src.main --config config.yaml --db-path ../JM_CTRIdb.sqlite
```

---

## Running Offline Unit Tests

The test suite uses local fixtures inside `tests/fixtures/` and **never makes live network requests** to CTRI during test execution:

```bash
pytest tests/test_extractor.py -v
```

---

## Ayurveda Relevance Scoring & Categorization

Each record includes an explicit relevance assessment:
- `ayurveda_relevance_score`:
  - `+3`: Ayurveda in public title
  - `+2`: Ayurveda/Ayurvedic in intervention name
  - `+2`: AYUSH explicitly mentioned
  - `+1`: Ayurveda in summary
  - `+1`: Ayurveda in intervention description
- `ayurveda_relevance_reason`: Explains the point breakdown.
- `trial_category`:
  - `AYURVEDA`: Pure Ayurvedic interventions
  - `AYUSH`: Broader AYUSH disciplines (Yoga, Unani, Siddha, Homeopathy)
  - `INTEGRATIVE`: Co-administered or compared with conventional standard care / allopathy
  - `OTHER`: General trials

---

## Dataset Schema (55 Columns)

| Field | Description |
|---|---|
| `trial_id` | CTRI internal registry identifier |
| `ctri_number` | Official CTRI Number (`CTRI/YYYY/MM/XXXXXX`) |
| `public_title` | Public title of the clinical trial |
| `scientific_title` | Scientific protocol title |
| `study_type` | Type of study (Drug, Interventional, etc.) |
| `study_design` | Study design methodology |
| `trial_phase` | Standardized clinical trial phase |
| `study_category` | Study classification / thesis status |
| `condition` | Medical condition / problem studied |
| `health_condition` | Health condition studied |
| `disease_category` | Categorization of disease |
| `intervention_name` | Name(s) of investigational agent |
| `intervention_type` | Type of intervention |
| `intervention_description` | Posology, dosage, route, duration |
| `comparator` | Control/comparator agent or placebo |
| `principal_investigator` | Name of Principal Investigator |
| `investigator_affiliation` | Institution and department |
| `investigator_contact` | Phone, email, fax |
| `primary_sponsor` | Organization funding/sponsoring |
| `secondary_sponsor` | Secondary funding entities |
| `sponsor_type` | Government, private, pharmaceutical |
| `country` | Country of recruitment |
| `state` | Standardized Indian state |
| `district` | District of trial site |
| `city` | City of trial site |
| `site_name` | Hospital / clinical site name |
| `site_address` | Physical location and address |
| `ethics_committee` | Institutional Ethics Committee |
| `ethics_approval_status` | Status of ethics clearance |
| `dcgi_approval_status` | DCGI / CDSCO regulatory status |
| `regulatory_status` | Regulatory standing |
| `ctri_registration_status` | Registered or Pending |
| `recruitment_status` | Normalized status (RECRUITING, COMPLETED, etc.) |
| `raw_recruitment_status` | Unaltered status from portal |
| `date_first_enrolment` | Normalized date (`YYYY-MM-DD`) |
| `estimated_duration` | Duration in years, months, days |
| `target_sample_size` | Target number of participants |
| `final_enrolment` | Completed enrolment count |
| `actual_completion_date` | Completion date (`YYYY-MM-DD`) |
| `primary_outcome` | Primary endpoint and time points |
| `secondary_outcome` | Secondary endpoints |
| `inclusion_criteria` | Participant inclusion criteria |
| `exclusion_criteria` | Participant exclusion criteria |
| `brief_summary` | Overview of the study |
| `study_description` | Detailed trial description |
| `trial_category` | AYURVEDA, AYUSH, INTEGRATIVE, OTHER |
| `ayurveda_relevance_score` | Numeric score based on explicit criteria |
| `ayurveda_relevance_reason` | Traceable rationale for score |
| `source_url` | Full URL of the public CTRI trial page |
| `source_pdf_url` | Public PDF document URL if available |
| `extraction_timestamp` | ISO-8601 extraction timestamp |
| `parser_version` | Extractor parser version (`1.0.0`) |
| `record_hash` | SHA-256 fingerprint of raw content |
| `validation_status` | VALID, WARNING, or INVALID |
| `validation_errors` | Diagnostics and validation messages |
