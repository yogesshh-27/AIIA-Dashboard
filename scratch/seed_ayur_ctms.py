"""
AYURCTMS Schema Definition and Seeding Engine for AIIA Clinical Trial Management System.
Implements the 28 core requirements of Smart India Hackathon Problem Statement 26046.
"""

import sqlite3
import os
import json
import datetime
import hashlib

APP_DB_PATH = "aiia_app.db"

def get_db():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_ayur_tables():
    conn = get_db()
    c = conn.cursor()

    # 1. Doctors Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        avatar TEXT,
        qualification TEXT NOT NULL,
        specialization TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        current_site TEXT NOT NULL,
        trial_id TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        email TEXT,
        phone TEXT,
        bio TEXT
    )
    """)

    # 2. Trials Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_trials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trial_id TEXT UNIQUE NOT NULL,
        trial_name TEXT NOT NULL,
        condition TEXT NOT NULL,
        intervention TEXT NOT NULL,
        description TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        pi_name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        duration_weeks INTEGER NOT NULL,
        target_participants INTEGER NOT NULL,
        enrolled_participants INTEGER NOT NULL,
        recruitment_status TEXT NOT NULL,
        trial_status TEXT NOT NULL,
        eligibility_criteria TEXT,
        exclusion_criteria TEXT,
        ethics_approval_status TEXT NOT NULL DEFAULT 'Approved',
        ctri_registration_status TEXT NOT NULL DEFAULT 'Registered',
        regulatory_status TEXT NOT NULL DEFAULT 'Approved',
        progress_pct INTEGER NOT NULL DEFAULT 0,
        outcome_metric_name TEXT,
        outcome_metric_value TEXT
    )
    """)

    # 3. Sites / Locations Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT UNIQUE NOT NULL,
        city TEXT UNIQUE NOT NULL,
        hospital_name TEXT NOT NULL,
        state TEXT NOT NULL,
        condition TEXT NOT NULL,
        pi_name TEXT NOT NULL,
        trial_id TEXT NOT NULL,
        duration_weeks INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        status TEXT NOT NULL,
        participants_enrolled INTEGER NOT NULL,
        participants_target INTEGER NOT NULL,
        progress_pct INTEGER NOT NULL,
        doctor_name TEXT NOT NULL,
        coordinator_name TEXT NOT NULL,
        pending_issues TEXT,
        outcome_trend_json TEXT
    )
    """)

    # 4. Patients Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        condition TEXT NOT NULL,
        area_city TEXT NOT NULL,
        state TEXT NOT NULL,
        assigned_trial_id TEXT NOT NULL,
        treatment_site TEXT NOT NULL,
        assigned_doctor_name TEXT NOT NULL,
        treatment_status TEXT NOT NULL,
        treatment_duration TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        contact_info TEXT,
        accessibility_needs TEXT,
        registration_date TEXT NOT NULL
    )
    """)

    # 5. Treatment Stages (8-Stage Clinical Flow)
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_patient_treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        stage_key TEXT NOT NULL,
        stage_title TEXT NOT NULL,
        stage_order INTEGER NOT NULL,
        date_recorded TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_doctor_name TEXT NOT NULL,
        dosage_frequency TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES ayur_patients(patient_id)
    )
    """)

    # 6. Adverse Events Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_adverse_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        patient_id TEXT NOT NULL,
        patient_name TEXT NOT NULL,
        trial_id TEXT NOT NULL,
        condition TEXT NOT NULL,
        location TEXT NOT NULL,
        adverse_event TEXT NOT NULL,
        severity TEXT NOT NULL,
        serious TEXT NOT NULL DEFAULT 'No',
        suspected_treatment TEXT NOT NULL,
        date_reported TEXT NOT NULL,
        action_taken TEXT,
        outcome TEXT,
        reported_by TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Reported'
    )
    """)

    # 7. Safety Signals Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_safety_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id TEXT UNIQUE NOT NULL,
        trial_id TEXT NOT NULL,
        condition TEXT NOT NULL,
        adverse_event_type TEXT NOT NULL,
        reported_count INTEGER NOT NULL,
        threshold INTEGER NOT NULL,
        date_detected TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active Signal',
        recommendation TEXT NOT NULL
    )
    """)

    # 8. Approvals Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        approval_id TEXT UNIQUE NOT NULL,
        trial_id TEXT NOT NULL,
        city TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        approval_type TEXT NOT NULL,
        status TEXT NOT NULL,
        submission_date TEXT NOT NULL,
        decision_date TEXT,
        reviewer_notes TEXT,
        action_required TEXT
    )
    """)

    # 9. GCP Guidelines Checklist Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_gcp_checklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        is_completed INTEGER NOT NULL DEFAULT 1,
        last_reviewed TEXT NOT NULL,
        reviewed_by TEXT NOT NULL,
        category TEXT NOT NULL
    )
    """)

    # 10. Notifications Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        notification_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        severity TEXT NOT NULL,
        target_route TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # 11. Audit Trail Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS ayur_audit_trail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id TEXT UNIQUE NOT NULL,
        user_name TEXT NOT NULL,
        action TEXT NOT NULL,
        module TEXT NOT NULL,
        previous_value TEXT,
        new_value TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def seed_ayur_data():
    conn = get_db()
    c = conn.cursor()

    # Clear existing to ensure clean seed
    for tbl in ['ayur_doctors', 'ayur_trials', 'ayur_sites', 'ayur_patients', 
                'ayur_patient_treatments', 'ayur_adverse_events', 'ayur_safety_signals',
                'ayur_approvals', 'ayur_gcp_checklist', 'ayur_notifications', 'ayur_audit_trail']:
        c.execute(f"DELETE FROM {tbl}")

    # -------------------------------------------------------------
    # 1. SEED DOCTORS (11 Doctors)
    # -------------------------------------------------------------
    doctors = [
        ('DOC-001', 'Dr. Ananya Sharma', 'AS', 'MD, Ayurveda', 'Kayachikitsa', 8, 'Mumbai', 'AYU-TRIAL-001', 'Principal Investigator', 'Active', 'ananya.sharma@aiia.gov.in', '+91 98201 44512', 'Specialist in chronic musculoskeletal disorders and classical Ayurvedic formulation kinetics.'),
        ('DOC-002', 'Dr. Galib', 'DG', 'MD, PhD, Ayurveda', 'Rasashastra & Bhaishajya Kalpana', 15, 'Delhi', 'AYU-TRIAL-002', 'Principal Investigator', 'Active', 'dr.galib@aiia.gov.in', '+91 98112 33490', 'Associate Professor and lead investigator for metabolic & endocrine Ayurvedic clinical trials at AIIA.'),
        ('DOC-003', 'Dr. Soumya Roy', 'SR', 'MD, Ayurveda', 'Dravyaguna', 10, 'Kolkata', 'AYU-TRIAL-003', 'Principal Investigator', 'Active', 'soumya.roy@aiia.gov.in', '+91 98302 99182', 'Expert in clinical phytopharmacology and therapeutic evaluation of dermatological Ayurvedic compounds.'),
        ('DOC-004', 'Dr. Rajesh K. Nair', 'RN', 'MD, Ayurveda', 'Kayachikitsa & Panchakarma', 14, 'Kerala', 'AYU-TRIAL-004', 'Principal Investigator', 'Active', 'rajesh.nair@aiia.gov.in', '+91 94471 28910', 'Senior physician specializing in cardiovascular autonomic regulation through classical Ayurvedic Shirodhara protocols.'),
        ('DOC-005', 'Dr. Akhilesh Mishra', 'AM', 'MS, Ayurveda', 'Shalya Tantra', 11, 'Lucknow', 'AYU-TRIAL-005', 'Principal Investigator', 'Active', 'akhilesh.mishra@aiia.gov.in', '+91 94150 11920', 'Gastrointestinal disorders and surgical recovery protocols utilizing specialized Takradhara and herbal gutikas.'),
        ('DOC-006', 'Dr. Vandana Joshi', 'VJ', 'MD, Ayurveda', 'Panchakarma', 12, 'Jaipur', 'AYU-TRIAL-006', 'Principal Investigator', 'Active', 'vandana.joshi@aiia.gov.in', '+91 98290 88219', 'Principal investigator for neuropsychiatric sleep and stress management clinical trials.'),
        ('DOC-007', 'Dr. Harish Chandra', 'HC', 'MS, Ayurveda', 'Shalakya Tantra', 9, 'Noida', 'AYU-TRIAL-007', 'Principal Investigator', 'Active', 'harish.chandra@aiia.gov.in', '+91 98188 77210', 'Specialist in upper respiratory tract, ENT, and sinus disorders.'),
        ('DOC-008', 'Dr. K. Venkat Rao', 'VR', 'MD, Ayurveda', 'Kayachikitsa', 13, 'Hyderabad', 'AYU-TRIAL-008', 'Principal Investigator', 'Active', 'venkat.rao@aiia.gov.in', '+91 98480 33910', 'Metabolic syndrome and dyslipidemia clinical research lead.'),
        ('DOC-009', 'Dr. Deepa Nambiar', 'DN', 'MD, Ayurveda', 'Kaumarbhritya & Rasayana', 7, 'Bengaluru', 'AYU-TRIAL-009', 'Principal Investigator', 'Active', 'deepa.nambiar@aiia.gov.in', '+91 98801 55670', 'Geriatric cognitive health and Medhya Rasayana clinical researcher.'),
        ('DOC-010', 'Dr. A. Verma', 'AV', 'MD, Ayurveda', 'Pharmacovigilance & Dravyaguna', 16, 'Delhi', 'Institutional General', 'Central Pharmacovigilance Officer', 'Active', 'a.verma@aiia.gov.in', '+91 98101 22918', 'National coordinator for adverse drug event monitoring and Ayurvedic safety signal detection.'),
        ('DOC-011', 'Dr. K. S. Dhiman', 'KD', 'MD, PhD', 'Institutional Governance', 20, 'Delhi', 'Institutional General', 'Ethics Committee Chair', 'Active', 'ks.dhiman@aiia.gov.in', '+91 98100 00192', 'Head of AIIA Institutional Ethics Committee and regulatory compliance coordinator.')
    ]
    c.executemany("""
    INSERT INTO ayur_doctors (doctor_id, name, avatar, qualification, specialization, experience_years, current_site, trial_id, role, status, email, phone, bio)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, doctors)

    # -------------------------------------------------------------
    # 2. SEED TRIALS (8 Trials including specific demo scenarios)
    # -------------------------------------------------------------
    trials = [
        ('AYU-TRIAL-001', 'Clinical Evaluation of Shallaki & Guggulu Extract in Osteoarthritis of Knee', 'Arthritis', 'Shallaki (Boswellia serrata) & Guggulu (Commiphora mukul) 500mg BD', 'A randomized, double-blind, active-controlled trial evaluating pain scores (VAS) and joint mobility over 12 weeks in primary knee osteoarthritis.', 'AIIA Partner Clinical Site - Mumbai', 'Mumbai', 'Maharashtra', 'Dr. Ananya Sharma', '2026-06-01', '2026-08-24', 12, 150, 120, 'Recruiting', 'Ongoing', 'Age 40-70, Diagnosed primary knee osteoarthritis Grade II/III on Kellgren-Lawrence scale.', 'Secondary osteoarthritis, severe renal impairment, systemic steroid therapy within 30 days.', 'Approved', 'Registered', 'Approved', 80, 'Pain Score (VAS) Reduction', '48% Decrease (7.2 → 3.7)'),
        ('AYU-TRIAL-002', 'Evaluation of Nishamalaki and Madhumehantak Formulation in Type 2 Diabetes Mellitus', 'Diabetes', 'Nishamalaki (Curcuma longa + Emblica officinalis) & Madhumehantak Tab', 'Randomized controlled clinical investigation on glycaemic control, fasting plasma glucose, and HbA1c trajectory in newly diagnosed Type 2 Diabetes.', 'AIIA Main Research Hospital - New Delhi', 'Delhi', 'Delhi', 'Dr. Galib', '2026-05-15', '2026-09-05', 16, 120, 95, 'Recruiting', 'Ongoing', 'Age 30-65, Diagnosed T2DM with HbA1c between 7.0% and 9.5%, drug-naive or metformin-tolerant.', 'Type 1 diabetes, diabetic ketoacidosis, serum creatinine > 1.8 mg/dL, pregnancy.', 'Approved', 'Registered', 'Approved', 79, 'Mean HbA1c Reduction', '1.2% Reduction (8.4% → 7.2%)'),
        ('AYU-TRIAL-003', 'Efficacy of Neem-Manjistha-Khadira Compound in Acne Vulgaris (Yuvanpidika)', 'Acne', 'Neem, Manjistha & Khadira Purified Extract (Oral BD + Topical Lepa)', 'Open-label prospective interventional study on facial inflammatory lesion counts and sebum production in Grade II/III Acne Vulgaris.', 'National Institute of Ayurveda Clinical Research Facility - Kolkata', 'Kolkata', 'West Bengal', 'Dr. Soumya Roy', '2026-07-01', '2026-08-26', 8, 80, 65, 'Recruiting', 'Ongoing', 'Age 16-30, Facial acne vulgaris Grade II/III on Global Acne Grading System (GAGS).', 'Nodulocystic acne Grade IV, oral isotretinoin usage within 6 months, hormonal contraception.', 'Approved', 'Registered', 'Approved', 81, 'GAGS Severity Score', '54% Score Improvement'),
        ('AYU-TRIAL-004', 'Comparative Study of Sarpagandha Ghanavati and Mukta Vati in Essential Hypertension', 'Hypertension', 'Sarpagandha Ghanavati (250mg) & Shirodhara Protocol', 'Multi-arm double-blind trial evaluating systolic and diastolic blood pressure modulation and autonomic tone over 14 weeks.', 'Government Ayurveda Research Institute - Thiruvananthapuram', 'Kerala', 'Kerala', 'Dr. Rajesh K. Nair', '2026-10-01', '2027-01-15', 14, 100, 0, 'Pending Approval', 'Pending Approval', 'Age 35-65, Stage 1 Essential Hypertension (SBP 140-159 mmHg, DBP 90-99 mmHg).', 'Secondary hypertension, history of stroke/myocardial infarction, severe bradycardia.', 'Pending', 'Submitted', 'Pending', 0, 'Target SBP/DBP Modulation', 'Target: -12 mmHg SBP'),
        ('AYU-TRIAL-005', 'Multi-center Evaluation of Bilwadi Gutika and Takradhara in Irritable Bowel Syndrome', 'Digestive Disorder', 'Bilwadi Gutika (500mg TDS) & Medicated Takradhara', 'Comparative randomized evaluation of stool frequency, abdominal discomfort, and IBS-QoL score in Grahani Roga.', 'State Ayurvedic College & Research Hospital - Lucknow', 'Lucknow', 'Uttar Pradesh', 'Dr. Akhilesh Mishra', '2026-10-15', '2026-12-24', 10, 90, 0, 'Upcoming', 'Upcoming', 'Age 20-55, Diagnosed IBS according to Rome IV criteria.', 'Inflammatory bowel disease (Crohn/Ulcerative Colitis), gastrointestinal bleeding, history of bowel surgery.', 'Approved', 'Registered', 'Approved', 0, 'IBS-Symptom Severity Score', 'Scheduled Protocol'),
        ('AYU-TRIAL-006', 'Clinical Evaluation of Ashwagandha (Withania somnifera) Extract in Chronic Insomnia and Fatigue', 'Stress/Fatigue', 'Standardized Withania somnifera Root Extract (300mg BD)', 'Placebo-controlled double-blind trial assessing sleep onset latency, total sleep time, and morning alertness via actigraphy and PSQI.', 'National Institute of Ayurveda Hospital - Jaipur', 'Jaipur', 'Rajasthan', 'Dr. Vandana Joshi', '2026-01-01', '2026-03-26', 12, 100, 100, 'Closed', 'Completed', 'Age 25-60, Diagnosed primary insomnia with PSQI score > 8.', 'Sleep apnea, psychiatric comorbidity, sedative/hypnotic drug dependence within 3 months.', 'Approved', 'Registered', 'Approved', 100, 'PSQI Sleep Quality Index', '62% Score Improvement (Concluded)'),
        ('AYU-TRIAL-007', 'Standardized Shadbindu Taila Nasya in Chronic Sinusitis (Dushta Pratishyaya)', 'Sinusitis', 'Shadbindu Taila (6 drops each nostril) with Steam Inhalation', 'Single-blind interventional trial evaluating nasal obstruction, headache, and mucociliary clearance in chronic rhinosinusitis.', 'AIIA Extension Clinical Center - Noida', 'Noida', 'Uttar Pradesh', 'Dr. Harish Chandra', '2026-06-15', '2026-09-15', 12, 60, 45, 'Recruiting', 'Ongoing', 'Age 18-55, Persistent chronic sinusitis symptoms > 12 weeks with radiographic confirmation.', 'Nasal polyposis requiring surgery, deviated septum Grade III, acute bacterial infection.', 'Approved', 'Registered', 'Approved', 75, 'SNOT-22 Score Improvement', '45% Symptom Reduction'),
        ('AYU-TRIAL-008', 'Metabolic Efficacy of Triphala-Guggulu & Vrikshamla in Obesity (Medoroga)', 'Obesity', 'Triphala-Guggulu & Vrikshamla (Garcinia indica) 1g BD with Warm Water', 'Randomized parallel-group trial on body mass index, waist-hip ratio, and lipid profile in Grade I/II obesity.', 'Government Ayurvedic Hospital & Research Centre - Hyderabad', 'Hyderabad', 'Telangana', 'Dr. K. Venkat Rao', '2026-04-01', '2026-09-30', 24, 120, 70, 'Recruiting', 'Ongoing', 'Age 20-50, BMI 27.5 - 34.9 kg/m2 with waist circumference > 90cm (M) / > 80cm (F).', 'Endocrine obesity (Cushing, severe hypothyroidism), bariatric surgery candidate.', 'Approved', 'Registered', 'Approved', 58, 'Body Weight & Lipid Profile', 'Average 5.4 kg Weight Loss')
    ]
    c.executemany("""
    INSERT INTO ayur_trials (trial_id, trial_name, condition, intervention, description, hospital_name, city, state, pi_name, start_date, end_date, duration_weeks, target_participants, enrolled_participants, recruitment_status, trial_status, eligibility_criteria, exclusion_criteria, ethics_approval_status, ctri_registration_status, regulatory_status, progress_pct, outcome_metric_name, outcome_metric_value)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trials)

    # -------------------------------------------------------------
    # 3. SEED SITES / LOCATIONS (9 Major Indian Cities)
    # -------------------------------------------------------------
    sites = [
        ('SITE-MUM', 'Mumbai', 'AIIA Partner Clinical Site - Mumbai', 'Maharashtra', 'Arthritis', 'Dr. Ananya Sharma', 'AYU-TRIAL-001', 12, '2026-06-01', '2026-08-24', 'Ongoing', 120, 150, 80, 'Dr. Ananya Sharma', 'Dr. Rahul Mehra, CRA', 'None (On Schedule)', json.dumps([{"week": 0, "vas": 7.2}, {"week": 2, "vas": 6.8}, {"week": 4, "vas": 5.9}, {"week": 6, "vas": 4.8}, {"week": 8, "vas": 3.7}])),
        ('SITE-DEL', 'Delhi', 'AIIA Main Research Hospital - New Delhi', 'Delhi', 'Diabetes', 'Dr. Galib', 'AYU-TRIAL-002', 16, '2026-05-15', '2026-09-05', 'Ongoing', 95, 120, 79, 'Dr. Galib', 'Dr. Priyanshu Gupta, CRA', 'Cluster of 7 mild skin rash cases reported (under PV review)', json.dumps([{"week": 0, "hba1c": 8.4}, {"week": 4, "hba1c": 8.1}, {"week": 8, "hba1c": 7.7}, {"week": 12, "hba1c": 7.3}, {"week": 16, "hba1c": 7.2}])),
        ('SITE-KOL', 'Kolkata', 'National Institute of Ayurveda Facility - Kolkata', 'West Bengal', 'Acne', 'Dr. Soumya Roy', 'AYU-TRIAL-003', 8, '2026-07-01', '2026-08-26', 'Ongoing', 65, 80, 81, 'Dr. Soumya Roy', 'S. Banerjee, CRA', 'Minor batch supply delay resolved in Week 3', json.dumps([{"week": 0, "gags": 28}, {"week": 2, "gags": 24}, {"week": 4, "gags": 19}, {"week": 6, "gags": 15}, {"week": 8, "gags": 13}])),
        ('SITE-KER', 'Kerala', 'Government Ayurveda Research Institute - Thiruvananthapuram', 'Kerala', 'Hypertension', 'Dr. Rajesh K. Nair', 'AYU-TRIAL-004', 14, '2026-10-01', '2027-01-15', 'Pending Approval', 0, 100, 0, 'Dr. Rajesh K. Nair', 'Meera V., CRA', 'Regulatory clearance endorsement pending with state ethics board', json.dumps([])),
        ('SITE-LKO', 'Lucknow', 'State Ayurvedic College & Research Hospital - Lucknow', 'Uttar Pradesh', 'Digestive Disorder', 'Dr. Akhilesh Mishra', 'AYU-TRIAL-005', 10, '2026-10-15', '2026-12-24', 'Upcoming', 0, 90, 0, 'Dr. Akhilesh Mishra', 'R. K. Shukla, CRA', 'Pre-study site initiation visit scheduled for next week', json.dumps([])),
        ('SITE-JAI', 'Jaipur', 'National Institute of Ayurveda Hospital - Jaipur', 'Rajasthan', 'Stress/Fatigue', 'Dr. Vandana Joshi', 'AYU-TRIAL-006', 12, '2026-01-01', '2026-03-26', 'Completed', 100, 100, 100, 'Dr. Vandana Joshi', 'Pooja Rathore, CRA', 'Study concluded. Final study report locked and archived.', json.dumps([{"week": 0, "psqi": 14.2}, {"week": 4, "psqi": 10.8}, {"week": 8, "psqi": 7.4}, {"week": 12, "psqi": 5.4}])),
        ('SITE-NOI', 'Noida', 'AIIA Extension Clinical Center - Noida', 'Uttar Pradesh', 'Sinusitis', 'Dr. Harish Chandra', 'AYU-TRIAL-007', 12, '2026-06-15', '2026-09-15', 'Ongoing', 45, 60, 75, 'Dr. Harish Chandra', 'S. Saxena, CRA', 'Site running smoothly with 98% participant retention', json.dumps([{"week": 0, "snot": 42}, {"week": 4, "snot": 33}, {"week": 8, "snot": 26}, {"week": 12, "snot": 23}])),
        ('SITE-HYD', 'Hyderabad', 'Government Ayurvedic Hospital & Research Centre - Hyderabad', 'Telangana', 'Obesity', 'Dr. K. Venkat Rao', 'AYU-TRIAL-008', 24, '2026-04-01', '2026-09-30', 'Ongoing', 70, 120, 58, 'Dr. K. Venkat Rao', 'N. Reddy, CRA', 'Mid-term diet adherence monitoring underway', json.dumps([{"month": 0, "weight": 88.5}, {"month": 1, "weight": 86.8}, {"month": 2, "weight": 85.1}, {"month": 3, "weight": 83.1}])),
        ('SITE-BLR', 'Bengaluru', 'AIIA Regional Ayurvedic Clinical Unit - Bengaluru', 'Karnataka', 'Memory Impairment', 'Dr. Deepa Nambiar', 'AYU-TRIAL-009', 16, '2026-07-10', '2026-11-10', 'Recruiting', 30, 80, 38, 'Dr. Deepa Nambiar', 'K. Murthy, CRA', 'Subject intake active at memory wellness OPD', json.dumps([{"week": 0, "mmse": 23.1}, {"week": 4, "mmse": 24.5}]))
    ]
    c.executemany("""
    INSERT INTO ayur_sites (site_id, city, hospital_name, state, condition, pi_name, trial_id, duration_weeks, start_date, end_date, status, participants_enrolled, participants_target, progress_pct, doctor_name, coordinator_name, pending_issues, outcome_trend_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sites)

    # -------------------------------------------------------------
    # 4. SEED PATIENTS (25+ Patients with Ramlal Scenario in Delhi)
    # -------------------------------------------------------------
    patients = [
        # Ramlal (Section 17 & 23 requirement)
        ('AYU-PAT-001', 'Ramlal Sharma', 54, 'Male', 'Diabetes', 'Delhi', 'Delhi', 'AYU-TRIAL-002', 'AIIA Main Research Hospital - New Delhi', 'Dr. Galib', 'Active (Under PV Review)', '16 Weeks', 'Active', 'ramlal.sharma@example.com / +91 98110 99821', 'None', '2026-05-18'),
        # Delhi diabetes cohort
        ('AYU-PAT-002', 'Sunita Devi', 48, 'Female', 'Diabetes', 'Delhi', 'Delhi', 'AYU-TRIAL-002', 'AIIA Main Research Hospital - New Delhi', 'Dr. Galib', 'Treatment Ongoing', '16 Weeks', 'Active', 'sunita.d@example.com', 'None', '2026-05-20'),
        ('AYU-PAT-003', 'Rajesh Kumar Verma', 59, 'Male', 'Diabetes', 'Delhi', 'Delhi', 'AYU-TRIAL-002', 'AIIA Main Research Hospital - New Delhi', 'Dr. Galib', 'Treatment Ongoing', '16 Weeks', 'Active', 'rajesh.v@example.com', 'Walking stick needed', '2026-05-22'),
        ('AYU-PAT-004', 'Meena Aggarwal', 51, 'Female', 'Diabetes', 'Delhi', 'Delhi', 'AYU-TRIAL-002', 'AIIA Main Research Hospital - New Delhi', 'Dr. Galib', 'Treatment Ongoing', '16 Weeks', 'Active', 'meena.agg@example.com', 'None', '2026-05-25'),
        ('AYU-PAT-005', 'Vikram Singh', 62, 'Male', 'Diabetes', 'Delhi', 'Delhi', 'AYU-TRIAL-002', 'AIIA Main Research Hospital - New Delhi', 'Dr. Galib', 'Treatment Ongoing', '16 Weeks', 'Active', 'vikram.s@example.com', 'None', '2026-06-01'),

        # Mumbai Arthritis cohort
        ('AYU-PAT-006', 'Shanti Patel', 58, 'Female', 'Arthritis', 'Mumbai', 'Maharashtra', 'AYU-TRIAL-001', 'AIIA Partner Clinical Site - Mumbai', 'Dr. Ananya Sharma', 'Treatment Ongoing', '12 Weeks', 'Active', 'shanti.p@example.com', 'Elevator access preferred', '2026-06-02'),
        ('AYU-PAT-007', 'Ganesh Kulkarni', 65, 'Male', 'Arthritis', 'Mumbai', 'Maharashtra', 'AYU-TRIAL-001', 'AIIA Partner Clinical Site - Mumbai', 'Dr. Ananya Sharma', 'Treatment Ongoing', '12 Weeks', 'Active', 'ganesh.k@example.com', 'Wheelchair support', '2026-06-04'),
        ('AYU-PAT-008', 'Kavita Deshmukh', 52, 'Female', 'Arthritis', 'Mumbai', 'Maharashtra', 'AYU-TRIAL-001', 'AIIA Partner Clinical Site - Mumbai', 'Dr. Ananya Sharma', 'Treatment Ongoing', '12 Weeks', 'Active', 'kavita.d@example.com', 'None', '2026-06-05'),
        ('AYU-PAT-009', 'Nitin Joshi', 49, 'Male', 'Arthritis', 'Mumbai', 'Maharashtra', 'AYU-TRIAL-001', 'AIIA Partner Clinical Site - Mumbai', 'Dr. Ananya Sharma', 'Treatment Ongoing', '12 Weeks', 'Active', 'nitin.j@example.com', 'None', '2026-06-10'),

        # Kolkata Acne cohort
        ('AYU-PAT-010', 'Pooja Mukherjee', 22, 'Female', 'Acne', 'Kolkata', 'West Bengal', 'AYU-TRIAL-003', 'National Institute of Ayurveda Facility - Kolkata', 'Dr. Soumya Roy', 'Treatment Ongoing', '8 Weeks', 'Active', 'pooja.m@example.com', 'None', '2026-07-02'),
        ('AYU-PAT-011', 'Anirban Sen', 25, 'Male', 'Acne', 'Kolkata', 'West Bengal', 'AYU-TRIAL-003', 'National Institute of Ayurveda Facility - Kolkata', 'Dr. Soumya Roy', 'Treatment Ongoing', '8 Weeks', 'Active', 'anirban.s@example.com', 'None', '2026-07-03'),
        ('AYU-PAT-012', 'Deblina Ghosh', 19, 'Female', 'Acne', 'Kolkata', 'West Bengal', 'AYU-TRIAL-003', 'National Institute of Ayurveda Facility - Kolkata', 'Dr. Soumya Roy', 'Treatment Ongoing', '8 Weeks', 'Active', 'deblina.g@example.com', 'None', '2026-07-05'),

        # Jaipur Stress/Insomnia cohort (Completed)
        ('AYU-PAT-013', 'Mahesh Rathore', 42, 'Male', 'Stress/Fatigue', 'Jaipur', 'Rajasthan', 'AYU-TRIAL-006', 'National Institute of Ayurveda Hospital - Jaipur', 'Dr. Vandana Joshi', 'Completed', '12 Weeks', 'Completed', 'mahesh.r@example.com', 'None', '2026-01-05'),
        ('AYU-PAT-014', 'Rekha Sharma', 38, 'Female', 'Stress/Fatigue', 'Jaipur', 'Rajasthan', 'AYU-TRIAL-006', 'National Institute of Ayurveda Hospital - Jaipur', 'Dr. Vandana Joshi', 'Completed', '12 Weeks', 'Completed', 'rekha.s@example.com', 'None', '2026-01-06'),

        # Noida Sinusitis cohort
        ('AYU-PAT-015', 'Amitav Saxena', 34, 'Male', 'Sinusitis', 'Noida', 'Uttar Pradesh', 'AYU-TRIAL-007', 'AIIA Extension Clinical Center - Noida', 'Dr. Harish Chandra', 'Treatment Ongoing', '12 Weeks', 'Active', 'amitav.s@example.com', 'None', '2026-06-18'),
        ('AYU-PAT-016', 'Priyanka Dubey', 29, 'Female', 'Sinusitis', 'Noida', 'Uttar Pradesh', 'AYU-TRIAL-007', 'AIIA Extension Clinical Center - Noida', 'Dr. Harish Chandra', 'Treatment Ongoing', '12 Weeks', 'Active', 'priyanka.d@example.com', 'None', '2026-06-20'),

        # Hyderabad Obesity cohort
        ('AYU-PAT-017', 'K. Madhavan', 44, 'Male', 'Obesity', 'Hyderabad', 'Telangana', 'AYU-TRIAL-008', 'Government Ayurvedic Hospital - Hyderabad', 'Dr. K. Venkat Rao', 'Treatment Ongoing', '24 Weeks', 'Active', 'madhavan.k@example.com', 'None', '2026-04-05'),
        ('AYU-PAT-018', 'Swathi Reddy', 39, 'Female', 'Obesity', 'Hyderabad', 'Telangana', 'AYU-TRIAL-008', 'Government Ayurvedic Hospital - Hyderabad', 'Dr. K. Venkat Rao', 'Treatment Ongoing', '24 Weeks', 'Active', 'swathi.r@example.com', 'None', '2026-04-10'),

        # Prospective & Screening Patients across regions
        ('AYU-PAT-019', 'Vijay Krishnan', 56, 'Male', 'Hypertension', 'Kerala', 'Kerala', 'AYU-TRIAL-004', 'Government Ayurveda Research Institute - Thiruvananthapuram', 'Dr. Rajesh K. Nair', 'Screened (Awaiting Study Launch)', '14 Weeks', 'Pre-enrolled', 'vijay.k@example.com', 'None', '2026-08-10'),
        ('AYU-PAT-020', 'Deepika Pillai', 49, 'Female', 'Hypertension', 'Kerala', 'Kerala', 'AYU-TRIAL-004', 'Government Ayurveda Research Institute - Thiruvananthapuram', 'Dr. Rajesh K. Nair', 'Screened (Awaiting Study Launch)', '14 Weeks', 'Pre-enrolled', 'deepika.p@example.com', 'None', '2026-08-12'),
        ('AYU-PAT-021', 'Ramesh Chandra Tiwari', 47, 'Male', 'Digestive Disorder', 'Lucknow', 'Uttar Pradesh', 'AYU-TRIAL-005', 'State Ayurvedic College - Lucknow', 'Dr. Akhilesh Mishra', 'Pre-registered', '10 Weeks', 'Pre-enrolled', 'ramesh.t@example.com', 'None', '2026-08-15'),
        ('AYU-PAT-022', 'Alka Srivastava', 41, 'Female', 'Digestive Disorder', 'Lucknow', 'Uttar Pradesh', 'AYU-TRIAL-005', 'State Ayurvedic College - Lucknow', 'Dr. Akhilesh Mishra', 'Pre-registered', '10 Weeks', 'Pre-enrolled', 'alka.s@example.com', 'None', '2026-08-18'),
        ('AYU-PAT-023', 'Narayana Swamy', 68, 'Male', 'Memory Impairment', 'Bengaluru', 'Karnataka', 'AYU-TRIAL-009', 'AIIA Regional Unit - Bengaluru', 'Dr. Deepa Nambiar', 'Treatment Ongoing', '16 Weeks', 'Active', 'n.swamy@example.com', 'Caregiver assisted', '2026-07-15'),
        ('AYU-PAT-024', 'Lalitha Hegde', 71, 'Female', 'Memory Impairment', 'Bengaluru', 'Karnataka', 'AYU-TRIAL-009', 'AIIA Regional Unit - Bengaluru', 'Dr. Deepa Nambiar', 'Treatment Ongoing', '16 Weeks', 'Active', 'lalitha.h@example.com', 'Caregiver assisted', '2026-07-20'),
        ('AYU-PAT-025', 'Harpreet Kaur', 36, 'Female', 'Arthritis', 'Delhi', 'Delhi', 'AYU-TRIAL-001', 'AIIA Main Research Hospital - New Delhi', 'Dr. Ananya Sharma', 'Active', '12 Weeks', 'Active', 'harpreet.k@example.com', 'None', '2026-06-15')
    ]
    c.executemany("""
    INSERT INTO ayur_patients (patient_id, full_name, age, gender, condition, area_city, state, assigned_trial_id, treatment_site, assigned_doctor_name, treatment_status, treatment_duration, status, contact_info, accessibility_needs, registration_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, patients)

    # -------------------------------------------------------------
    # 5. SEED 8-STAGE TREATMENT FLOW (For Ramlal & Others)
    # -------------------------------------------------------------
    stages = [
        ('AYU-PAT-001', 'REG', 'Registration & Consent', 1, '2026-05-18', 'Completed', 'Dr. Galib', 'N/A', 'Patient registered, Informed Consent Document (PIS/ICF) signed in Hindi.'),
        ('AYU-PAT-001', 'SCR', 'Clinical Screening', 2, '2026-05-20', 'Completed', 'Dr. Galib', 'N/A', 'Fasting Blood Sugar: 168 mg/dL, HbA1c: 8.6%, Blood Pressure: 128/82 mmHg. Inclusion criteria confirmed.'),
        ('AYU-PAT-001', 'BASE', 'Baseline Assessment', 3, '2026-05-24', 'Completed', 'Dr. Galib', 'N/A', 'Baseline lipid profile, renal panel, liver function, and Prakriti assessment (Vata-Pitta Pradhana).'),
        ('AYU-PAT-001', 'TREAT', 'Treatment Started', 4, '2026-05-25', 'Completed', 'Dr. Galib', 'Nishamalaki 500mg BD + Madhumehantak Tab 1 BD', 'Initial 30-day medication pack dispensed. Diary card provided for dose compliance.'),
        ('AYU-PAT-001', 'FU1', 'Follow-up Visit 1 (Week 4)', 5, '2026-06-25', 'Completed', 'Dr. Galib', 'Same dosage continued', 'FBS: 142 mg/dL. Good medication tolerance reported. 96% pill count compliance.'),
        ('AYU-PAT-001', 'FU2', 'Follow-up Visit 2 (Week 8)', 6, '2026-07-25', 'Completed', 'Dr. Galib', 'Same dosage continued', 'FBS: 130 mg/dL, HbA1c: 7.8%. Blood biochemistry within normal limits.'),
        ('AYU-PAT-001', 'FU3', 'Follow-up Visit 3 & PV Check (Week 12)', 7, '2026-09-18', 'Under PV Review', 'Dr. Galib / Dr. A. Verma', 'Dose Withheld Pending Review', 'Erythematous skin rash on both forearms reported 4 days prior. Adverse event recorded (AE-001). Shatadhauta Ghrita prescribed.'),
        ('AYU-PAT-001', 'OUT', 'Outcome Assessment', 8, '2026-09-24', 'Pending', 'Dr. Galib', 'TBD following safety clearance', 'Final glycemic index, safety resolution, and trial completion assessment.')
    ]
    c.executemany("""
    INSERT INTO ayur_patient_treatments (patient_id, stage_key, stage_title, stage_order, date_recorded, status, assigned_doctor_name, dosage_frequency, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, stages)

    # -------------------------------------------------------------
    # 6. SEED ADVERSE EVENTS (10+ Events including Ramlal & Cluster)
    # -------------------------------------------------------------
    events = [
        # Ramlal's adverse event
        ('AE-001', 'AYU-PAT-001', 'Ramlal Sharma', 'AYU-TRIAL-002', 'Diabetes', 'Delhi', 'Skin Rash', 'Moderate', 'No', 'Nishamalaki & Madhumehantak (Batch B-402)', '2026-09-18', 'Study medication temporarily withheld; topical Shatadhauta Ghrita applied; total eosinophil count ordered.', 'Condition recovering; erythema subsided by 70%.', 'Dr. Galib', 'Under Investigation'),
        # Other skin rash events in AYU-TRIAL-002 creating the Safety Signal cluster
        ('AE-002', 'AYU-PAT-002', 'Sunita Devi', 'AYU-TRIAL-002', 'Diabetes', 'Delhi', 'Mild Itching & Rash', 'Mild', 'No', 'Nishamalaki & Madhumehantak (Batch B-402)', '2026-09-15', 'Antihistaminic Ayurvedic topical lotion applied.', 'Resolved completely in 48 hours.', 'Dr. Galib', 'Resolved'),
        ('AE-003', 'AYU-PAT-003', 'Rajesh Kumar Verma', 'AYU-TRIAL-002', 'Diabetes', 'Delhi', 'Pruritus / Mild Rash', 'Mild', 'No', 'Nishamalaki & Madhumehantak (Batch B-402)', '2026-09-16', 'Observation and dosage timing shifted after meals.', 'Resolved.', 'Dr. Galib', 'Resolved'),
        ('AE-004', 'AYU-PAT-004', 'Meena Aggarwal', 'AYU-TRIAL-002', 'Diabetes', 'Delhi', 'Mild Macular Rash', 'Mild', 'No', 'Nishamalaki & Madhumehantak (Batch B-402)', '2026-09-17', 'Topical Chandana Lepa application.', 'Resolved.', 'Dr. Galib', 'Resolved'),
        ('AE-005', 'AYU-PAT-005', 'Vikram Singh', 'AYU-TRIAL-002', 'Diabetes', 'Delhi', 'Skin Itching (Forearm)', 'Mild', 'No', 'Nishamalaki & Madhumehantak (Batch B-402)', '2026-09-19', 'Dose compliance verified; batch sample sent for chemical assay.', 'Under Investigation', 'Dr. Galib', 'Under Investigation'),
        ('AE-006', 'AYU-PAT-006', 'Shanti Patel', 'AYU-TRIAL-001', 'Arthritis', 'Mumbai', 'Mild Gastric Irritation', 'Mild', 'No', 'Shallaki & Guggulu Extract', '2026-07-10', 'Instructed to consume medication with warm milk post-lunch.', 'Resolved within 2 days.', 'Dr. Ananya Sharma', 'Resolved'),
        ('AE-007', 'AYU-PAT-007', 'Ganesh Kulkarni', 'AYU-TRIAL-001', 'Arthritis', 'Mumbai', 'Nausea (Transient)', 'Mild', 'No', 'Shallaki & Guggulu Extract', '2026-07-14', 'Dose divided into twice daily with food.', 'Resolved.', 'Dr. Ananya Sharma', 'Resolved'),
        ('AE-008', 'AYU-PAT-010', 'Pooja Mukherjee', 'AYU-TRIAL-003', 'Acne', 'Kolkata', 'Topical Skin Dryness', 'Mild', 'No', 'Khadira Lepa Topical', '2026-07-20', 'Application duration reduced from 30 mins to 15 mins.', 'Resolved.', 'Dr. Soumya Roy', 'Resolved'),
        ('AE-009', 'AYU-PAT-015', 'Amitav Saxena', 'AYU-TRIAL-007', 'Sinusitis', 'Noida', 'Throat Irritation post Nasya', 'Mild', 'No', 'Shadbindu Taila Nasya', '2026-07-08', 'Kavala (warm saline gargle) administered post procedure.', 'Resolved.', 'Dr. Harish Chandra', 'Resolved'),
        ('AE-010', 'AYU-PAT-017', 'K. Madhavan', 'AYU-TRIAL-008', 'Obesity', 'Hyderabad', 'Abdominal Cramps', 'Mild', 'No', 'Triphala-Guggulu Compound', '2026-05-12', 'Dosage lowered for 3 days then titrated back.', 'Resolved.', 'Dr. K. Venkat Rao', 'Resolved')
    ]
    c.executemany("""
    INSERT INTO ayur_adverse_events (event_id, patient_id, patient_name, trial_id, condition, location, adverse_event, severity, serious, suspected_treatment, date_reported, action_taken, outcome, reported_by, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events)

    # -------------------------------------------------------------
    # 7. SEED SAFETY SIGNALS (Section 18 requirement)
    # -------------------------------------------------------------
    signals = [
        ('SIG-001', 'AYU-TRIAL-002', 'Diabetes', 'Skin Rash / Pruritus Cluster', 7, 3, '2026-09-20', 'Potential Safety Signal', '7 participants in AYU-002 (Delhi) have reported similar skin-related adverse events. Potential safety signal detected. Review by qualified pharmacovigilance personnel is recommended.')
    ]
    c.executemany("""
    INSERT INTO ayur_safety_signals (signal_id, trial_id, condition, adverse_event_type, reported_count, threshold, date_detected, status, recommendation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, signals)

    # -------------------------------------------------------------
    # 8. SEED APPROVALS (Section 12 requirement)
    # -------------------------------------------------------------
    approvals = [
        ('APP-001', 'AYU-TRIAL-001', 'Mumbai', 'AIIA Partner Site Mumbai', 'Ethics Approval', 'APPROVED', '2026-04-10', '2026-05-02', 'Full clearance granted by Institutional Ethics Committee.', 'None - Active'),
        ('APP-002', 'AYU-TRIAL-003', 'Kolkata', 'National Institute of Ayurveda Kolkata', 'Ethics Approval', 'APPROVED', '2026-05-12', '2026-06-04', 'Informed consent template and patient information sheet endorsed.', 'None - Active'),
        ('APP-003', 'AYU-TRIAL-004', 'Kerala', 'Govt Ayurveda Research Institute Kerala', 'Regulatory Approval', 'PENDING', '2026-08-01', None, 'Protocol awaiting final clearance endorsement from State Health Authority / DCGI nodal officer.', 'Regulatory Officer review required'),
        ('APP-004', 'AYU-TRIAL-002', 'Delhi', 'AIIA Main Hospital New Delhi', 'Protocol Amendment', 'PENDING', '2026-09-20', None, 'Amendment submitted to clarify batch testing requirements following mild skin rash signal.', 'IEC Review Scheduled for 28 Sep 2026'),
        ('APP-005', 'AYU-TRIAL-005', 'Lucknow', 'State Ayurvedic College Lucknow', 'Ethics Approval', 'APPROVED', '2026-08-15', '2026-09-10', 'Approved for upcoming IBS study launch.', 'Site readiness verification')
    ]
    c.executemany("""
    INSERT INTO ayur_approvals (approval_id, trial_id, city, hospital_name, approval_type, status, submission_date, decision_date, reviewer_notes, action_required)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, approvals)

    # -------------------------------------------------------------
    # 9. SEED GCP GUIDELINES CHECKLIST (Section 13 requirement)
    # -------------------------------------------------------------
    checklist = [
        ('GCP-01', 'Informed Consent Documentation', 'All participants have signed verified bilingual Patient Information Sheets (PIS) & Informed Consent Forms (ICF) prior to trial enrollment.', 1, '2026-09-20', 'Prof. (Dr.) Tanuja Nesari', 'Ethics & Consent'),
        ('GCP-02', 'Participant Confidentiality', 'All digital patient records are pseudonymized with unique trial subject identifiers and stored in access-controlled environments.', 1, '2026-09-20', 'Dr. Galib', 'Data Security'),
        ('GCP-03', 'Proper Record Keeping', 'Investigator Site Files (ISF), electronic Case Report Forms (eCRF), and dispensing logs are maintained up-to-date.', 1, '2026-09-18', 'Dr. Ananya Sharma', 'Documentation'),
        ('GCP-04', 'Investigator Qualification Verification', 'Curriculum vitae, GCP training certificates, and Medical Council registrations verified for all 11 investigators.', 1, '2026-09-15', 'Dr. K. S. Dhiman', 'Governance'),
        ('GCP-05', 'Protocol Adherence', 'Trial operations and eligibility criteria strictly follow the CDSCO and CTRI approved master study protocols.', 1, '2026-09-19', 'Dr. Soumya Roy', 'Protocol Fidelity'),
        ('GCP-06', 'Safety Event Reporting', 'Pharmacovigilance SOPs established for 24-hour SAE notification and 15-day expedited reporting to DCGI & Ethics Committee.', 1, '2026-09-22', 'Dr. A. Verma', 'Safety & Vigilance'),
        ('GCP-07', 'Trial Master File Documentation', 'All regulatory correspondence, approval certificates, and statistical analysis plans are deposited in secure central repository.', 1, '2026-09-10', 'S. Sharma, CRA', 'Quality Assurance'),
        ('GCP-08', 'Pending Monitoring Review', 'Independent Clinical Research Associate (CRA) monitoring visits scheduled for Q3 2026 across multi-center sites.', 0, '2026-09-23', 'S. Sharma, CRA', 'Monitoring'),
        ('GCP-09', 'Site Training Completed', 'Site staff, trial coordinators, and nursing personnel completed training on GCP, herbal drug storage, and CRF entry.', 1, '2026-09-05', 'Dr. Priyanshu Gupta', 'Training')
    ]
    c.executemany("""
    INSERT INTO ayur_gcp_checklist (item_id, title, description, is_completed, last_reviewed, reviewed_by, category)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, checklist)

    # -------------------------------------------------------------
    # 10. SEED NOTIFICATIONS (Section 21 requirement)
    # -------------------------------------------------------------
    notifications = [
        ('NOTIF-01', 'Approval Pending: Kerala Site', 'Regulatory approval for Hypertension trial (AYU-TRIAL-004) at Kerala site is pending review.', 'warning', 'approvals', 0, '2026-09-24 09:30:00'),
        ('NOTIF-02', 'Safety Signal Review Required', 'Potential Safety Signal detected in AYU-TRIAL-002: 7 participants reported skin rash.', 'critical', 'pharmacovigilance', 0, '2026-09-23 16:45:00'),
        ('NOTIF-03', 'Recruitment Milestone Near Target', 'Trial AYU-TRIAL-001 (Mumbai) has enrolled 120/150 participants (80% target achieved).', 'info', 'active-trials', 0, '2026-09-22 14:15:00'),
        ('NOTIF-04', 'Ethics Clearance Endorsed', 'Mumbai Site Ethics Committee renewal approved for AYU-TRIAL-001.', 'success', 'approvals', 1, '2026-09-20 11:00:00'),
        ('NOTIF-05', 'GCP Checklist Review', 'Quarterly GCP compliance review updated: 8/9 items completed (89%).', 'info', 'gcp', 1, '2026-09-18 10:20:00')
    ]
    c.executemany("""
    INSERT INTO ayur_notifications (notification_id, title, message, severity, target_route, is_read, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, notifications)

    # -------------------------------------------------------------
    # 11. SEED AUDIT TRAIL (Section 25 requirement)
    # -------------------------------------------------------------
    audits = [
        ('AUD-001', 'Dr. Research Admin', 'Updated patient treatment duration', 'Patient Management', '12 Weeks', '16 Weeks', '2026-09-23 10:32:00'),
        ('AUD-002', 'Dr. Galib', 'Reported adverse event for Ramlal Sharma (AE-001)', 'Pharmacovigilance', 'None', 'Skin Rash (Moderate)', '2026-09-18 14:15:00'),
        ('AUD-003', 'Dr. A. Verma', 'Recorded Safety Signal SIG-001 for AYU-TRIAL-002', 'Pharmacovigilance', 'None', 'Cluster Signal (7 cases)', '2026-09-20 16:00:00'),
        ('AUD-004', 'Dr. K. S. Dhiman', 'Endorsed Ethics Approval APP-001 (Mumbai Site)', 'Approvals', 'Pending', 'APPROVED', '2026-05-02 11:30:00'),
        ('AUD-005', 'Prof. (Dr.) Tanuja Nesari', 'Verified GCP Checklist item GCP-01', 'GCP Guidelines', 'Unverified', 'Completed & Verified', '2026-09-20 09:45:00')
    ]
    c.executemany("""
    INSERT INTO ayur_audit_trail (audit_id, user_name, action, module, previous_value, new_value, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, audits)

    conn.commit()
    conn.close()
    print("AYURCTMS Database initialized and successfully seeded.")

if __name__ == "__main__":
    init_ayur_tables()
    seed_ayur_data()
