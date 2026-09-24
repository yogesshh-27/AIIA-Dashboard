import sqlite3
import hashlib
import os
import secrets
import json
from datetime import datetime, timedelta

APP_DB_PATH = "aiia_app.db"

ROLES_DATA = [
    {
        "id": 1,
        "name": "Administrator",
        "description": "Institutional Research Administrator with unrestricted read/write access across all system entities.",
        "permissions": ["*"]
    },
    {
        "id": 2,
        "name": "Principal Investigator",
        "description": "Principal Investigator with scientific oversight over assigned studies, protocol milestones, and recruitment.",
        "permissions": ["trials:read", "trials:write", "ctms:read", "ctms:write", "compliance:read", "safety:read", "documents:read", "documents:write", "assistant:use"]
    },
    {
        "id": 3,
        "name": "Study Coordinator",
        "description": "Lead Study Coordinator managing operational trial data, patient intake, milestones, and deviation logs.",
        "permissions": ["trials:read", "ctms:read", "ctms:write", "recruitment:write", "deviations:write", "documents:read", "documents:write", "assistant:use"]
    },
    {
        "id": 4,
        "name": "Monitor",
        "description": "Clinical Research Associate / Monitor with site visit oversight, monitoring reports, and protocol compliance tracking.",
        "permissions": ["trials:read", "ctms:read", "monitoring:write", "deviations:verify", "compliance:read", "documents:read", "assistant:use"]
    },
    {
        "id": 5,
        "name": "Ethics Committee",
        "description": "Institutional Ethics Committee (IEC) reviewer evaluating initial protocol clearances, annual renewals, and ICFs.",
        "permissions": ["trials:read", "compliance:read", "iec:approve", "iec:review", "documents:read", "alerts:read", "assistant:use"]
    },
    {
        "id": 6,
        "name": "Pharmacovigilance Officer",
        "description": "Institutional & PvPI Safety Officer managing adverse events, safety signals, and statutory reporting deadlines.",
        "permissions": ["trials:read", "safety:read", "safety:write", "signals:review", "deadlines:submit", "alerts:read", "assistant:use"]
    },
    {
        "id": 7,
        "name": "Institutional Leadership",
        "description": "Institutional Executive Leadership with high-level portfolio oversight, completion metrics, and governance analytics.",
        "permissions": ["dashboard:read", "trials:read", "compliance:read", "ctms:read", "safety:read", "analytics:read", "interop:read", "assistant:use"]
    },
    {
        "id": 8,
        "name": "Regulator / Read-only",
        "description": "External regulatory auditor (CDSCO / AYUSH / CTRI) with authorized read-only inspection access.",
        "permissions": ["trials:read", "compliance:read", "safety:read", "audit:read", "interop:read", "cdisc:export", "fhir:read", "assistant:use"]
    }
]

USERS_DATA = [
    {
        "username": "admin_nesari",
        "full_name": "Prof. (Dr.) Tanuja Nesari",
        "role_name": "Administrator",
        "role_id": 1,
        "email": "director@aiia.gov.in",
        "institution": "All India Institute of Ayurveda, New Delhi",
        "default_password": "AdminPassword@2026"
    },
    {
        "username": "pi_galib",
        "full_name": "Dr. Galib",
        "role_name": "Principal Investigator",
        "role_id": 2,
        "email": "galib.pi@aiia.gov.in",
        "institution": "Department of Rasa Shastra, AIIA",
        "default_password": "PIPassword@2026"
    },
    {
        "username": "coord_gupta",
        "full_name": "Dr. P. Gupta",
        "role_name": "Study Coordinator",
        "role_id": 3,
        "email": "coord.gupta@aiia.gov.in",
        "institution": "Clinical Research Operations Unit, AIIA",
        "default_password": "CoordPassword@2026"
    },
    {
        "username": "monitor_sharma",
        "full_name": "S. Sharma, CRA",
        "role_name": "Monitor",
        "role_id": 4,
        "email": "cra.monitor@aiia.gov.in",
        "institution": "Clinical Quality Monitoring Board, AIIA",
        "default_password": "MonitorPassword@2026"
    },
    {
        "username": "iec_dhiman",
        "full_name": "Dr. K. S. Dhiman",
        "role_name": "Ethics Committee",
        "role_id": 5,
        "email": "iec.chair@aiia.gov.in",
        "institution": "Institutional Ethics Committee, AIIA",
        "default_password": "EthicsPassword@2026"
    },
    {
        "username": "pv_verma",
        "full_name": "Dr. A. Verma",
        "role_name": "Pharmacovigilance Officer",
        "role_id": 6,
        "email": "pv.safety@aiia.gov.in",
        "institution": "Pharmacovigilance & Safety Surveillance Center, AIIA",
        "default_password": "SafetyPassword@2026"
    },
    {
        "username": "dean_research",
        "full_name": "Dean of Research & Academics",
        "role_name": "Institutional Leadership",
        "role_id": 7,
        "email": "dean.research@aiia.gov.in",
        "institution": "Executive Council, AIIA",
        "default_password": "LeadershipPassword@2026"
    },
    {
        "username": "reg_auditor",
        "full_name": "Central Regulatory Auditor",
        "role_name": "Regulator / Read-only",
        "role_id": 8,
        "email": "regulatory.audit@cdsco.gov.in",
        "institution": "CDSCO / Ministry of AYUSH Inspectorate",
        "default_password": "RegulatorPassword@2026"
    }
]

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

