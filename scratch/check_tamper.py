import db_service
import hashlib

conn = db_service.get_app_connection()
c = conn.cursor()
c.execute('SELECT * FROM hash_audit_chain WHERE event_id="EVT-0003"')
r = dict(c.fetchone())
print('Row EVT-0003:', r)

v1 = db_service.verify_audit_chain()
print('Initial verify:', v1['verified'], v1.get('status'))

t = db_service.tamper_audit_event_demo('EVT-0003', 'MALICIOUS_VAL_123')
print('Tamper result:', t)

v2 = db_service.verify_audit_chain()
print('After tamper verify:', v2['verified'], v2.get('status'), v2.get('reason'), v2.get('failed_event_id'))

res = db_service.restore_audit_chain_demo()
print('Restore result:', res)

v3 = db_service.verify_audit_chain()
print('After restore verify:', v3['verified'], v3.get('status'))
