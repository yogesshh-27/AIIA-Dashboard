"""Fetcher module for retrieving publicly accessible CTRI trial pages."""

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("ctri_extractor.fetcher")

class AccessBlockedError(Exception):
    """Raised when access is blocked by human verification or CAPTCHA."""
    pass

class CTRIFetcher:
    """Manages rate-limited, polite HTTP requests to CTRI."""
    
    def __init__(
        self,
        delay_seconds: float = 3.0,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        user_agent: str = "AYURCTMS-CTRI-Extractor/1.0",
        raw_html_dir: str = "data/raw/html",
        raw_pdf_dir: str = "data/raw/pdf",
        progress_path: str = "data/processed/progress.json",
        manual_review_path: str = "output/manual_review.csv"
    ):
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.raw_html_dir = raw_html_dir
        self.raw_pdf_dir = raw_pdf_dir
        self.progress_path = progress_path
        self.manual_review_path = manual_review_path
        
        os.makedirs(self.raw_html_dir, exist_ok=True)
        os.makedirs(self.raw_pdf_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.progress_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.manual_review_path), exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        })
        self._last_request_time = 0.0
        self.progress = self._load_progress()

    def _load_progress(self) -> Dict[str, Dict]:
        """Load resume/progress state."""
        if os.path.exists(self.progress_path):
            try:
                with open(self.progress_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
        return {}

    def _save_progress(self):
        """Save resume/progress state."""
        try:
            with open(self.progress_path, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save progress file: {e}")

    def _rate_limit(self):
        """Enforce configured polite delay between network requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay_seconds:
            sleep_duration = self.delay_seconds - elapsed
            time.sleep(sleep_duration)
        self._last_request_time = time.time()

    def sanitize_filename(self, ctri_number: str) -> str:
        """Sanitize CTRI number for safe local filename."""
        clean = re.sub(r'[^a-zA-Z0-9_-]', '_', ctri_number)
        return clean.strip('_')

    def check_access_blocked(self, html_text: str) -> Tuple[bool, str]:
        """Detect CAPTCHA, Cloudflare, human verification, or security block.
        
        Adheres to Rule 2: NEVER bypass or defeat anti-bot systems.
        """
        lower = html_text.lower()
        if "captcha" in lower and ("captcha_image" in lower or "captchafiles" in lower):
            return True, "CAPTCHA verification detected"
        if "verify you are human" in lower or "cloudflare" in lower and "ray id" in lower:
            return True, "Cloudflare / Human verification detected"
        if "security code did not match" in lower:
            return True, "Security code challenge detected"
        if "access denied" in lower or "forbidden" in lower and len(html_text) < 1000:
            return True, "Access denied / forbidden"
        return False, ""

    def fetch_trial(
        self,
        ctri_number: str,
        source_url: str,
        force_refresh: bool = False
    ) -> Tuple[Optional[str], str, int, Optional[str]]:
        """Fetch trial HTML page with rate limiting, retries, and caching.
        
        Returns:
            (html_content, status, http_status_code, error_message)
            Status values: SUCCESS, ACCESS_BLOCKED, NOT_FOUND, SERVER_ERROR, TIMEOUT, PARSE_ERROR
        """
        safe_name = self.sanitize_filename(ctri_number)
        html_file = os.path.join(self.raw_html_dir, f"{safe_name}.html")
        
        # Check cache if resume/cache is active and not force_refresh
        if not force_refresh and os.path.exists(html_file):
            try:
                with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if content and len(content) > 500:
                    logger.debug(f"Loaded {ctri_number} from local raw cache: {html_file}")
                    return content, "SUCCESS", 200, None
            except Exception as e:
                logger.warning(f"Error reading cached file {html_file}: {e}")

        # Execute HTTP request with exponential backoff retries
        retries = 0
        backoffs = [3, 6, 12]
        last_error = None
        
        while retries <= self.max_retries:
            self._rate_limit()
            try:
                logger.info(f"Fetching CTRI record: {ctri_number} from {source_url} (attempt {retries + 1})")
                resp = self.session.get(source_url, timeout=self.timeout_seconds)
                
                # Check for HTTP status codes
                if resp.status_code == 404:
                    return None, "NOT_FOUND", 404, "Page not found"
                if resp.status_code >= 500:
                    last_error = f"Server returned HTTP {resp.status_code}"
                    retries += 1
                    if retries <= self.max_retries:
                        delay = backoffs[min(retries - 1, len(backoffs) - 1)]
                        logger.warning(f"Server error {resp.status_code}, backing off for {delay}s...")
                        time.sleep(delay)
                    continue

                html_text = resp.text

                # Check if access is blocked by CAPTCHA / human verification (Rule 2)
                is_blocked, block_reason = self.check_access_blocked(html_text)
                if is_blocked:
                    logger.warning(f"ACCESS_BLOCKED for {ctri_number}: {block_reason}. Stopping processing of this record.")
                    self._record_manual_review(ctri_number, source_url, "ACCESS_BLOCKED", block_reason)
                    self.progress[ctri_number] = {
                        "status": "ACCESS_BLOCKED",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    self._save_progress()
                    return None, "ACCESS_BLOCKED", resp.status_code, block_reason

                # Save raw HTML unmodified
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_text)

                self.progress[ctri_number] = {
                    "status": "SUCCESS",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "cached_file": html_file
                }
                self._save_progress()
                return html_text, "SUCCESS", resp.status_code, None

            except requests.Timeout as e:
                last_error = f"Request timed out: {e}"
                retries += 1
                if retries <= self.max_retries:
                    delay = backoffs[min(retries - 1, len(backoffs) - 1)]
                    logger.warning(f"Timeout on {source_url}, retrying in {delay}s...")
                    time.sleep(delay)
            except requests.RequestException as e:
                last_error = f"Network request error: {e}"
                retries += 1
                if retries <= self.max_retries:
                    delay = backoffs[min(retries - 1, len(backoffs) - 1)]
                    logger.warning(f"Network error on {source_url}, retrying in {delay}s...")
                    time.sleep(delay)

        # Max retries exhausted
        logger.error(f"Failed to fetch {ctri_number} after {self.max_retries} retries: {last_error}")
        return None, "TIMEOUT" if "timed out" in str(last_error).lower() else "SERVER_ERROR", 0, str(last_error)

    def download_pdf(self, ctri_number: str, pdf_url: str) -> Optional[str]:
        """Download and store publicly available trial PDF."""
        safe_name = self.sanitize_filename(ctri_number)
        pdf_file = os.path.join(self.raw_pdf_dir, f"{safe_name}.pdf")
        if os.path.exists(pdf_file):
            return pdf_file

        self._rate_limit()
        try:
            resp = self.session.get(pdf_url, timeout=self.timeout_seconds)
            if resp.status_code == 200 and resp.content.startswith(b"%PDF"):
                with open(pdf_file, "wb") as f:
                    f.write(resp.content)
                logger.info(f"Downloaded PDF for {ctri_number} -> {pdf_file}")
                return pdf_file
        except Exception as e:
            logger.warning(f"Failed to download PDF for {ctri_number} from {pdf_url}: {e}")
        return None

    def _record_manual_review(self, ctri_number: str, source_url: str, reason: str, notes: str):
        """Append record to manual review CSV."""
        import csv
        file_exists = os.path.exists(self.manual_review_path)
        with open(self.manual_review_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["ctri_number", "source_url", "reason", "timestamp", "status", "notes"])
            writer.writerow([
                ctri_number,
                source_url,
                reason,
                datetime.now(timezone.utc).isoformat(),
                "BLOCKED" if reason == "ACCESS_BLOCKED" else "REVIEW_NEEDED",
                notes
            ])
