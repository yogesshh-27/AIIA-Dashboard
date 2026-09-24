"""Command-line interface and orchestrator for the CTRI Clinical Trial Extractor."""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List
import yaml

from src.deduplicator import CTRIDeduplicator
from src.discovery import discover_trials
from src.exporter import export_csv, export_json, generate_quality_report, log_extraction_event
from src.fetcher import CTRIFetcher
from src.normalizer import normalize_trial_record
from src.parser import CTRIHTMLParser, PARSER_VERSION
from src.pdf_parser import CTRIPDFParser
from src.validator import validate_trial_record

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ctri_extractor.main")

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    logger.warning(f"Config file {config_path} not found. Using defaults.")
    return {}

def run_pipeline(
    max_trials: int = 100,
    keywords: List[str] = None,
    force_refresh: bool = False,
    config_path: str = "config.yaml",
    db_path: str = None
):
    """Run full extraction pipeline."""
    config = load_config(config_path)

    # Resolve settings from config with CLI overrides
    src_cfg = config.get("source", {})
    search_cfg = config.get("search", {})
    out_cfg = config.get("output", {})
    behavior_cfg = config.get("behavior", {})

    base_url = src_cfg.get("base_url", "https://ctri.nic.in/")
    delay_seconds = src_cfg.get("delay_seconds", 3.0)
    timeout_seconds = src_cfg.get("timeout_seconds", 30.0)
    max_retries = src_cfg.get("max_retries", 3)
    user_agent = src_cfg.get("user_agent", "AYURCTMS-CTRI-Extractor/1.0")

    if not keywords:
        keywords = search_cfg.get("keywords", ["Ayurveda", "Ayurvedic", "AYUSH"])

    if max_trials is None:
        max_trials = search_cfg.get("max_trials", 100)

    csv_out = out_cfg.get("csv", "output/ctri_trials.csv")
    json_out = out_cfg.get("json", "output/ctri_trials.json")
    log_out = out_cfg.get("extraction_log", "output/extraction_log.csv")
    manual_review_out = out_cfg.get("manual_review", "output/manual_review.csv")
    quality_report_out = out_cfg.get("quality_report", "output/quality_report.txt")

    download_pdf_flag = behavior_cfg.get("download_pdf", True)

    # Print Start Banner
    print("\nAYURCTMS CTRI EXTRACTOR\n")
    print("Keywords:")
    for kw in keywords:
        print(f"  {kw}")
    print(f"\nTarget:\n  {max_trials} trials\n")
    print("----------------------------\n")

    # Step 1: Discovery
    discovered_trials = discover_trials(
        keywords=keywords,
        base_url=base_url,
        max_trials=max_trials,
        output_path="data/processed/discovered_trials.csv",
        manual_review_path=manual_review_out,
        db_path=db_path
    )

    fetcher = CTRIFetcher(
        delay_seconds=delay_seconds,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        user_agent=user_agent,
        raw_html_dir="data/raw/html",
        raw_pdf_dir="data/raw/pdf",
        progress_path="data/processed/progress.json",
        manual_review_path=manual_review_out
    )
    html_parser = CTRIHTMLParser()
    pdf_parser = CTRIPDFParser()
    deduplicator = CTRIDeduplicator()

    extracted_records: List[Dict[str, Any]] = []
    blocked_count = 0
    failed_count = 0
    successful_count = 0

    # Step 2: Fetching & Parsing
    for idx, disc in enumerate(discovered_trials, 1):
        ctri_num = disc.get("ctri_number", f"TRIAL_{idx}")
        source_url = disc.get("source_url")
        trial_id = disc.get("trial_id")

        html_text, status, http_status, error_msg = fetcher.fetch_trial(
            ctri_number=ctri_num,
            source_url=source_url,
            force_refresh=force_refresh
        )

        timestamp = datetime.now(timezone.utc).isoformat()

        if status == "ACCESS_BLOCKED":
            blocked_count += 1
            log_extraction_event(
                log_out, timestamp, ctri_num, source_url, "ACCESS_BLOCKED",
                http_status, 0, 0, error_msg or "CAPTCHA / human verification", PARSER_VERSION
            )
            continue

        if status != "SUCCESS" or not html_text:
            failed_count += 1
            log_extraction_event(
                log_out, timestamp, ctri_num, source_url, status,
                http_status, 0, max_retries, error_msg or "Failed to retrieve record", PARSER_VERSION
            )
            continue

        # Parse HTML
        try:
            parsed = html_parser.parse(html_text, source_url, trial_id)
            
            # Check for PDF Fallback if HTML is incomplete and PDF is available
            if download_pdf_flag and parsed.get("source_pdf_url"):
                pdf_url = parsed["source_pdf_url"]
                pdf_path = fetcher.download_pdf(ctri_num, pdf_url)
                if pdf_path:
                    pdf_data = pdf_parser.parse_pdf(pdf_path)
                    parsed = pdf_parser.merge_with_html(parsed, pdf_data)

            # Normalize record
            normalized = normalize_trial_record(parsed)

            # Validate record
            val_status, val_errors = validate_trial_record(
                normalized,
                seen_ctri_numbers=deduplicator.seen_ctri_numbers
            )
            normalized["validation_status"] = val_status
            normalized["validation_errors"] = val_errors

            # Count non-empty fields
            fields_count = sum(1 for v in normalized.values() if v not in (None, "", "NULL"))

            log_extraction_event(
                log_out, timestamp, normalized.get("ctri_number") or ctri_num, source_url,
                "SUCCESS", http_status, fields_count, 0, "", PARSER_VERSION
            )

            extracted_records.append(normalized)
            successful_count += 1

        except Exception as e:
            logger.error(f"Error parsing {ctri_num}: {e}")
            failed_count += 1
            log_extraction_event(
                log_out, timestamp, ctri_num, source_url, "PARSE_ERROR",
                http_status, 0, 0, str(e), PARSER_VERSION
            )

    # Step 3: Deduplication
    unique_records, dup_count, _ = deduplicator.deduplicate(extracted_records)

    # Step 4: Exporter
    export_csv(unique_records, csv_out)
    export_json(unique_records, json_out)

    # Count manual review records
    manual_review_count = blocked_count
    if os.path.exists(manual_review_out):
        try:
            import csv
            with open(manual_review_out, "r", encoding="utf-8") as f:
                manual_review_count = max(0, sum(1 for _ in csv.reader(f)) - 1)
        except Exception:
            pass

    generate_quality_report(
        records=unique_records,
        total_discovered=len(discovered_trials),
        duplicates_removed=dup_count,
        access_blocked_count=blocked_count,
        failed_count=failed_count,
        manual_review_count=manual_review_count,
        output_path=quality_report_out
    )

    # Terminal Output Summary
    print(f"Discovered: {len(discovered_trials)}")
    print(f"Unique: {len(unique_records)}")
    print(f"Successful: {successful_count}")
    print(f"Blocked: {blocked_count}")
    print(f"Failed: {failed_count}")
    print(f"Duplicates removed: {dup_count}")
    print(f"\nOutput:\n{csv_out}\n")

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AYURCTMS CTRI Clinical Trial Data Extractor")
    parser.add_argument("--max-trials", type=int, default=None, help="Maximum number of trials to extract (e.g. 50, 100)")
    parser.add_argument("--keyword", action="append", dest="keywords", help="Search keyword (can specify multiple)")
    parser.add_argument("--force-refresh", action="store_true", help="Force re-download of existing records")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--db-path", default=None, help="Path to SQLite database dump (e.g. JM_CTRIdb.sqlite)")

    args = parser.parse_args()
    run_pipeline(
        max_trials=args.max_trials,
        keywords=args.keywords,
        force_refresh=args.force_refresh,
        config_path=args.config,
        db_path=args.db_path
    )

if __name__ == "__main__":
    main()
