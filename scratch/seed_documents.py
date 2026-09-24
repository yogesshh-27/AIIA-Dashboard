import os
import sys
import sqlite3
import hashlib
import datetime

# Ensure project root in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_service

def init_documents_and_storage():
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secure_documents")
    os.makedirs(storage_dir, exist_ok=True)

    conn = db_service.get_app_connection()
    c = conn.cursor()

    # Drop and recreate documents and document_versions
    c.execute("DROP TABLE IF EXISTS document_versions")
    c.execute("DROP TABLE IF EXISTS documents")

    c.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id VARCHAR(50) UNIQUE NOT NULL,
            trial_id INTEGER,
            trial_ctri VARCHAR(100),
            document_name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            current_version VARCHAR(50) NOT NULL,
            uploaded_by VARCHAR(150) NOT NULL,
            upload_date DATETIME NOT NULL,
            status VARCHAR(50) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_path TEXT NOT NULL,
            file_size_kb INTEGER NOT NULL,
            checksum_sha256 VARCHAR(64) NOT NULL,
            security_classification VARCHAR(50) NOT NULL,
            description TEXT
        )
    """)

    c.execute("""
        CREATE TABLE document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            version VARCHAR(50) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_path TEXT NOT NULL,
            file_size_kb INTEGER NOT NULL,
            checksum_sha256 VARCHAR(64) NOT NULL,
            uploaded_by VARCHAR(150) NOT NULL,
            upload_date DATETIME NOT NULL,
            status VARCHAR(50) NOT NULL,
            change_summary TEXT,
            FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
        )
    """)

    # Seed Document definitions across all 6 categories
    doc_seeds = [
        # 1. PROTOCOL
        {
            "doc_id": "DOC-PRT-001",
            "trial_ctri": "CTRI/2017/10/010023",
            "document_name": "Clinical Study Protocol: Guduchi Ghanavati in Osteoarthritis",
            "category": "Protocol",
            "current_version": "v2.1",
            "uploaded_by": "Dr. Galib",
            "upload_date": "2026-08-14 10:30:00",
            "status": "Approved",
            "file_name": "Protocol_Guduchi_OA_v2.1.pdf",
            "security_classification": "Institutional Confidential",
            "description": "Final approved Phase III clinical investigation protocol incorporating DSMB sample size amendment.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "Protocol_Guduchi_OA_v1.0.pdf",
                    "uploaded_by": "Dr. Galib",
                    "upload_date": "2025-09-10 11:00:00",
                    "status": "Superseded",
                    "change_summary": "Initial protocol submitted for Institutional Ethics Committee review.",
                    "size_kb": 2450
                },
                {
                    "version": "v2.0",
                    "file_name": "Protocol_Guduchi_OA_v2.0.pdf",
                    "uploaded_by": "Dr. Galib",
                    "upload_date": "2026-03-15 14:20:00",
                    "status": "Superseded",
                    "change_summary": "Amendment 1: Clarified secondary biomarker endpoint schedules.",
                    "size_kb": 2510
                },
                {
                    "version": "v2.1",
                    "file_name": "Protocol_Guduchi_OA_v2.1.pdf",
                    "uploaded_by": "Dr. Galib",
                    "upload_date": "2026-08-14 10:30:00",
                    "status": "Approved",
                    "change_summary": "Administrative amendment: Updated contact details for CRA monitoring.",
                    "size_kb": 2540
                }
            ]
        },
        {
            "doc_id": "DOC-PRT-002",
            "trial_ctri": "CTRI/2018/02/011783",
            "document_name": "Master Protocol: Ashwagandha Avaleha in Chronic Stress & Fatigue",
            "category": "Protocol",
            "current_version": "v1.2",
            "uploaded_by": "Dr. P. Gupta",
            "upload_date": "2026-07-20 09:15:00",
            "status": "Approved",
            "file_name": "Protocol_Ashwagandha_Stress_v1.2.pdf",
            "security_classification": "Institutional Confidential",
            "description": "Double-blind randomized placebo-controlled investigation protocol.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "Protocol_Ashwagandha_Stress_v1.0.pdf",
                    "uploaded_by": "Dr. P. Gupta",
                    "upload_date": "2026-01-12 10:00:00",
                    "status": "Superseded",
                    "change_summary": "Initial submission draft.",
                    "size_kb": 1890
                },
                {
                    "version": "v1.2",
                    "file_name": "Protocol_Ashwagandha_Stress_v1.2.pdf",
                    "uploaded_by": "Dr. P. Gupta",
                    "upload_date": "2026-07-20 09:15:00",
                    "status": "Approved",
                    "change_summary": "Formal approval version post IEC stipulations.",
                    "size_kb": 1940
                }
            ]
        },

        # 2. IEC / ETHICS
        {
            "doc_id": "DOC-IEC-001",
            "trial_ctri": "CTRI/2017/10/010023",
            "document_name": "Institutional Ethics Committee Clearance Certificate (AIIA-IEC-2024-88)",
            "category": "IEC / Ethics",
            "current_version": "v1.0",
            "uploaded_by": "Dr. K. S. Dhiman",
            "upload_date": "2026-06-18 16:45:00",
            "status": "Approved",
            "file_name": "IEC_Clearance_AIIA_2024_88.pdf",
            "security_classification": "Official Record",
            "description": "Formal annual renewal certificate issued by AIIA Institutional Ethics Committee.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "IEC_Clearance_AIIA_2024_88.pdf",
                    "uploaded_by": "Dr. K. S. Dhiman",
                    "upload_date": "2026-06-18 16:45:00",
                    "status": "Approved",
                    "change_summary": "Signed IEC Approval Certificate with validity through June 2027.",
                    "size_kb": 820
                }
            ]
        },
        {
            "doc_id": "DOC-IEC-002",
            "trial_ctri": "CTRI/2018/02/011783",
            "document_name": "IEC Protocol Amendment Endorsement (AIIA-IEC-AMD-02)",
            "category": "IEC / Ethics",
            "current_version": "v1.1",
            "uploaded_by": "Dr. K. S. Dhiman",
            "upload_date": "2026-07-25 11:20:00",
            "status": "Approved",
            "file_name": "IEC_Amendment_Endorsement_AMD02.pdf",
            "security_classification": "Official Record",
            "description": "Ethics Committee endorsement of revised Patient Information Sheet & Consent Form.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "IEC_Amendment_Endorsement_AMD01.pdf",
                    "uploaded_by": "Dr. K. S. Dhiman",
                    "upload_date": "2026-02-10 14:00:00",
                    "status": "Superseded",
                    "change_summary": "Preliminary ethics review committee observations.",
                    "size_kb": 640
                },
                {
                    "version": "v1.1",
                    "file_name": "IEC_Amendment_Endorsement_AMD02.pdf",
                    "uploaded_by": "Dr. K. S. Dhiman",
                    "upload_date": "2026-07-25 11:20:00",
                    "status": "Approved",
                    "change_summary": "Final signed endorsement letter.",
                    "size_kb": 710
                }
            ]
        },

        # 3. CTRI
        {
            "doc_id": "DOC-CTR-001",
            "trial_ctri": "CTRI/2017/10/010023",
            "document_name": "CTRI Official Registration Verification & Dossier Record",
            "category": "CTRI",
            "current_version": "v1.0",
            "uploaded_by": "Prof. (Dr.) Tanuja Nesari",
            "upload_date": "2026-01-05 09:00:00",
            "status": "Approved",
            "file_name": "CTRI_Registration_Certificate_010023.pdf",
            "security_classification": "Official Record",
            "description": "Official registration acknowledgment from the Clinical Trials Registry - India (ICMR-NIMS).",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "CTRI_Registration_Certificate_010023.pdf",
                    "uploaded_by": "Prof. (Dr.) Tanuja Nesari",
                    "upload_date": "2026-01-05 09:00:00",
                    "status": "Approved",
                    "change_summary": "Verified CTRI registration public dossier record.",
                    "size_kb": 540
                }
            ]
        },
        {
            "doc_id": "DOC-CTR-002",
            "trial_ctri": "CTRI/2018/02/011783",
            "document_name": "CTRI Prospective Registration Certificate & Trial Details",
            "category": "CTRI",
            "current_version": "v1.0",
            "uploaded_by": "Dr. P. Gupta",
            "upload_date": "2026-02-14 12:30:00",
            "status": "Approved",
            "file_name": "CTRI_Certificate_011783.pdf",
            "security_classification": "Official Record",
            "description": "Prospective registration verification from CTRI public database.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "CTRI_Certificate_011783.pdf",
                    "uploaded_by": "Dr. P. Gupta",
                    "upload_date": "2026-02-14 12:30:00",
                    "status": "Approved",
                    "change_summary": "Official registration certificate.",
                    "size_kb": 512
                }
            ]
        },

        # 4. MONITORING
        {
            "doc_id": "DOC-MON-001",
            "trial_ctri": "CTRI/2017/10/010023",
            "document_name": "Interim Site Monitoring Visit Report (IMV-04)",
            "category": "Monitoring",
            "current_version": "v1.1",
            "uploaded_by": "S. Sharma, CRA",
            "upload_date": "2026-09-02 17:00:00",
            "status": "Approved",
            "file_name": "Monitoring_Report_IMV04_AIIA.pdf",
            "security_classification": "Institutional Confidential",
            "description": "Routine quarterly CRA monitoring report confirming 100% Source Document Verification on primary outcomes.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "Monitoring_Report_IMV04_Draft.pdf",
                    "uploaded_by": "S. Sharma, CRA",
                    "upload_date": "2026-08-28 16:00:00",
                    "status": "Superseded",
                    "change_summary": "Draft visit findings submitted for PI acknowledgement.",
                    "size_kb": 1150
                },
                {
                    "version": "v1.1",
                    "file_name": "Monitoring_Report_IMV04_AIIA.pdf",
                    "uploaded_by": "S. Sharma, CRA",
                    "upload_date": "2026-09-02 17:00:00",
                    "status": "Approved",
                    "change_summary": "Final signed monitoring visit report with PI corrective action plan.",
                    "size_kb": 1280
                }
            ]
        },
        {
            "doc_id": "DOC-MON-002",
            "trial_ctri": "CTRI/2018/02/011783",
            "document_name": "Site Initiation & Readiness Verification Audit Log",
            "category": "Monitoring",
            "current_version": "v1.0",
            "uploaded_by": "S. Sharma, CRA",
            "upload_date": "2026-03-01 10:45:00",
            "status": "Approved",
            "file_name": "Site_Initiation_Audit_Log.pdf",
            "security_classification": "Institutional Confidential",
            "description": "Site readiness assessment, investigational product storage verification, and delegation of authority log.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "Site_Initiation_Audit_Log.pdf",
                    "uploaded_by": "S. Sharma, CRA",
                    "upload_date": "2026-03-01 10:45:00",
                    "status": "Approved",
                    "change_summary": "Site Initiation Visit signoff.",
                    "size_kb": 950
                }
            ]
        },

        # 5. SAFETY
        {
            "doc_id": "DOC-SAF-001",
            "trial_ctri": "CTRI/2017/10/010023",
            "document_name": "Data Safety Monitoring Board (DSMB) Interim Assessment Charter",
            "category": "Safety",
            "current_version": "v2.0",
            "uploaded_by": "Dr. A. Verma",
            "upload_date": "2026-08-30 14:10:00",
            "status": "Approved",
            "file_name": "DSMB_Charter_Assessment_v2.0.pdf",
            "security_classification": "Restricted - Regulatory Only",
            "description": "Independent DSMB formal safety review confirming unblinded safety stopping boundaries have not been breached.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "DSMB_Charter_v1.0.pdf",
                    "uploaded_by": "Dr. A. Verma",
                    "upload_date": "2025-11-15 09:30:00",
                    "status": "Superseded",
                    "change_summary": "Original DSMB operational charter.",
                    "size_kb": 1420
                },
                {
                    "version": "v2.0",
                    "file_name": "DSMB_Charter_Assessment_v2.0.pdf",
                    "uploaded_by": "Dr. A. Verma",
                    "upload_date": "2026-08-30 14:10:00",
                    "status": "Approved",
                    "change_summary": "Interim safety analysis milestone charter with updated stopping guidelines.",
                    "size_kb": 1680
                }
            ]
        },
        {
            "doc_id": "DOC-SAF-002",
            "trial_ctri": "CTRI/2018/02/011783",
            "document_name": "Expedited SAE Narrative & Causality Dossier (SAE-2026-09)",
            "category": "Safety",
            "current_version": "v1.0",
            "uploaded_by": "Dr. A. Verma",
            "upload_date": "2026-09-12 11:00:00",
            "status": "Approved",
            "file_name": "SAE_Expedited_Dossier_2026_09.pdf",
            "security_classification": "Restricted - Regulatory Only",
            "description": "15-day expedited reporting narrative submitted to CDSCO and Institutional Ethics Committee.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "SAE_Expedited_Dossier_2026_09.pdf",
                    "uploaded_by": "Dr. A. Verma",
                    "upload_date": "2026-09-12 11:00:00",
                    "status": "Approved",
                    "change_summary": "Initial expedited safety report submission.",
                    "size_kb": 890
                }
            ]
        },

        # 6. REPORTS
        {
            "doc_id": "DOC-REP-001",
            "trial_ctri": "CTRI/2017/10/010023",
            "document_name": "Interim Clinical Study Performance & Statistical Summary Report",
            "category": "Reports",
            "current_version": "v1.1",
            "uploaded_by": "Prof. (Dr.) Tanuja Nesari",
            "upload_date": "2026-09-01 15:30:00",
            "status": "Approved",
            "file_name": "Interim_Study_Performance_Report_2026.pdf",
            "security_classification": "Official Record",
            "description": "Annual institutional clinical research progress report presented to Ministry of AYUSH & Scientific Advisory Board.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "Interim_Study_Performance_Report_Draft.pdf",
                    "uploaded_by": "Prof. (Dr.) Tanuja Nesari",
                    "upload_date": "2026-08-15 10:00:00",
                    "status": "Superseded",
                    "change_summary": "Draft report for internal scientific committee review.",
                    "size_kb": 3100
                },
                {
                    "version": "v1.1",
                    "file_name": "Interim_Study_Performance_Report_2026.pdf",
                    "uploaded_by": "Prof. (Dr.) Tanuja Nesari",
                    "upload_date": "2026-09-01 15:30:00",
                    "status": "Approved",
                    "change_summary": "Final approved institutional publication version.",
                    "size_kb": 3340
                }
            ]
        },
        {
            "doc_id": "DOC-REP-002",
            "trial_ctri": "CTRI/2018/02/011783",
            "document_name": "Institutional Pharmacovigilance Annual Aggregate Safety Summary",
            "category": "Reports",
            "current_version": "v1.0",
            "uploaded_by": "Dr. A. Verma",
            "upload_date": "2026-09-10 16:20:00",
            "status": "Approved",
            "file_name": "Annual_Aggregate_Safety_Summary_2026.pdf",
            "security_classification": "Official Record",
            "description": "Annual comprehensive safety signal analysis across all ongoing Ayurvedic interventional trials.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": "Annual_Aggregate_Safety_Summary_2026.pdf",
                    "uploaded_by": "Dr. A. Verma",
                    "upload_date": "2026-09-10 16:20:00",
                    "status": "Approved",
                    "change_summary": "Annual aggregate safety compilation.",
                    "size_kb": 2180
                }
            ]
        }
    ]

    for doc in doc_seeds:
        # Check if trial exists
        c.execute("SELECT id FROM trials WHERE ctri_number = ?", (doc["trial_ctri"],))
        t_row = c.fetchone()
        trial_id = t_row["id"] if t_row else 1

        # Create physical dummy file in secure_documents storage
        physical_path = os.path.join(storage_dir, doc["file_name"])
        dummy_content = f"""ALL INDIA INSTITUTE OF AYURVEDA (AIIA)