def hash_password(password: str) -> str:
    """Generate salted PBKDF2-HMAC-SHA256 hash formatted as salt$hash."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"

def verify_password(stored_password_hash: str, password_attempt: str) -> bool:
    """Verify password against stored salt$hash."""
    try:
        salt, key_hex = stored_password_hash.split("$", 1)
        expected_key = hashlib.pbkdf2_hmac("sha256", password_attempt.encode("utf-8"), salt.encode("utf-8"), 100000)
        return secrets.compare_digest(expected_key.hex(), key_hex)
    except Exception:
        return False

def setup():
    conn = sqlite3.connect(APP_DB_PATH)
    c = conn.cursor()

    # 1. Update/recreate roles table
    c.execute("DROP TABLE IF EXISTS roles")
    c.execute("""
        CREATE TABLE roles (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            permissions_json TEXT NOT NULL
        )
    """)
    for r in ROLES_DATA:
        c.execute("INSERT INTO roles (id, name, description, permissions_json) VALUES (?, ?, ?, ?)",
                  (r["id"], r["name"], r["description"], json.dumps(r["permissions"])))

    # 2. Recreate users table
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            role_name TEXT NOT NULL,
            institution TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    """)
    for u in USERS_DATA:
        phash = hash_password(u["default_password"])
        c.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role_id, role_name, institution, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (u["username"], u["email"], phash, u["full_name"], u["role_id"], u["role_name"], u["institution"]))

    # 3. Create user_sessions table
    c.execute("DROP TABLE IF EXISTS user_sessions")
    c.execute("""
        CREATE TABLE user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            role_name TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 4. Create hash_audit_chain table
    c.execute("DROP TABLE IF EXISTS hash_audit_chain")
    c.execute("""
        CREATE TABLE hash_audit_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            user_name TEXT NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            entity TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            previous_value TEXT,
            new_value TEXT,
            ip_address TEXT,
            device_metadata TEXT,
            prev_hash TEXT NOT NULL,
            current_hash TEXT NOT NULL
        )
    """)

    # Seed initial cryptographic audit events
    initial_events = [
        {
            "event_id": "EVT-0001",
            "timestamp": "2026-09-23 09:00:00",
            "user_name": "System Genesis",
            "role": "System",
            "action": "SYSTEM_GENESIS",
            "entity": "System",
            "entity_id": "SYS-INIT",
            "previous_value": "None",
            "new_value": "Initialized Institutional Trial Intelligence Database",
            "ip_address": "127.0.0.1",
            "device_metadata": "AIIA Server Kernel 6.1"
        },
        {
            "event_id": "EVT-0002",
            "timestamp": "2026-09-23 09:15:32",
            "user_name": "Prof. (Dr.) Tanuja Nesari",
            "role": "Administrator",
            "action": "SEED_SECURITY_ROLES",
            "entity": "RoleMatrix",
            "entity_id": "ROLES-8",
            "previous_value": "3 Legacy Roles",
            "new_value": "8 Institutional RBAC Roles Configured",
            "ip_address": "192.168.1.10",
            "device_metadata": "Firefox 128.0 (Windows NT 10.0; Win64; x64)"
        },
        {
            "event_id": "EVT-0003",
            "timestamp": "2026-09-23 10:30:14",
            "user_name": "Dr. Galib",
            "role": "Principal Investigator",
            "action": "UPDATE_RECRUITMENT",
            "entity": "TrialRecruitment",
            "entity_id": "CTRI/2017/10/010023",
            "previous_value": "Enrolled: 82",
            "new_value": "Enrolled: 86 (Target: 100)",
            "ip_address": "192.168.1.45",
            "device_metadata": "Chrome 128.0 (Macintosh; Intel Mac OS X 10_15_7)"
        },
        {
            "event_id": "EVT-0004",
            "timestamp": "2026-09-23 11:20:05",
            "user_name": "Dr. K. S. Dhiman",
            "role": "Ethics Committee",
            "action": "RENEW_IEC_APPROVAL",
            "entity": "EthicsCommittee",
            "entity_id": "CTRI/2018/02/011783",
            "previous_value": "Status: Due Soon (Exp: 2026-10-15)",
            "new_value": "Status: Approved (Exp: 2027-10-15)",
            "ip_address": "192.168.1.88",
            "device_metadata": "Edge 128.0 (Windows NT 10.0; Win64; x64)"
        },
        {
            "event_id": "EVT-0005",
            "timestamp": "2026-09-23 14:45:22",
            "user_name": "Dr. A. Verma",
            "role": "Pharmacovigilance Officer",
            "action": "FLAG_SAFETY_SIGNAL",
            "entity": "SafetySignal",
            "entity_id": "SIG-0001",
            "previous_value": "Status: Unreviewed",
            "new_value": "Status: Under Investigation (Joint pain +100%)",
            "ip_address": "192.168.1.92",
            "device_metadata": "Safari 17.5 (Macintosh; Intel Mac OS X 10_15_7)"
        }
    ]

    last_hash = GENESIS_HASH
    for ev in initial_events:
        payload = f"{last_hash}|{ev['event_id']}|{ev['timestamp']}|{ev['user_name']}|{ev['role']}|{ev['action']}|{ev['entity']}|{ev['entity_id']}|{ev['previous_value']}|{ev['new_value']}"
        curr_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        c.execute("""
            INSERT INTO hash_audit_chain (
                event_id, timestamp, user_name, role, action, entity, entity_id,
                previous_value, new_value, ip_address, device_metadata, prev_hash, current_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ev["event_id"], ev["timestamp"], ev["user_name"], ev["role"], ev["action"],
            ev["entity"], ev["entity_id"], ev["previous_value"], ev["new_value"],
            ev["ip_address"], ev["device_metadata"], last_hash, curr_hash
        ))
        last_hash = curr_hash

    conn.commit()
    conn.close()
    print("Security, RBAC, Users, and Hash Audit Chain initialized successfully.")

if __name__ == "__main__":
    setup()
