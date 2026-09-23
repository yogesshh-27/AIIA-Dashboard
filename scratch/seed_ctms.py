import sqlite3
import json
import datetime
import os

APP_DB_PATH = "aiia_app.db"

def init_and_seed_ctms():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 1. Create CTMS Tables if they don't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS ctms_timelines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trial_id INTEGER NOT NULL,
        ctri_number TEXT NOT NULL,
        trial_title TEXT NOT NULL,
        stage_protocol_status TEXT DEFAULT 'Completed',
        stage_protocol_date TEXT,
        stage_iec_status TEXT DEFAULT 'Completed',
        stage_iec_date TEXT,
        stage_ctri_status TEXT DEFAULT 'Completed',
        stage_ctri_date TEXT,
        stage_activation_status TEXT DEFAULT 'Completed',
        stage_activation_date TEXT,
        stage_recruitment_status TEXT DEFAULT 'In Progress',
        stage_recruitment_date TEXT,
        stage_monitoring_status TEXT DEFAULT 'In Progress',
        stage_monitoring_date TEXT,
        stage_followup_status TEXT DEFAULT 'Upcoming',
        stage_followup_date TEXT,
        stage_dblock_status TEXT DEFAULT 'Upcoming',
        stage_dblock_date TEXT,
        stage_closeout_status TEXT DEFAULT 'Upcoming',
        stage_closeout_date TEXT,
        overall_status TEXT DEFAULT 'In Progress',
        is_synthetic INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ctms_recruitment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trial_id INTEGER NOT NULL,
        ctri_number TEXT NOT NULL,
        trial_title TEXT NOT NULL,
        target_enrollment INTEGER NOT NULL,
        current_enrollment INTEGER NOT NULL DEFAULT 0,
        enrollment_pct REAL NOT NULL DEFAULT 0.0,
        expected_enrollment INTEGER NOT NULL,
        enrollment_gap INTEGER NOT NULL DEFAULT 0,
        monthly_trend_json TEXT,
        is_synthetic INTEGER DEFAULT 1,
        last_updated TEXT
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ctms_monitoring_visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visit_code TEXT NOT NULL,
        trial_id INTEGER NOT NULL,
        ctri_number TEXT NOT NULL,
        trial_title TEXT NOT NULL,
        site_name TEXT NOT NULL,
        monitor_name TEXT NOT NULL,
        visit_type TEXT DEFAULT 'Interim Monitoring Visit (IMV)',
        planned_date TEXT NOT NULL,
        actual_date TEXT,
        status TEXT NOT NULL,
        findings TEXT,
        is_synthetic INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ctms_protocol_deviations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deviation_code TEXT NOT NULL,
        trial_id INTEGER NOT NULL,
        ctri_number TEXT NOT NULL,
        trial_title TEXT NOT NULL,
        site_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL,
        date_identified TEXT NOT NULL,
        status TEXT DEFAULT 'Open',
        resolution TEXT,
        is_synthetic INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ctms_milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        milestone_code TEXT NOT NULL,
        trial_id INTEGER NOT NULL,
        ctri_number TEXT NOT NULL,
        trial_title TEXT NOT NULL,
        milestone_name TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL,
        responsible_role TEXT NOT NULL,
        is_overdue INTEGER DEFAULT 0,
        is_synthetic INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check if records already seeded
    c.execute("SELECT COUNT(*) FROM ctms_timelines")
    count = c.fetchone()[0]
    if count > 0:
        print(f"CTMS operational tables already contain {count} timelines. Skipping seed.")
        conn.close()
        return

    # Fetch 15 actual AIIA trials to link realistic operational data
    c.execute("""
        SELECT id, ctri_number, public_title, target_sample_size 
        FROM trials 
        WHERE is_aiia = 1 
        ORDER BY id ASC 
        LIMIT 15
    """)
    trials = [dict(r) for r in c.fetchall()]

    if not trials:
        print("No AIIA trials found in trials table.")
        conn.close()
        return

    print(f"Seeding CTMS operational demonstration data for {len(trials)} AIIA trials...")

    # Pre-defined operational profiles
    profiles = [
        {
            "rec_status": "In Progress", "overall": "In Progress",
            "p_stat": "Completed", "p_dt": "2021-02-10",
            "iec_stat": "Completed", "iec_dt": "2021-03-15",
            "ctri_stat": "Completed", "ctri_dt": "2021-04-02",
            "act_stat": "Completed", "act_dt": "2021-05-01",
            "rec_dt": "2021-06-01",
            "mon_stat": "In Progress", "mon_dt": "2022-03-15",
            "fol_stat": "Upcoming", "fol_dt": "2022-11-01",
            "db_stat": "Upcoming", "db_dt": "2023-02-15",
            "cls_stat": "Upcoming", "cls_dt": "2023-04-30",
            "target": 120, "current": 84, "expected": 95,
        },
        {
            "rec_status": "Completed", "overall": "Completed",
            "p_stat": "Completed", "p_dt": "2017-06-15",
            "iec_stat": "Completed", "iec_dt": "2017-08-20",
            "ctri_stat": "Completed", "ctri_dt": "2017-10-06",
            "act_stat": "Completed", "act_dt": "2017-11-01",
            "rec_dt": "2017-11-15",
            "mon_stat": "Completed", "mon_dt": "2018-09-10",
            "fol_stat": "Completed", "fol_dt": "2018-12-15",
            "db_stat": "Completed", "db_dt": "2019-02-28",
            "cls_stat": "Completed", "cls_dt": "2019-05-15",
            "target": 66, "current": 66, "expected": 66,
        },
        {
            "rec_status": "Due Soon", "overall": "Due Soon",
            "p_stat": "Completed", "p_dt": "2021-08-01",
            "iec_stat": "Completed", "iec_dt": "2021-09-15",
            "ctri_stat": "Completed", "ctri_dt": "2021-11-05",
            "act_stat": "Completed", "act_dt": "2021-12-01",
            "rec_dt": "2022-01-10",
            "mon_stat": "Due Soon", "mon_dt": "2022-09-28",
            "fol_stat": "Upcoming", "fol_dt": "2023-01-15",
            "db_stat": "Upcoming", "db_dt": "2023-04-01",
            "cls_stat": "Upcoming", "cls_dt": "2023-06-30",
            "target": 80, "current": 52, "expected": 68,
        },
        {
            "rec_status": "Overdue", "overall": "Overdue",
            "p_stat": "Completed", "p_dt": "2020-04-12",
            "iec_stat": "Completed", "iec_dt": "2020-06-18",
            "ctri_stat": "Completed", "ctri_dt": "2020-08-25",
            "act_stat": "Completed", "act_dt": "2020-09-30",
            "rec_dt": "2020-10-15",
            "mon_stat": "Overdue", "mon_dt": "2021-06-15",
            "fol_stat": "Overdue", "fol_dt": "2021-12-01",
            "db_stat": "Overdue", "db_dt": "2022-03-15",
            "cls_stat": "Upcoming", "cls_dt": "2022-07-30",
            "target": 150, "current": 92, "expected": 150,
        },
        {
            "rec_status": "Upcoming", "overall": "Upcoming",
            "p_stat": "Completed", "p_dt": "2022-01-15",
            "iec_stat": "Completed", "iec_dt": "2022-02-28",
            "ctri_stat": "Completed", "ctri_dt": "2022-03-25",
            "act_stat": "In Progress", "act_dt": "2022-05-15",
            "rec_dt": "2022-06-01",
            "mon_stat": "Upcoming", "mon_dt": "2022-08-15",
            "fol_stat": "Upcoming", "fol_dt": "2022-12-01",
            "db_stat": "Upcoming", "db_dt": "2023-03-01",
            "cls_stat": "Upcoming", "cls_dt": "2023-05-30",
            "target": 50, "current": 8, "expected": 15,
        }
    ]

    monitors = [
        "Dr. M. S. Baghel (Lead Monitor)",
        "Dr. Rajeshwari Sharma (Senior CRA)",
        "Dr. Anand K. Verma (Clinical Monitor)",
        "Dr. Sunita Pathak (QA Monitor)",
        "Dr. Harish C. Gupta (GCP Auditor)"
    ]

    sites = [
        "All India Institute of Ayurveda - Hospital IPD Ward, New Delhi",
        "AIIA Department of Kayachikitsa & Panchakarma Clinical Unit",
        "National Institute of Ayurveda (NIA) Satellite Center, Jaipur",
        "Institute of Post Graduate Teaching & Research in Ayurveda (IPGT&RA), Jamnagar",
        "Government Ayurvedic College & Hospital, Varanasi"
    ]

    roles = [
        "Principal Investigator",
        "Clinical Research Coordinator (CRC)",
        "Ethics Committee Secretary",
        "Lead Clinical Monitor (CRA)",
        "Data Management Officer"
    ]

    deviation_templates = [
        ("Informed Consent", "Subject signed version 1.1 instead of version 1.2 of the Informed Consent Form.", "Major", "IEC notified; Subject re-consented under approved ICF version 1.2. Staff retrained."),
        ("Visit Window", "Day 28 follow-up assessment completed at Day 34 (+6 days outside +/- 2 day window).", "Minor", "Investigator reviewed clinical lab safety parameters; no patient safety impact. Logged in visit tracking."),
        ("Investigational Product", "Trial herbal formulation stored at 28°C for 4 hours during power fluctuation (specified 15-25°C).", "Minor", "Quality Assurance stability analysis confirmed batch potency within monograph specifications."),
        ("Eligibility", "Participant enrolled with baseline blood pressure 142/92 mmHg exceeding protocol threshold (140/90).", "Critical", "Medical Monitor granted safety exception waiver with heightened monitoring protocol. IEC formally informed."),
        ("Safety Reporting", "Grade 1 gastrointestinal discomfort reported 48 hours post onset instead of within 24 hours.", "Minor", "Investigator staff retrained on institutional adverse event reporting timeliness SOP."),
        ("Study Procedure", "Mandatory Day 14 Prakriti assessment checklist not completed by investigator prior to medication dispensing.", "Major", "Prakriti assessment retroactively verified by co-investigator on Day 15; SOP deviation logged.")
    ]

    milestone_templates = [
        ("Institutional Ethics Committee (IEC) Clearance", "Completed", 0),
        ("Clinical Trials Registry of India (CTRI) Clearance", "Completed", 0),
        ("Investigator Meeting & Site Initiation Visit (SIV)", "Completed", 0),
        ("First Participant Enrolled (FPI)", "Completed", 0),
        ("25% Enrollment Target Achieved", "Completed", 0),
        ("50% Enrollment Target Achieved", "Due Soon", 0),
        ("75% Enrollment Target Achieved", "Pending", 0),
        ("Final Participant Enrolled (LPI)", "Pending", 0),
        ("Last Participant Last Visit (LPLV)", "Pending", 0),
        ("Interim Monitoring Visit - Midterm SDV", "Overdue", 1),
        ("Annual IEC Progress & Safety Renewal", "Due Soon", 0),
        ("Data Clarification Forms (DCF) Reconciliation", "Pending", 0),
        ("Database Lock & Statistical Freeze", "Pending", 0),
        ("Clinical Study Report (CSR) Final Sign-off", "Pending", 0)
    ]

    for idx, t in enumerate(trials):
        prof = profiles[idx % len(profiles)]
        trial_id = t["id"]
        ctri_num = t["ctri_number"]
        title = t["public_title"]
        target = t["target_sample_size"] if t["target_sample_size"] and t["target_sample_size"] > 0 else prof["target"]
        current = int(target * (prof["current"] / prof["target"]))
        expected = int(target * (prof["expected"] / prof["target"]))
        pct = round((current / target * 100), 1) if target > 0 else 0.0
        gap = expected - current

        # 1. Timeline
        c.execute("""
            INSERT INTO ctms_timelines (
                trial_id, ctri_number, trial_title,
                stage_protocol_status, stage_protocol_date,
                stage_iec_status, stage_iec_date,
                stage_ctri_status, stage_ctri_date,
                stage_activation_status, stage_activation_date,
                stage_recruitment_status, stage_recruitment_date,
                stage_monitoring_status, stage_monitoring_date,
                stage_followup_status, stage_followup_date,
                stage_dblock_status, stage_dblock_date,
                stage_closeout_status, stage_closeout_date,
                overall_status, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            trial_id, ctri_num, title,
            prof["p_stat"], prof["p_dt"],
            prof["iec_stat"], prof["iec_dt"],
            prof["ctri_stat"], prof["ctri_dt"],
            prof["act_stat"], prof["act_dt"],
            prof["rec_status"], prof["rec_dt"],
            prof["mon_stat"], prof["mon_dt"],
            prof["fol_stat"], prof["fol_dt"],
            prof["db_stat"], prof["db_dt"],
            prof["cls_stat"], prof["cls_dt"],
            prof["overall"]
        ))

        # 2. Recruitment Trend
        trend = []
        months = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"]
        step_act = current / 12
        step_proj = expected / 12
        for m_idx, m_name in enumerate(months, 1):
            act_val = min(current, int(step_act * m_idx))
            proj_val = min(target, int(step_proj * m_idx))
            trend.append({"month": m_name, "actual": act_val, "projected": proj_val})

        c.execute("""
            INSERT INTO ctms_recruitment (
                trial_id, ctri_number, trial_title,
                target_enrollment, current_enrollment, enrollment_pct,
                expected_enrollment, enrollment_gap,
                monthly_trend_json, is_synthetic, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            trial_id, ctri_num, title,
            target, current, pct,
            expected, gap,
            json.dumps(trend), "2026-09-20"
        ))

        # 3. Monitoring Visits (2 visits per trial)
        v_stat1 = "Completed"
        v_dt1 = prof["p_dt"]
        c.execute("""
            INSERT INTO ctms_monitoring_visits (
                visit_code, trial_id, ctri_number, trial_title,
                site_name, monitor_name, visit_type,
                planned_date, actual_date, status, findings, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            f"SIV-2022-{idx+1:02d}", trial_id, ctri_num, title,
            sites[idx % len(sites)], monitors[idx % len(monitors)], "Site Initiation Visit (SIV)",
            v_dt1, v_dt1, v_stat1, "Site activation protocol completed. Pharmacy temperature log verified. Regulatory binder complete."
        ))

        v_stat2 = prof["mon_stat"]
        v_dt2 = prof["mon_dt"]
        act_dt2 = v_dt2 if v_stat2 == "Completed" else None
        findings2 = "Source data verification (SDV) completed for active cohort. Informed consent compliance 100%." if v_stat2 == "Completed" else ("Pending interim safety report audit and CRF monitoring." if v_stat2 != "Overdue" else "CRITICAL: Monitoring visit overdue by 45 days. Action plan required from Lead CRA.")

        c.execute("""
            INSERT INTO ctms_monitoring_visits (
                visit_code, trial_id, ctri_number, trial_title,
                site_name, monitor_name, visit_type,
                planned_date, actual_date, status, findings, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            f"IMV-2022-{idx+1:02d}", trial_id, ctri_num, title,
            sites[idx % len(sites)], monitors[(idx+1) % len(monitors)], "Interim Monitoring Visit (IMV)",
            v_dt2, act_dt2, v_stat2, findings2
        ))

        # 4. Protocol Deviations (1 deviation per trial for realism)
        dev_templ = deviation_templates[idx % len(deviation_templates)]
        dev_stat = "Resolved" if idx % 2 == 0 else ("Open" if idx % 3 == 0 else "Under Investigation")
        c.execute("""
            INSERT INTO ctms_protocol_deviations (
                deviation_code, trial_id, ctri_number, trial_title,
                site_name, category, description, severity,
                date_identified, status, resolution, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            f"DEV-2022-{idx+1:03d}", trial_id, ctri_num, title,
            sites[idx % len(sites)], dev_templ[0], dev_templ[1], dev_templ[2],
            prof["rec_dt"], dev_stat, dev_templ[3] if dev_stat == "Resolved" else "Under active institutional review.",
        ))

        # 5. Milestones (3 milestones per trial)
        for m_offset in range(3):
            m_item = milestone_templates[(idx * 3 + m_offset) % len(milestone_templates)]
            role = roles[(idx + m_offset) % len(roles)]
            due_d = f"2022-{(idx%12)+1:02d}-15"
            is_ov = 1 if m_item[1] == "Overdue" else 0
            c.execute("""
                INSERT INTO ctms_milestones (
                    milestone_code, trial_id, ctri_number, trial_title,
                    milestone_name, due_date, status, responsible_role,
                    is_overdue, is_synthetic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                f"MIL-2022-{idx*3+m_offset+1:03d}", trial_id, ctri_num, title,
                m_item[0], due_d, m_item[1], role, is_ov
            ))

    conn.commit()
    conn.close()
    print("CTMS operational demonstration data successfully created and seeded!")

if __name__ == "__main__":
    init_and_seed_ctms()
