import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_service

conn = db_service.get_app_connection()
c = conn.cursor()
c.execute("SELECT id, event_id, prev_hash, current_hash, new_value, user_name, role, action, entity, entity_id, previous_value, timestamp FROM hash_audit_chain WHERE event_id='EVT-0003'")
rows = c.fetchall()
print("EVT-0003 rows found:", len(rows))
for r in rows:
    rd = dict(r)
    print("Row:", rd)
    payload = f"{rd['prev_hash']}|{rd['event_id']}|{rd['timestamp']}|{rd['user_name']}|{rd['role']}|{rd['action']}|{rd['entity']}|{rd['entity_id']}|{rd['previous_value']}|{rd['new_value']}"
    calc = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    print("Stored hash:", rd['current_hash'])
    print("Recalc hash:", calc)
    print("Match?:", rd['current_hash'] == calc)

c.execute("SELECT id, event_id, current_hash FROM hash_audit_chain ORDER BY id ASC")
all_rows = c.fetchall()
print("Total rows:", len(all_rows))
print("All event IDs:", [dict(r)['event_id'] for r in all_rows[:10]])

res = db_service.verify_audit_chain()
print("Verify audit chain result:", res)
