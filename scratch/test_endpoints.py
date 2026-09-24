import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"

def post_json(path, data, headers=None):
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE}{path}", data=json.dumps(data).encode("utf-8"), headers=req_headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.status

def test():
    # 1. Test Assistant
    ans, status = post_json("/api/assistant/query", {"query": "How many recruiting trials are in the dataset?"})
    print("ASSISTANT STATUS:", status)
    print("ASSISTANT INTENT:", ans["intent"])
    print("ASSISTANT ANSWER:", ans["answer"])
    print("ASSISTANT METRICS:", ans["verified_metrics"])
    print("ASSISTANT SOURCE:", ans["source"])

    # 2. Test Login
    login_res, status = post_json("/api/auth/login", {"username": "admin_nesari", "password": "AdminPassword@2026"})
    print("LOGIN STATUS:", status, "USER:", login_res["full_name"], "ROLE:", login_res["role_name"])

    # 3. Test RBAC: Regulator Read-Only restriction
    try:
        post_json("/api/alerts/1/status", {"status": "Resolved"}, headers={"X-Active-Role": "Regulator / Read-only"})
        print("RBAC REGULATOR CHECK FAILED: Expected 403")
    except urllib.error.HTTPError as e:
        print("RBAC REGULATOR 403 ENFORCED:", e.code, e.read().decode("utf-8"))

    # 4. Test RBAC: Admin allowed
    res, status = post_json("/api/alerts/1/status", {"status": "Acknowledged"}, headers={"X-Active-Role": "Administrator"})
    print("RBAC ADMIN ALLOWED:", status, res.get("status"))

    # 5. Test Audit Chain Verification
    req = urllib.request.Request(f"{BASE}/api/audit/verify")
    with urllib.request.urlopen(req) as resp:
        verify_res = json.loads(resp.read().decode("utf-8"))
        print("AUDIT CHAIN:", verify_res["status"], "EVENTS VERIFIED:", verify_res["total_events"])

    # 6. Test FHIR Validation
    req = urllib.request.Request(f"{BASE}/api/interop/fhir/study")
    with urllib.request.urlopen(req) as resp:
        study = json.loads(resp.read().decode("utf-8"))
    val_res, _ = post_json("/api/interop/fhir/validate", study)
    print("FHIR VALIDATION:", val_res["is_valid"], val_res["compliance_summary"])

if __name__ == "__main__":
    test()