OFFICIAL INSTITUTIONAL CLINICAL TRIAL DOCUMENT
============================================================
Document ID:     {doc['doc_id']}
Title:           {doc['document_name']}
Category:        {doc['category']}
CTRI Reference:  {doc['trial_ctri']}
Current Version: {doc['current_version']}
Status:          {doc['status']}
Uploaded By:     {doc['uploaded_by']}
Upload Date:     {doc['upload_date']}
Classification:  {doc['security_classification']}
============================================================
DESCRIPTION / SUMMARY:
{doc['description']}

SECURITY NOTICE:
This document is an official institutional record of the All India Institute of Ayurveda.
Unauthorized reproduction, distribution, or alteration is strictly prohibited.
Electronic audit trails are cryptographically maintained for all access and download operations.
"""
        with open(physical_path, "w", encoding="utf-8") as f:
            f.write(dummy_content)

        file_size_kb = max(1, os.path.getsize(physical_path) // 1024)
        checksum = hashlib.sha256(dummy_content.encode("utf-8")).hexdigest()

        # Insert main document record
        c.execute("""
            INSERT INTO documents (
                doc_id, trial_id, trial_ctri, document_name, category,
                current_version, uploaded_by, upload_date, status,
                file_name, file_path, file_size_kb, checksum_sha256,
                security_classification, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc["doc_id"], trial_id, doc["trial_ctri"], doc["document_name"], doc["category"],
            doc["current_version"], doc["uploaded_by"], doc["upload_date"], doc["status"],
            doc["file_name"], physical_path, file_size_kb, checksum,
            doc["security_classification"], doc["description"]
        ))
        document_db_id = c.lastrowid

        # Insert historical version records
        for v in doc["versions"]:
            v_path = os.path.join(storage_dir, v["file_name"])
            if not os.path.exists(v_path):
                v_content = f"AIIA Document {doc['doc_id']} Version {v['version']}\n{v['change_summary']}"
                with open(v_path, "w", encoding="utf-8") as vf:
                    vf.write(v_content)
                v_checksum = hashlib.sha256(v_content.encode("utf-8")).hexdigest()
            else:
                with open(v_path, "r", encoding="utf-8") as vf:
                    v_content = vf.read()
                v_checksum = hashlib.sha256(v_content.encode("utf-8")).hexdigest()

            c.execute("""
                INSERT INTO document_versions (
                    document_id, version, file_name, file_path, file_size_kb,
                    checksum_sha256, uploaded_by, upload_date, status, change_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_db_id, v["version"], v["file_name"], v_path,
                v.get("size_kb", file_size_kb), v_checksum, v["uploaded_by"],
                v["upload_date"], v["status"], v["change_summary"]
            ))

    conn.commit()
    conn.close()
    print("Documents and Document Versions tables seeded with physical secure storage files.")

if __name__ == "__main__":
    init_documents_and_storage()
