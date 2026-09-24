"""PDF Fallback Parser module using pdfplumber to extract fields from trial PDFs."""

import logging
import os
import re
from typing import Any, Dict, Optional
import pdfplumber

logger = logging.getLogger("ctri_extractor.pdf_parser")

class CTRIPDFParser:
    """Extracts trial fields from CTRI PDF files as a fallback."""

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract trial fields from a local PDF file."""
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF file does not exist: {pdf_path}")
            return {}

        extracted: Dict[str, Any] = {}
        full_text = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text.append(text)
                    
                    # Also inspect tables on page
                    tables = page.extract_tables()
                    for tbl in tables:
                        for row in tbl:
                            if not row or len(row) < 2:
                                continue
                            k = str(row[0] or "").strip()
                            v = str(row[1] or "").strip()
                            if "ctri number" in k.lower():
                                m = re.search(r'CTRI/\d{4}/\d{2,3}/\d+', v or k)
                                if m:
                                    extracted["ctri_number"] = m.group(0)
                            elif "public title" in k.lower():
                                extracted["public_title"] = v
                            elif "scientific title" in k.lower():
                                extracted["scientific_title"] = v
                            elif "principal investigator" in k.lower() or "pi" in k.lower():
                                extracted["principal_investigator"] = v
                            elif "health condition" in k.lower() or "condition" in k.lower():
                                extracted["condition"] = v
                            elif "intervention" in k.lower():
                                extracted["intervention_name"] = v

            combined_text = "\n".join(full_text)
            
            # Regex extraction for common fields if not found in tables
            if not extracted.get("ctri_number"):
                m_ctri = re.search(r'CTRI/\d{4}/\d{2,3}/\d+', combined_text)
                if m_ctri:
                    extracted["ctri_number"] = m_ctri.group(0)

            if not extracted.get("public_title"):
                m_title = re.search(r'Public\s*Title\s*(?:of\s*Study)?[:\s]+([^\n]+)', combined_text, re.IGNORECASE)
                if m_title:
                    extracted["public_title"] = m_title.group(1).strip()

            if not extracted.get("scientific_title"):
                m_stitle = re.search(r'Scientific\s*Title\s*(?:of\s*Study)?[:\s]+([^\n]+)', combined_text, re.IGNORECASE)
                if m_stitle:
                    extracted["scientific_title"] = m_stitle.group(1).strip()

            if not extracted.get("principal_investigator"):
                m_pi = re.search(r'Principal\s*Investigator[:\s]+([^\n]+)', combined_text, re.IGNORECASE)
                if m_pi:
                    extracted["principal_investigator"] = m_pi.group(1).strip()

            if not extracted.get("condition"):
                m_cond = re.search(r'Health\s*Condition[:\s]+([^\n]+)', combined_text, re.IGNORECASE)
                if m_cond:
                    extracted["condition"] = m_cond.group(1).strip()
                    extracted["health_condition"] = m_cond.group(1).strip()

            if not extracted.get("brief_summary"):
                m_sum = re.search(r'Brief\s*Summary[:\s]+([\s\S]+?)(?:Primary\s*Outcome|Inclusion|Exclusion|$)', combined_text, re.IGNORECASE)
                if m_sum:
                    extracted["brief_summary"] = m_sum.group(1).strip()

        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")

        return extracted

    @staticmethod
    def merge_with_html(html_record: Dict[str, Any], pdf_record: Dict[str, Any]) -> Dict[str, Any]:
        """Merge PDF fields into HTML record where HTML values are missing.
        
        HTML takes strict priority when both sources provide a value.
        Never fabricates missing values.
        """
        merged = dict(html_record)
        for key, val in pdf_record.items():
            if val and (merged.get(key) is None or str(merged.get(key)).strip() in ("", "None", "NULL")):
                merged[key] = val
        return merged
