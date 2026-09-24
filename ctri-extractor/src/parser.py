"""HTML Parser module for extracting CTRI clinical trial fields semantically."""

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger("ctri_extractor.parser")

PARSER_VERSION = "1.0.0"

class CTRIHTMLParser:
    """Semantic parser for publicly accessible CTRI trial pages."""
    
    def __init__(self, version: str = PARSER_VERSION):
        self.version = version

    def compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of the raw response."""
        return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()

    def parse(self, html_text: str, source_url: str, trial_id: Optional[str] = None) -> Dict[str, Any]:
        """Parse CTRI HTML page into structured trial dictionary."""
        timestamp = datetime.now(timezone.utc).isoformat()
        record_hash = self.compute_hash(html_text)
        
        soup = BeautifulSoup(html_text, "html.parser")
        
        # 1. Main Study Rows Extraction
        # In CTRI showallp.php, the table containing 'Public Title of Study' contains direct field rows
        main_table = None
        for tbl in soup.find_all("table"):
            text = tbl.get_text()
            if "Public Title of Study" in text and "CTRI Number" in text:
                main_table = tbl
                break
        if not main_table and soup.find("table"):
            main_table = soup.find_all("table")[0]

        direct_kv: Dict[str, Any] = {}
        if main_table:
            for tr in main_table.find_all("tr", recursive=False):
                cells = tr.find_all("td", recursive=False)
                if len(cells) >= 2:
                    label = cells[0].get_text(separator=" ", strip=True)
                    # Strip any Modification(s) tag or punctuation
                    clean_label = re.sub(r'Modification\(s\)', '', label, flags=re.IGNORECASE)
                    clean_label = re.sub(r'\s+', ' ', clean_label).strip().rstrip(":")
                    direct_kv[clean_label] = cells[1]
                elif len(cells) == 1:
                    lbl = cells[0].get_text(separator=" ", strip=True)
                    clean_lbl = re.sub(r'Modification\(s\)', '', lbl, flags=re.IGNORECASE)
                    clean_lbl = re.sub(r'\s+', ' ', clean_lbl).strip().rstrip(":")
                    direct_kv[clean_lbl] = cells[0]

        # Helper to find cell by regex in direct_kv or entire soup
        def find_cell(pattern: str) -> Optional[Tag]:
            for k, val in direct_kv.items():
                if re.search(pattern, k, re.IGNORECASE):
                    return val if isinstance(val, Tag) else None
            # Fallback across all trs
            for tr in soup.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if cells:
                    lbl = re.sub(r'Modification\(s\)', '', cells[0].get_text(strip=True), flags=re.IGNORECASE)
                    if re.search(pattern, lbl, re.IGNORECASE):
                        return cells[1] if len(cells) > 1 else cells[0]
            return None

        def extract_text(pattern: str) -> Optional[str]:
            cell = find_cell(pattern)
            if cell:
                # clone and strip nested tables
                clone = BeautifulSoup(str(cell), "html.parser")
                for inner in clone.find_all("table"):
                    inner.decompose()
                txt = clone.get_text(separator=" ", strip=True)
                txt = re.sub(r'\s+', ' ', txt).strip()
                if txt in ("NIL", "None", "No Date Specified", "Not Applicable", ""):
                    if txt == "No Date Specified" or txt == "NIL" or txt == "None" or not txt:
                        return None
                return txt or None
            return None

        # 2. Identification Fields
        ctri_match = re.search(r"CTRI/\d{4}/\d{2,3}/\d+", html_text)
        ctri_number = ctri_match.group(0) if ctri_match else None
        
        reg_status = "Registered" if ctri_number else "Pending"
        reg_match = re.search(r"Registered\s*on:\s*(\d{1,2}/\d{1,2}/\d{4})", html_text)
        reg_date = reg_match.group(1) if reg_match else None

        # 3. Study Details
        public_title = extract_text(r"^Public\s*Title")
        scientific_title = extract_text(r"^Scientific\s*Title")
        study_type = extract_text(r"^Type\s*of\s*Study") or extract_text(r"^Type\s*of\s*Trial")
        study_design = extract_text(r"^Study\s*Design")
        trial_phase = extract_text(r"^Phase\s*of\s*Trial")
        study_category = extract_text(r"^Type\s*of\s*Trial") or extract_text(r"^Post\s*Graduate\s*Thesis")

        # 4. Secondary IDs
        sec_id_cell = find_cell(r"^Secondary\s*IDs")
        sec_ids = self._parse_subtable_rows(sec_id_cell)

        # 5. Principal Investigator
        pi_cell = find_cell(r"^Details\s*of\s*Principal\s*Investigator")
        pi_kv = self._parse_kv_subtable(pi_cell)
        principal_investigator = pi_kv.get("Name")
        investigator_affiliation = pi_kv.get("Address")
        pi_contacts = []
        if pi_kv.get("Phone"):
            pi_contacts.append(f"Phone: {pi_kv.get('Phone')}")
        if pi_kv.get("Email"):
            pi_contacts.append(f"Email: {pi_kv.get('Email')}")
        if pi_kv.get("Fax"):
            pi_contacts.append(f"Fax: {pi_kv.get('Fax')}")
        investigator_contact = " | ".join(pi_contacts) if pi_contacts else None

        # 6. Sponsor Details
        sponsor_cell = find_cell(r"^Primary\s*Sponsor")
        sponsor_kv = self._parse_kv_subtable(sponsor_cell)
        primary_sponsor = sponsor_kv.get("Name")
        sponsor_type = sponsor_kv.get("Type of Sponsor")

        sec_sponsor_cell = find_cell(r"^Details\s*of\s*Secondary\s*Sponsor")
        sec_sponsor_kv = self._parse_kv_subtable(sec_sponsor_cell)
        secondary_sponsor = sec_sponsor_kv.get("Name") or sec_sponsor_kv.get("Address")

        # 7. Sites of Study / Location
        sites_cell = find_cell(r"^Sites\s*of\s*Study")
        sites_data = self._parse_sites_table(sites_cell)
        site_names = [s.get("site_name") for s in sites_data if s.get("site_name")]
        site_addrs = [s.get("site_address") for s in sites_data if s.get("site_address")]
        site_name = " ; ".join(site_names) if site_names else None
        site_address = " ; ".join(site_addrs) if site_addrs else None

        country = extract_text(r"^Countries\s*of\s*Recruitment") or "India"
        
        # Extract City, State, District
        loc_text = f"{site_address or ''} {site_name or ''} {investigator_affiliation or ''}"
        state = self._extract_state(loc_text)
        district = self._extract_district(loc_text)
        city = self._extract_city(loc_text)

        # 8. Ethics Committee & Regulatory
        ethics_cell = find_cell(r"^Details\s*of\s*Ethics\s*Committee")
        ethics_data = self._parse_ethics_table(ethics_cell)
        ethics_names = [e.get("name") for e in ethics_data if e.get("name")]
        ethics_statuses = [e.get("status") for e in ethics_data if e.get("status")]
        ethics_committee = " ; ".join(ethics_names) if ethics_names else None
        ethics_approval_status = " ; ".join(set(ethics_statuses)) if ethics_statuses else None

        dcgi_cell = find_cell(r"^Regulatory\s*Clearance\s*Status\s*from\s*DCGI")
        dcgi_status = None
        if dcgi_cell:
            dcgi_text = dcgi_cell.get_text(separator=" ", strip=True)
            dcgi_status_match = re.search(r'(?:Status\s*)?([A-Za-z\s]+)', dcgi_text)
            if dcgi_status_match:
                dcgi_status = dcgi_status_match.group(1).replace("Status", "").strip()
        dcgi_approval_status = dcgi_status
        regulatory_status = dcgi_status

        # 9. Health Condition
        cond_cell = find_cell(r"^Health\s*Condition")
        conditions, disease_cats = self._parse_health_condition(cond_cell)
        condition = " ; ".join(conditions) if conditions else None
        health_condition = condition
        disease_category = " ; ".join(disease_cats) if disease_cats else None

        # 10. Interventions & Comparators
        interv_cell = find_cell(r"^Intervention\s*/\s*Comparator")
        interventions, comparators = self._parse_interventions_table(interv_cell)
        
        interv_names = [i.get("name") for i in interventions if i.get("name")]
        interv_types = [i.get("type") for i in interventions if i.get("type")]
        interv_descs = [i.get("details") for i in interventions if i.get("details")]
        
        intervention_name = " ; ".join(interv_names) if interv_names else None
        intervention_type = " ; ".join(set(interv_types)) if interv_types else None
        intervention_description = " ; ".join(interv_descs) if interv_descs else None
        
        comp_items = [f"{c.get('name', '')} ({c.get('details', '')})".strip(' ()') for c in comparators]
        comparator = " ; ".join(comp_items) if comp_items else None

        # 11. Eligibility
        incl_cell = find_cell(r"^Inclusion\s*Criteria")
        inclusion_criteria = self._parse_criteria(incl_cell)

        excl_cell = find_cell(r"^Exclusion\s*Criteria")
        exclusion_criteria = self._parse_criteria(excl_cell)

        # 12. Outcomes
        prim_cell = find_cell(r"^Primary\s*Outcome")
        primary_outcome = self._parse_outcome_table(prim_cell)

        sec_cell = find_cell(r"^Secondary\s*Outcome")
        secondary_outcome = self._parse_outcome_table(sec_cell)

        # 13. Recruitment Details
        rec_status_ind = extract_text(r"^Recruitment\s*Status\s*of\s*Trial\s*\(India\)")
        rec_status_glob = extract_text(r"^Recruitment\s*Status\s*of\s*Trial\s*\(Global\)")
        raw_recruitment_status = rec_status_ind or rec_status_glob

        date_first_ind = extract_text(r"^Date\s*of\s*First\s*Enrollment\s*\(India\)")
        date_first_glob = extract_text(r"^Date\s*of\s*First\s*Enrollment\s*\(Global\)")
        date_first_enrolment = date_first_ind or date_first_glob

        est_duration = extract_text(r"^Estimated\s*Duration\s*of\s*Trial")
        
        # Sample Size
        sample_cell = find_cell(r"^Target\s*Sample\s*Size")
        target_sample_size = None
        if sample_cell:
            sz_text = sample_cell.get_text()
            m = re.search(r'Total\s*Sample\s*Size\s*=\s*"?(\d+)"?', sz_text, re.IGNORECASE)
            if m:
                target_sample_size = m.group(1)
            else:
                m2 = re.search(r'(\d+)', sz_text)
                if m2:
                    target_sample_size = m2.group(1)

        final_enrolment = extract_text(r"^Final\s*Enrollment")
        actual_completion_date = extract_text(r"^Date\s*of\s*Study\s*Completion")

        # 14. Descriptions
        brief_summary = extract_text(r"^Brief\s*Summary")
        study_description = extract_text(r"^Study\s*Description") or brief_summary

        # Check for PDF link
        source_pdf_url = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf") or ("pdf" in href.lower() and "trial" in href.lower()):
                if href.startswith("http"):
                    source_pdf_url = href
                else:
                    source_pdf_url = f"{source_url.split('/Clinicaltrials')[0]}/{href.lstrip('/')}"
                break

        if not trial_id:
            m_tid = re.search(r'mid1=(\d+)', source_url)
            if m_tid:
                trial_id = m_tid.group(1)

        return {
            "trial_id": trial_id,
            "ctri_number": ctri_number,
            "public_title": public_title,
            "scientific_title": scientific_title,
            "study_type": study_type,
            "study_design": study_design,
            "trial_phase": trial_phase,
            "study_category": study_category,
            "condition": condition,
            "health_condition": health_condition,
            "disease_category": disease_category,
            "intervention_name": intervention_name,
            "intervention_type": intervention_type,
            "intervention_description": intervention_description,
            "comparator": comparator,
            "principal_investigator": principal_investigator,
            "investigator_affiliation": investigator_affiliation,
            "investigator_contact": investigator_contact,
            "primary_sponsor": primary_sponsor,
            "secondary_sponsor": secondary_sponsor,
            "sponsor_type": sponsor_type,
            "country": country,
            "state": state,
            "district": district,
            "city": city,
            "site_name": site_name,
            "site_address": site_address,
            "ethics_committee": ethics_committee,
            "ethics_approval_status": ethics_approval_status,
            "dcgi_approval_status": dcgi_approval_status,
            "regulatory_status": regulatory_status,
            "ctri_registration_status": reg_status,
            "recruitment_status": raw_recruitment_status,
            "raw_recruitment_status": raw_recruitment_status,
            "date_first_enrolment": date_first_enrolment,
            "estimated_duration": est_duration,
            "target_sample_size": target_sample_size,
            "final_enrolment": final_enrolment,
            "actual_completion_date": actual_completion_date,
            "primary_outcome": primary_outcome,
            "secondary_outcome": secondary_outcome,
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "brief_summary": brief_summary,
            "study_description": study_description,
            "source_url": source_url,
            "source_pdf_url": source_pdf_url,
            "source_name": "Clinical Trials Registry - India (CTRI)",
            "extraction_timestamp": timestamp,
            "parser_version": self.version,
            "record_hash": record_hash,
            "registered_on_raw": reg_date
        }

    def _parse_kv_subtable(self, cell: Optional[Tag]) -> Dict[str, str]:
        """Parse key-value table inside a cell."""
        res = {}
        if not cell:
            return res
        table = cell.find("table") or cell
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) == 2:
                k = cells[0].get_text(strip=True).rstrip(":")
                v = cells[1].get_text(separator=" ", strip=True)
                if k and v:
                    res[k] = re.sub(r'\s+', ' ', v).strip()
            elif len(cells) == 1 and ":" in cells[0].get_text():
                parts = cells[0].get_text(strip=True).split(":", 1)
                res[parts[0].strip()] = parts[1].strip()
        return res

    def _parse_subtable_rows(self, cell: Optional[Tag]) -> List[str]:
        """Extract lines from subtable."""
        if not cell:
            return []
        items = []
        table = cell.find("table") or cell
        for tr in table.find_all("tr"):
            txt = tr.get_text(separator=" ", strip=True)
            if txt and not re.search(r"Secondary ID|Registry", txt, re.IGNORECASE):
                items.append(re.sub(r'\s+', ' ', txt).strip())
        return items

    def _parse_sites_table(self, cell: Optional[Tag]) -> List[Dict[str, str]]:
        """Parse Sites of Study table."""
        sites = []
        if not cell:
            return sites
        table = cell.find("table") or cell
        rows = table.find_all("tr")
        if not rows:
            return sites

        header_idx = -1
        headers = []
        for idx, r in enumerate(rows):
            tds = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
            # If line is "No of Sites = ...", skip
            if len(tds) == 1 and "no of sites" in tds[0].lower():
                continue
            if any("site" in h.lower() for h in tds) or any("contact" in h.lower() for h in tds):
                header_idx = idx
                headers = [re.sub(r'\s+', ' ', h).strip() for h in tds]
                break

        if header_idx != -1:
            for r in rows[header_idx + 1:]:
                cells = [c.get_text(separator=" ", strip=True) for c in r.find_all(["td", "th"])]
                if not any(cells):
                    continue
                site_entry = {}
                for h, c in zip(headers, cells):
                    hl = h.lower()
                    if "name of site" in hl:
                        site_entry["site_name"] = re.sub(r'\s+', ' ', c).strip()
                    elif "address" in hl:
                        site_entry["site_address"] = re.sub(r'\s+', ' ', c).strip()
                    elif "contact" in hl:
                        site_entry["contact_person"] = re.sub(r'\s+', ' ', c).strip()
                if site_entry.get("site_name") or site_entry.get("site_address"):
                    sites.append(site_entry)
        return sites

    def _parse_ethics_table(self, cell: Optional[Tag]) -> List[Dict[str, str]]:
        """Parse Details of Ethics Committee table."""
        committees = []
        if not cell:
            return committees
        table = cell.find("table") or cell
        rows = table.find_all("tr")
        for r in rows:
            cells = [c.get_text(separator=" ", strip=True) for c in r.find_all(["td", "th"])]
            if len(cells) >= 2:
                name, status = cells[0].strip(), cells[1].strip()
                if "Name of Committee" in name or "No of Ethics" in name:
                    continue
                if name:
                    committees.append({"name": re.sub(r'\s+', ' ', name), "status": status})
        return committees

    def _parse_health_condition(self, cell: Optional[Tag]) -> Tuple[List[str], List[str]]:
        """Parse Health Condition table."""
        conds, cats = [], []
        if not cell:
            return conds, cats
        table = cell.find("table") or cell
        for r in table.find_all("tr"):
            cells = [c.get_text(separator=" ", strip=True) for c in r.find_all(["td", "th"])]
            if len(cells) >= 2:
                htype, cond = cells[0].strip(), cells[1].strip()
                if "Health Type" in htype or "Condition" in cond:
                    continue
                if cond:
                    conds.append(re.sub(r'\s+', ' ', cond))
                if htype:
                    cats.append(re.sub(r'\s+', ' ', htype))
            elif len(cells) == 1:
                c = cells[0].strip()
                if c and "Health Type" not in c:
                    conds.append(re.sub(r'\s+', ' ', c))
        return conds, cats

    def _parse_interventions_table(self, cell: Optional[Tag]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """Parse Intervention / Comparator table."""
        interventions, comparators = [], []
        if not cell:
            return interventions, comparators
        table = cell.find("table") or cell
        for r in table.find_all("tr"):
            cells = [c.get_text(separator=" ", strip=True) for c in r.find_all(["td", "th"])]
            if len(cells) >= 3:
                itype, iname, idet = cells[0].strip(), cells[1].strip(), cells[2].strip()
                if itype == "Type" and iname == "Name":
                    continue
                entry = {
                    "type": itype,
                    "name": re.sub(r'\s+', ' ', iname),
                    "details": re.sub(r'\s+', ' ', idet)
                }
                if "comparator" in itype.lower():
                    comparators.append(entry)
                else:
                    interventions.append(entry)
            elif len(cells) == 2:
                itype, iname = cells[0].strip(), cells[1].strip()
                if itype == "Type":
                    continue
                entry = {"type": itype, "name": re.sub(r'\s+', ' ', iname), "details": ""}
                if "comparator" in itype.lower():
                    comparators.append(entry)
                else:
                    interventions.append(entry)
        return interventions, comparators

    def _parse_criteria(self, cell: Optional[Tag]) -> Optional[str]:
        """Parse Inclusion or Exclusion criteria cell."""
        if not cell:
            return None
        table = cell.find("table") or cell
        details_txt = ""
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) >= 2:
                lbl = cells[0].get_text(strip=True)
                if "detail" in lbl.lower():
                    details_txt += cells[1].get_text(separator="\n", strip=True) + "\n"
            elif len(cells) == 1:
                t = cells[0].get_text(separator="\n", strip=True)
                if not re.search(r"Age From|Age To|Gender", t):
                    details_txt += t + "\n"
        if not details_txt.strip():
            details_txt = cell.get_text(separator="\n", strip=True)
        clean = re.sub(r"^(Inclusion Criteria|ExclusionCriteria|Details)\s*", "", details_txt.strip(), flags=re.IGNORECASE)
        return clean.strip() or None

    def _parse_outcome_table(self, cell: Optional[Tag]) -> Optional[str]:
        """Parse outcome table into unified string."""
        if not cell:
            return None
        table = cell.find("table") or cell
        outcomes = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(separator=" ", strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) >= 2:
                out, tp = cells[0].strip(), cells[1].strip()
                if out == "Outcome" or tp == "TimePoints":
                    continue
                if out and out != "Not Applicable":
                    line = f"{out} (TimePoints: {tp})" if tp else out
                    outcomes.append(re.sub(r'\s+', ' ', line))
            elif len(cells) == 1:
                out = cells[0].strip()
                if out and out not in ("Outcome", "TimePoints", "Not Applicable"):
                    outcomes.append(re.sub(r'\s+', ' ', out))
        return " ; ".join(outcomes) if outcomes else None

    def _extract_state(self, text: str) -> Optional[str]:
        """Extract Indian state from address text."""
        indian_states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Delhi", "New Delhi", "Chandigarh", "Jammu and Kashmir", "Jammu & Kashmir",
            "Puducherry", "Ladakh"
        ]
        for st in indian_states:
            if re.search(r'\b' + re.escape(st) + r'\b', text, re.IGNORECASE):
                if st.lower() in ("new delhi", "delhi"):
                    return "Delhi"
                if "jammu" in st.lower():
                    return "Jammu and Kashmir"
                return st.title()
        return None

    def _extract_district(self, text: str) -> Optional[str]:
        """Extract district from address text if present."""
        m = re.search(r'(?:Dist\.?|District)[:\s]+([a-zA-Z\s]+?)(?:,|\.|\d|\n|$)', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None

    def _extract_city(self, text: str) -> Optional[str]:
        """Extract prominent Indian city from address text."""
        cities = [
            "Mumbai", "Delhi", "New Delhi", "Bengaluru", "Bangalore", "Hyderabad",
            "Chennai", "Kolkata", "Ahmedabad", "Pune", "Jaipur", "Surat", "Lucknow",
            "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri",
            "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad",
            "Meerut", "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
            "Amritsar", "Navi Mumbai", "Allahabad", "Prayagraj", "Ranchi", "Howrah",
            "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai",
            "Raipur", "Kota", "Guwahati", "Chandigarh", "Solapur", "Hubli", "Bareilly",
            "Mysore", "Mysuru", "Tiruchirappalli", "Aligarh", "Trivandrum", "Thiruvananthapuram",
            "Bhubaneswar", "Dehradun", "Rishikesh", "Jamnagar", "Haridwar", "Kottakkal",
            "Udupi", "Belgaum", "Nadiad"
        ]
        for c in cities:
            if re.search(r'\b' + re.escape(c) + r'\b', text, re.IGNORECASE):
                if c.lower() in ("bengaluru", "bangalore"):
                    return "Bengaluru"
                if c.lower() in ("new delhi", "delhi"):
                    return "Delhi"
                if c.lower() in ("thiruvananthapuram", "trivandrum"):
                    return "Thiruvananthapuram"
                return c
        return None
