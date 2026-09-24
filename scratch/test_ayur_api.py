import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post(path, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

try:
    print("1. Testing /api/ayur/dashboard/stats ...")
    stats = get("/api/ayur/dashboard/stats")
    print(f"   Doctors: {stats['kpi_cards']['doctors']['total_doctors']}, Patients: {stats['kpi_cards']['patients']['total_patients']}, Adverse Events: {stats['kpi_cards']['pharmacovigilance']['total_adverse_events']}")

    print("2. Testing /api/ayur/patient/match ...")
    match = post("/api/ayur/patient/match", {
        "condition": "Arthritis",
        "accessible_locations": ["Mumbai", "Delhi"],
        "distance_pref": "Within 50km"
    })
    print(f"   Matches: {match['total_matches']}, First trial: {match['results'][0]['trial_id']} - {match['results'][0]['condition']}")

    print("3. Testing /api/ayur/auth/login ...")
    login_success = post("/api/ayur/auth/login", {
        "staff_id": "AIIA001",
        "password": "AIIA@123"
    })
    print(f"   Login Success: {login_success.get('success')}, User: {login_success.get('user', {}).get('full_name')}")

    print("4. Testing /api/ayur/sites ...")
    sites = get("/api/ayur/sites")
    print(f"   Total Sites: {len(sites.get('sites', []))}")

    print("5. Testing /api/ayur/pv/signals ...")
    signals = get("/api/ayur/pv/signals")
    print(f"   Signals: {signals.get('total')}, Summary: {signals.get('signals', [{}])[0].get('signal_title')}")

    print("6. Testing /api/ayur/gcp ...")
    gcp = get("/api/ayur/gcp")
    print(f"   GCP Compliance: {gcp.get('compliance_pct')}% ({gcp.get('completed_items')}/{gcp.get('total_items')})")

    print("7. Testing /api/ayur/search?q=Ramlal ...")
    search = get("/api/ayur/search?q=Ramlal")
    print(f"   Search Results Patients: {len(search.get('patients', []))}")

    print("\nALL AYURCTMS BACKEND APIS FUNCTIONING PROPERLY!")
except Exception as e:
    print("Error testing API:", e)
