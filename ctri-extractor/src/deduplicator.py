"""Deduplication module for CTRI trial records."""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger("ctri_extractor.deduplicator")

class CTRIDeduplicator:
    """Performs primary and secondary deduplication on CTRI records."""

    def __init__(self):
        self.seen_ctri_numbers: Set[str] = set()
        self.seen_secondary_keys: Set[Tuple[str, str, str]] = set()

    @staticmethod
    def _normalize_title_for_dedup(title: str) -> str:
        """Strip punctuation and whitespace for fuzzy title comparison."""
        clean = re.sub(r'[^a-zA-Z0-9]', '', (title or "").lower())
        return clean

    @staticmethod
    def _normalize_pi_for_dedup(pi: str) -> str:
        """Normalize investigator name."""
        clean = re.sub(r'^(dr|prof|mr|mrs|ms)\.?\s*', '', (pi or "").lower())
        clean = re.sub(r'[^a-zA-Z0-9]', '', clean)
        return clean

    def is_duplicate(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if record is a duplicate by primary or secondary key."""
        ctri_num = (record.get("ctri_number") or "").strip()
        if ctri_num and ctri_num in self.seen_ctri_numbers:
            return True, f"Primary key match: {ctri_num}"

        title = self._normalize_title_for_dedup(record.get("public_title") or "")
        pi = self._normalize_pi_for_dedup(record.get("principal_investigator") or "")
        date_enrol = str(record.get("date_first_enrolment") or "").strip()

        # If all three secondary attributes exist, check secondary key
        if title and pi and date_enrol and date_enrol not in ("None", "NULL"):
            sec_key = (title, pi, date_enrol)
            if sec_key in self.seen_secondary_keys:
                return True, f"Secondary key match: title+PI+date ({ctri_num})"

        return False, ""

    def register(self, record: Dict[str, Any]):
        """Register record keys into seen sets."""
        ctri_num = (record.get("ctri_number") or "").strip()
        if ctri_num:
            self.seen_ctri_numbers.add(ctri_num)

        title = self._normalize_title_for_dedup(record.get("public_title") or "")
        pi = self._normalize_pi_for_dedup(record.get("principal_investigator") or "")
        date_enrol = str(record.get("date_first_enrolment") or "").strip()
        if title and pi and date_enrol and date_enrol not in ("None", "NULL"):
            self.seen_secondary_keys.add((title, pi, date_enrol))

    def deduplicate(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int, List[Dict[str, Any]]]:
        """Deduplicate a list of records.
        
        Returns:
            (unique_records, duplicate_count, duplicates_list)
        """
        unique: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []

        for rec in records:
            is_dup, reason = self.is_duplicate(rec)
            if is_dup:
                logger.info(f"Duplicate trial discarded: {rec.get('ctri_number')} ({reason})")
                duplicates.append({"record": rec, "reason": reason})
            else:
                self.register(rec)
                unique.append(rec)

        return unique, len(duplicates), duplicates
