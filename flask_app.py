"""
AIIA Dashboard — Flask Backend (Production-Grade)
Upgraded from raw http.server to Flask with proper middleware, error handling, and CORS.
"""
import io
import os
import csv
import sys
import json
import urllib.parse
from typing import Dict, Any
from functools import wraps

from flask import Flask, request, jsonify, make_response, send_from_directory

import db_service

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder=None)
app.config['JSON_SORT_KEYS'] = False

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Session-Token, X-Active-Role'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.status_code = 204
        return resp


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def get_auth_context() -> Dict[str, Any]:
    """Extract active user, role, and permissions from headers or token."""
    auth_header = request.headers.get('Authorization', '')
    token = ''
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    if not token:
        token = request.headers.get('X-Session-Token', '')
    if not token:
        token = request.args.get('token', '')

    session = db_service.get_session(token) if token else None
    demo_role = request.headers.get('X-Active-Role', '').strip()

    if session:
        active_role = demo_role if demo_role else session.get('role_name', 'Administrator')
        user_name = session.get('full_name', session.get('username', 'Authenticated User'))
        user_id = session.get('user_id', 1)
        perms = session.get('permissions', ['*'])
    elif demo_role:
        active_role = demo_role
        user_name = f'Demo User ({demo_role})'
        user_id = 1
        roles = db_service.get_roles()
        role_dict = next((r for r in roles if r['name'] == active_role), None)
        perms = role_dict['permissions'] if role_dict else ['*']
    else:
        active_role = 'Administrator'
        user_name = 'Prof. (Dr.) Tanuja Nesari'
        user_id = 1
        perms = ['*']

    return {
        'token': token or 'demo-session-token',
        'user_id': user_id,
        'user_name': user_name,
        'role': active_role,
        'permissions': perms,
        'is_authenticated': True,
    }


def require_permission(permission_code: str):
    """Decorator to enforce server-side RBAC authorization."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = get_auth_context()
            role = auth['role']

            # Regulator role is strictly read-only
            if role == 'Regulator / Read-only' and request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
                return jsonify({
                    'error': 'Forbidden: Read-Only Access',
                    'message': f"Role '{role}' is restricted to authorized read-only audit access. All modifying actions are prohibited.",
                    'role': role,
                    'required_permission': permission_code,
                }), 403

            if not db_service.has_permission(role, permission_code):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f"Role '{role}' is not authorized to perform action '{permission_code}'. Server-side RBAC restriction enforced.",
                    'role': role,
                    'required_permission': permission_code,
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_client_ip() -> str:
    return request.remote_addr or '127.0.0.1'


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found', 'code': 404}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'code': 500}), 500


# ===================================================================
# GET ROUTES — Core Dashboard
# ===================================================================

@app.route('/api/dashboard/portfolio')
def dashboard_portfolio():
    return jsonify(db_service.get_dashboard_portfolio())


@app.route('/api/stats')
def stats():
    return jsonify(db_service.get_kpis())


@app.route('/api/trials')
def trials():
    return jsonify(db_service.get_trials(
        scope=request.args.get('scope', 'aiia'),
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        phase=request.args.get('phase', ''),
        trial_type=request.args.get('trial_type', ''),
        sponsor=request.args.get('sponsor', ''),
        thesis=request.args.get('thesis', ''),
        year=request.args.get('year', ''),
        date_from=request.args.get('date_from', ''),
        date_to=request.args.get('date_to', ''),
        sort_by=request.args.get('sort_by', 'registered_on'),
        sort_dir=request.args.get('sort_dir', 'desc'),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


@app.route('/api/trials/<trial_id_str>')
def trial_detail(trial_id_str):
    try:
        trial_id = int(trial_id_str)
        trial_data = db_service.get_trial_detail(trial_id)
    except (ValueError, TypeError):
        trial_data = None
    if trial_data:
        return jsonify(trial_data)
    return jsonify({'error': 'Trial not found', 'code': 404}), 404


@app.route('/api/governance')
def governance():
    return jsonify(db_service.get_governance_insights(scope=request.args.get('scope', 'aiia')))


@app.route('/api/analytics')
def analytics():
    return jsonify(db_service.get_analytics_deep_dive(scope=request.args.get('scope', 'aiia')))


@app.route('/api/cdisc')
def cdisc():
    return jsonify(db_service.search_cdisc_concepts(
        search=request.args.get('search', ''),
        limit=int(request.args.get('limit', 50)),
    ))


@app.route('/api/app/stats')
def app_stats():
    return jsonify(db_service.get_app_db_stats())


@app.route('/api/app/trials')
def app_trials():
    return jsonify(db_service.get_app_trials(
        scope=request.args.get('scope', 'aiia'),
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


# ===================================================================
# GET ROUTES — CTRI Extractor
# ===================================================================

@app.route('/api/ctri-extractor/trials')
@app.route('/api/ctri/dataset')
def ctri_extractor_trials():
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctri-extractor', 'output', 'ctri_trials.json')
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            trials = json.load(f)
        for t in trials:
            c_num = t.get('ctri_number', '')
            s_url = t.get('source_url', '')
            if s_url and 'showallp.php' in s_url and c_num:
                if 'userName=' in s_url:
                    base = s_url.split('userName=')[0]
                    t['source_url'] = f'{base}userName={urllib.parse.quote(c_num)}'
                else:
                    sep = '&' if '?' in s_url else '?'
                    t['source_url'] = f'{s_url}{sep}userName={urllib.parse.quote(c_num)}'
    else:
        trials = []

    search_term = request.args.get('search', '').lower()
    if search_term:
        trials = [
            t for t in trials if search_term in (t.get('public_title', '') or '').lower()
            or search_term in (t.get('ctri_number', '') or '').lower()
            or search_term in (t.get('condition', '') or '').lower()
            or search_term in (t.get('intervention_name', '') or '').lower()
            or search_term in (t.get('principal_investigator', '') or '').lower()
        ]

    limit_val = int(request.args.get('limit', 100))
    return jsonify({'total': len(trials), 'trials': trials[:limit_val]})


@app.route('/api/ctri-extractor/quality-report')
def ctri_quality_report():
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctri-extractor', 'output', 'quality_report.txt')
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = 'Quality report not found.'
    return jsonify({'report': content})


# ===================================================================
# GET ROUTES — CTMS
# ===================================================================

@app.route('/api/ctms/overview')
def ctms_overview():
    return jsonify(db_service.get_ctms_overview())


@app.route('/api/ctms/timelines')
def ctms_timelines():
    return jsonify(db_service.get_ctms_timelines(
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


@app.route('/api/ctms/recruitment')
def ctms_recruitment():
    return jsonify(db_service.get_ctms_recruitment(
        search=request.args.get('search', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


@app.route('/api/ctms/monitoring')
def ctms_monitoring():
    return jsonify(db_service.get_ctms_monitoring(
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


@app.route('/api/ctms/deviations')
def ctms_deviations():
    return jsonify(db_service.get_ctms_deviations(
        search=request.args.get('search', ''),
        severity=request.args.get('severity', ''),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


@app.route('/api/ctms/milestones')
def ctms_milestones():
    return jsonify(db_service.get_ctms_milestones(
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        overdue_only=request.args.get('overdue_only', 'false').lower() in ('true', '1'),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


# ===================================================================
# GET ROUTES — Compliance
# ===================================================================

@app.route('/api/compliance/overview')
def compliance_overview():
    return jsonify(db_service.get_compliance_overview())


@app.route('/api/compliance/data-quality')
def compliance_data_quality():
    return jsonify(db_service.calculate_data_quality_audit(scope=request.args.get('scope', 'aiia')))


# ===================================================================
# GET ROUTES — Alerts
# ===================================================================

@app.route('/api/alerts')
def alerts():
    return jsonify(db_service.get_alerts(
        category=request.args.get('category', ''),
        severity=request.args.get('severity', ''),
        status=request.args.get('status', ''),
        search=request.args.get('search', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 15)),
    ))


# ===================================================================
# GET ROUTES — Pharmacovigilance
# ===================================================================

@app.route('/api/pv/overview')
def pv_overview():
    return jsonify(db_service.get_pv_overview())


@app.route('/api/pv/adverse-events')
def pv_adverse_events():
    return jsonify(db_service.get_pv_adverse_events(
        search=request.args.get('search', ''),
        severity=request.args.get('severity', ''),
        serious_only=request.args.get('serious_only', 'false').lower() in ('true', '1'),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 20)),
    ))


@app.route('/api/pv/signals')
def pv_signals():
    return jsonify(db_service.get_pv_safety_signals(
        search=request.args.get('search', ''),
        severity=request.args.get('severity', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 20)),
    ))


@app.route('/api/pv/reporting')
def pv_reporting():
    return jsonify(db_service.get_pv_reporting_deadlines(
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 20)),
    ))


# ===================================================================
# GET ROUTES — Security & RBAC
# ===================================================================

@app.route('/api/auth/roles')
def auth_roles():
    return jsonify(db_service.get_roles())


@app.route('/api/auth/users')
def auth_users():
    return jsonify(db_service.get_users())


@app.route('/api/auth/me')
def auth_me():
    return jsonify(get_auth_context())


# ===================================================================
# GET ROUTES — Hash-Linked Audit Trail
# ===================================================================

@app.route('/api/audit/chain')
def audit_chain():
    return jsonify(db_service.get_audit_chain(
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 20)),
        search=request.args.get('search', ''),
        role_filter=request.args.get('role', ''),
    ))


@app.route('/api/audit/verify')
def audit_verify():
    return jsonify(db_service.verify_audit_chain())


# ===================================================================
# GET ROUTES — Interoperability (CDISC & FHIR R4)
# ===================================================================

@app.route('/api/interop/cdisc/overview')
def interop_cdisc_overview():
    return jsonify(db_service.get_cdisc_overview())


@app.route('/api/interop/cdisc/mapping')
def interop_cdisc_mapping():
    return jsonify(db_service.get_cdisc_mappings())


@app.route('/api/interop/cdisc/export')
def interop_cdisc_export():
    fmt = request.args.get('format', 'sdtm').lower()
    trial_id = request.args.get('trial_id', None)

    if fmt == 'sdtm':
        return jsonify(db_service.export_cdisc_sdtm(trial_id=trial_id))
    elif fmt == 'adam':
        return jsonify(db_service.export_cdisc_adam(trial_id=trial_id))
    elif fmt == 'define_xml':
        xml_data = db_service.export_cdisc_define_xml(trial_id=trial_id)
        resp = make_response(xml_data)
        resp.headers['Content-Type'] = 'application/xml; charset=utf-8'
        resp.headers['Content-Disposition'] = 'attachment; filename="define_xml_demonstration.xml"'
        return resp
    else:
        return jsonify({'error': f"Unsupported export format '{fmt}'"}), 400


@app.route('/api/interop/fhir/study')
def interop_fhir_study():
    return jsonify(db_service.get_fhir_research_study(trial_id=request.args.get('trial_id', None)))


# ===================================================================
# GET ROUTES — Documents
# ===================================================================

@app.route('/api/documents/summary')
def documents_summary():
    return jsonify(db_service.get_documents_summary())


@app.route('/api/documents')
def documents_list():
    return jsonify(db_service.get_documents(
        category=request.args.get('category', ''),
        search=request.args.get('search', ''),
        trial_ctri=request.args.get('trial_ctri', ''),
        status=request.args.get('status', ''),
        page=int(request.args.get('page', 1)),
        limit=int(request.args.get('limit', 20)),
    ))


@app.route('/api/documents/<doc_id_str>/download')
@require_permission('documents:read')
def documents_download(doc_id_str):
    version = request.args.get('version', '')
    doc_file = db_service.get_document_file_path(doc_id_str, version=version if version else None)
    if not doc_file or not os.path.exists(doc_file['file_path']):
        return jsonify({'error': 'Document file not found in secure repository.', 'code': 404}), 404

    auth = get_auth_context()
    db_service.log_audit_event(
        user_name=auth['user_name'],
        role=auth['role'],
        action='DOWNLOAD_DOCUMENT',
        entity='DocumentRepository',
        entity_id=doc_file['doc_id'],
        previous_value='Stored Securely',
        new_value=f"Downloaded {doc_file['file_name']} (v{doc_file['version']}) - SHA256: {doc_file['checksum_sha256'][:12]}...",
        ip_address=get_client_ip(),
    )

    with open(doc_file['file_path'], 'rb') as f:
        file_bytes = f.read()

    resp = make_response(file_bytes)
    resp.headers['Content-Type'] = 'application/octet-stream'
    resp.headers['Content-Disposition'] = f'attachment; filename="{doc_file["file_name"]}"'
    resp.headers['X-Document-ID'] = doc_file['doc_id']
    resp.headers['X-Document-Checksum'] = doc_file['checksum_sha256']
    return resp


@app.route('/api/documents/<doc_id_str>')
def documents_detail(doc_id_str):
    doc_detail = db_service.get_document_detail(doc_id_str)
    if doc_detail:
        return jsonify(doc_detail)
    return jsonify({'error': 'Document not found', 'code': 404}), 404


# ===================================================================
# GET ROUTES — Reports
# ===================================================================

@app.route('/api/reports/data')
def reports_data():
    rep_type = request.args.get('type', 'portfolio').lower()
    return _get_report_by_type(rep_type)


@app.route('/api/reports/<rep_type>')
def reports_by_type(rep_type):
    if rep_type == 'export':
        return reports_export()
    return _get_report_by_type(rep_type.strip().lower())


def _get_report_by_type(rep_type):
    handlers = {
        'portfolio': db_service.get_report_portfolio,
        'recruitment': db_service.get_report_recruitment,
        'compliance': db_service.get_report_compliance,
        'safety': db_service.get_report_safety,
        'data_quality': db_service.get_report_data_quality,
        'data-quality': db_service.get_report_data_quality,
        'audit': db_service.get_report_audit,
    }
    handler = handlers.get(rep_type)
    if handler:
        return jsonify(handler())
    return jsonify({'error': f"Unknown report type '{rep_type}'"}), 400


@app.route('/api/reports/export')
def reports_export():
    rep_type = request.args.get('type', 'portfolio').lower()
    export_fmt = request.args.get('format', 'csv').lower()
    auth = get_auth_context()

    if export_fmt in ('pdf', 'html'):
        html_content = db_service.generate_report_printable_html(
            rep_type,
            generated_by=auth.get('user_name', 'Prof. (Dr.) Tanuja Nesari'),
            role=auth.get('role', 'Administrator'),
        )
        resp = make_response(html_content)
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
        return resp
    else:
        csv_content = db_service.generate_report_csv(rep_type)
        resp = make_response(csv_content)
        resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
        resp.headers['Content-Disposition'] = f'attachment; filename="AIIA_{rep_type.upper()}_REPORT.csv"'
        return resp


# ===================================================================
# GET ROUTES — Export (Trials)
# ===================================================================

@app.route('/api/export')
def export_trials():
    res = db_service.get_trials(
        scope=request.args.get('scope', 'aiia'),
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        phase=request.args.get('phase', ''),
        trial_type=request.args.get('trial_type', ''),
        sponsor=request.args.get('sponsor', ''),
        thesis=request.args.get('thesis', ''),
        year=request.args.get('year', ''),
        date_from=request.args.get('date_from', ''),
        date_to=request.args.get('date_to', ''),
        sort_by=request.args.get('sort_by', 'registered_on'),
        sort_dir=request.args.get('sort_dir', 'desc'),
        page=1, limit=2000,
    )
    export_fmt = request.args.get('format', 'csv').lower()

    if export_fmt == 'json':
        json_bytes = json.dumps(res['data'], indent=2, ensure_ascii=False)
        resp = make_response(json_bytes)
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        resp.headers['Content-Disposition'] = 'attachment; filename="aiia_trials_export.json"'
        resp.headers['X-Export-Disclaimer'] = 'Prototype mapping/export - AIIA Clinical Trial Intelligence'
        return resp
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'CTRI Number', 'Public Title', 'Scientific Title', 'Recruitment Status',
            'Phase', 'Type of Trial', 'Target Sample Size', 'Registration Date',
            'Primary Sponsor', 'Principal Investigator', 'Affiliation',
        ])
        for r in res['data']:
            writer.writerow([
                r.get('CTRI_Number', ''), r.get('Public_Title', ''),
                r.get('Scientific_Title', ''), r.get('Recruitment_Status_India', ''),
                r.get('Phase', ''), r.get('Type_of_Trial', ''),
                r.get('Target_Sample_Size', ''), r.get('Registration_Date', ''),
                r.get('Primary_Sponsor', ''), r.get('PI_Name', ''),
                r.get('PI_Affiliation', ''),
            ])
        resp = make_response(output.getvalue())
        resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
        resp.headers['Content-Disposition'] = 'attachment; filename="aiia_trials_export.csv"'
        return resp


# ===================================================================
# GET ROUTES — AYURCTMS Dedicated REST API
# ===================================================================

@app.route('/api/ayur/dashboard/stats')
def ayur_dashboard_stats():
    return jsonify(db_service.get_ayur_dashboard_stats())


@app.route('/api/ayur/sites')
def ayur_sites():
    city = request.args.get('city', '')
    if city:
        return jsonify(db_service.get_ayur_sites(city=city))
    return jsonify(db_service.get_ayur_sites())


@app.route('/api/ayur/sites/<path:city>')
def ayur_site_detail(city):
    return jsonify(db_service.get_ayur_sites(city=city))


@app.route('/api/ayur/trials')
def ayur_trials():
    return jsonify(db_service.get_ayur_trials(
        status=request.args.get('status', ''),
        condition=request.args.get('condition', ''),
        location=request.args.get('location', ''),
        search=request.args.get('search', ''),
    ))


@app.route('/api/ayur/trials/<path:trial_id>')
def ayur_trial_detail(trial_id):
    return jsonify(db_service.get_ayur_trial_detail(trial_id))


@app.route('/api/ayur/doctors')
def ayur_doctors():
    return jsonify(db_service.get_ayur_doctors(
        site=request.args.get('site', ''),
        specialization=request.args.get('specialization', ''),
        status=request.args.get('status', ''),
        search=request.args.get('search', ''),
    ))


@app.route('/api/ayur/doctors/<path:doctor_id>')
def ayur_doctor_detail(doctor_id):
    return jsonify(db_service.get_ayur_doctor_detail(doctor_id))


@app.route('/api/ayur/patients')
def ayur_patients():
    return jsonify(db_service.get_ayur_patients(
        condition=request.args.get('condition', ''),
        site=request.args.get('site', ''),
        status=request.args.get('status', ''),
        search=request.args.get('search', ''),
    ))


@app.route('/api/ayur/patients/<path:patient_id>')
def ayur_patient_detail(patient_id):
    return jsonify(db_service.get_ayur_patient_detail(patient_id))


@app.route('/api/ayur/pv/summary')
def ayur_pv_summary():
    return jsonify(db_service.get_ayur_pv_summary())


@app.route('/api/ayur/pv/events')
def ayur_pv_events():
    return jsonify(db_service.get_ayur_adverse_events(
        trial_id=request.args.get('trial_id', ''),
        severity=request.args.get('severity', ''),
        status=request.args.get('status', ''),
        search=request.args.get('search', ''),
    ))


@app.route('/api/ayur/pv/signals')
def ayur_pv_signals():
    return jsonify(db_service.get_ayur_safety_signals())


@app.route('/api/ayur/approvals')
def ayur_approvals():
    return jsonify(db_service.get_ayur_approvals(
        site=request.args.get('site', ''),
        approval_type=request.args.get('type', ''),
        status=request.args.get('status', ''),
    ))


@app.route('/api/ayur/gcp')
def ayur_gcp():
    return jsonify(db_service.get_ayur_gcp_checklist())


@app.route('/api/ayur/reports')
def ayur_reports():
    return jsonify(db_service.get_ayur_report_data(
        report_type=request.args.get('type', 'trial_progress'),
    ))


@app.route('/api/ayur/reports/export')
def ayur_reports_export():
    report_type = request.args.get('type', 'trial_progress')
    fmt = request.args.get('format', 'csv').lower()
    rep_data = db_service.get_ayur_report_data(report_type=report_type)

    if fmt == 'csv':
        out = io.StringIO()
        writer = csv.writer(out)
        cols = rep_data.get('columns', [])
        writer.writerow(cols)
        for row in rep_data.get('rows', []):
            writer.writerow([row.get(c, '') for c in cols])
        resp = make_response(out.getvalue())
        resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
        resp.headers['Content-Disposition'] = f'attachment; filename="AYURCTMS_{report_type.upper()}_REPORT.csv"'
        return resp
    else:
        return jsonify(rep_data)


@app.route('/api/ayur/search')
def ayur_search():
    q = request.args.get('q', request.args.get('search', ''))
    return jsonify(db_service.global_ayur_search(q))


@app.route('/api/ayur/notifications')
def ayur_notifications():
    return jsonify(db_service.get_ayur_notifications())


@app.route('/api/ayur/interop/demo')
def ayur_interop_demo():
    return jsonify(db_service.get_ayur_interop_demo())


@app.route('/api/ayur/audit')
def ayur_audit():
    return jsonify(db_service.get_ayur_audit_trail())


# ===================================================================
# POST ROUTES
# ===================================================================

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    body = request.get_json(force=True, silent=True) or {}
    username = body.get('username', '')
    password = body.get('password', '')
    ip = get_client_ip()
    agent = request.headers.get('User-Agent', 'WebBrowser')
    auth_res = db_service.authenticate_user(username, password, ip_address=ip, user_agent=agent)
    if auth_res:
        return jsonify(auth_res)
    return jsonify({'error': 'Invalid institutional credentials or inactive account.'}), 401


@app.route('/api/auth/switch-role', methods=['POST'])
def auth_switch_role():
    body = request.get_json(force=True, silent=True) or {}
    target_role = body.get('role', 'Administrator')
    token = request.headers.get('X-Session-Token', '')
    res = db_service.switch_role_session(token, target_role)
    if not res:
        roles = db_service.get_roles()
        role_dict = next((r for r in roles if r['name'] == target_role), None)
        res = {
            'role_name': target_role,
            'full_name': f'AIIA User ({target_role})',
            'permissions': role_dict['permissions'] if role_dict else ['*'],
            'is_authenticated': True,
        }
    return jsonify(res)


@app.route('/api/audit/log', methods=['POST'])
@require_permission('audit:write')
def audit_log():
    body = request.get_json(force=True, silent=True) or {}
    auth = get_auth_context()
    res = db_service.log_audit_event(
        user_name=body.get('user', auth['user_name']),
        role=body.get('role', auth['role']),
        action=body.get('action', 'USER_ACTION'),
        entity=body.get('entity', 'GeneralEntity'),
        entity_id=body.get('entity_id', 'N/A'),
        previous_value=body.get('previous_value', ''),
        new_value=body.get('new_value', ''),
        ip_address=get_client_ip(),
        device_metadata=request.headers.get('User-Agent', 'WebBrowser')[:120],
    )
    return jsonify(res)


@app.route('/api/audit/tamper-demo', methods=['POST'])
@require_permission('audit:admin')
def audit_tamper_demo():
    body = request.get_json(force=True, silent=True) or {}
    event_id = body.get('event_id', 'EVT-0003')
    malicious_val = body.get('malicious_value', 'Tampered enrollment count (UNAUTHORIZED_MUTATION)')
    return jsonify(db_service.tamper_audit_event_demo(event_id, malicious_val))


@app.route('/api/audit/restore-demo', methods=['POST'])
@require_permission('audit:admin')
def audit_restore_demo():
    return jsonify(db_service.restore_audit_chain_demo())


@app.route('/api/interop/fhir/validate', methods=['POST'])
def interop_fhir_validate():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify(db_service.validate_fhir_research_study(body))


@app.route('/api/assistant/query', methods=['POST'])
def assistant_query():
    body = request.get_json(force=True, silent=True) or {}
    user_query = body.get('query', '').strip()
    if not user_query:
        return jsonify({'error': 'Empty query'}), 400
    ans = db_service.query_trial_assistant(user_query)
    auth = get_auth_context()
    db_service.log_audit_event(
        user_name=auth['user_name'],
        role=auth['role'],
        action='ASSISTANT_QUERY',
        entity='TrialAssistant',
        entity_id=ans.get('intent', 'QUERY'),
        previous_value='',
        new_value=user_query[:100],
        ip_address=get_client_ip(),
    )
    return jsonify(ans)


@app.route('/api/alerts/<int:alert_id>/status', methods=['POST'])
@require_permission('alerts:write')
def alerts_status(alert_id):
    body = request.get_json(force=True, silent=True) or {}
    new_status = body.get('status', 'Acknowledged')
    auth = get_auth_context()
    user_name = body.get('user', auth['user_name'])
    try:
        res = db_service.update_alert_status(alert_id, new_status, user_name)
        db_service.log_audit_event(
            user_name=user_name,
            role=auth['role'],
            action='UPDATE_ALERT_STATUS',
            entity='Alert',
            entity_id=str(alert_id),
            previous_value='Active',
            new_value=new_status,
            ip_address=get_client_ip(),
        )
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/documents/upload', methods=['POST'])
@require_permission('documents:write')
def documents_upload():
    body = request.get_json(force=True, silent=True) or {}
    auth = get_auth_context()
    doc_name = body.get('document_name', 'New Institutional Document')
    category = body.get('category', 'Protocol')
    trial_ctri = body.get('trial_ctri', '')
    version = body.get('version', 'v1.0')
    uploaded_by = auth.get('user_name', 'Prof. (Dr.) Tanuja Nesari')
    status = body.get('status', 'Under Review')
    description = body.get('description', '')
    file_name = body.get('file_name', f"{doc_name.replace(' ', '_')}.pdf")
    file_content_raw = body.get('file_content', f"Institutional Record: {doc_name}\nCategory: {category}\nVersion: {version}\n")
    if isinstance(file_content_raw, str):
        file_bytes = file_content_raw.encode('utf-8')
    else:
        file_bytes = bytes(file_content_raw)

    res = db_service.create_document(
        document_name=doc_name, category=category, trial_ctri=trial_ctri,
        version=version, uploaded_by=uploaded_by, status=status,
        description=description, file_name=file_name, file_content_bytes=file_bytes,
    )
    return jsonify(res)


@app.route('/api/documents/<doc_id_str>/version', methods=['POST'])
@require_permission('documents:write')
def documents_version(doc_id_str):
    body = request.get_json(force=True, silent=True) or {}
    auth = get_auth_context()
    version = body.get('version', 'v1.1')
    change_summary = body.get('change_summary', 'Routine periodic version update.')
    uploaded_by = auth.get('user_name', 'Principal Investigator')
    status = body.get('status', 'Approved')
    file_name = body.get('file_name', f'Document_Update_{version}.pdf')
    file_content_raw = body.get('file_content', f"Updated Document Version: {version}\nSummary: {change_summary}\n")
    if isinstance(file_content_raw, str):
        file_bytes = file_content_raw.encode('utf-8')
    else:
        file_bytes = bytes(file_content_raw)

    res = db_service.add_document_version(
        document_id=doc_id_str, version=version, change_summary=change_summary,
        uploaded_by=uploaded_by, status=status, file_name=file_name, file_content_bytes=file_bytes,
    )
    return jsonify(res)


# ===================================================================
# POST ROUTES — AYURCTMS
# ===================================================================

@app.route('/api/ayur/patient/match', methods=['POST'])
def ayur_patient_match():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify(db_service.match_patient_trials(
        condition=body.get('condition', ''),
        accessible_locations=body.get('accessible_locations', []),
        distance_pref=body.get('distance_pref', ''),
        age=body.get('age'),
        gender=body.get('gender'),
    ))


@app.route('/api/ayur/auth/login', methods=['POST'])
def ayur_auth_login():
    body = request.get_json(force=True, silent=True) or {}
    staff_id = body.get('staff_id', body.get('username', '')).strip()
    password = body.get('password', '').strip()

    if (staff_id.upper() == 'AIIA001' and password == 'AIIA@123') or (staff_id.lower() == 'admin' and password == 'admin123'):
        return jsonify({
            'success': True,
            'token': 'ayur-demo-token-998811',
            'user': {
                'staff_id': 'AIIA001',
                'full_name': 'Dr. Research Admin',
                'role': 'AIIA Authorized Staff',
                'designation': 'Clinical Research Coordinator / Admin',
                'institution': 'All India Institute of Ayurveda (AIIA), New Delhi',
            },
            'message': 'Login successful. Welcome to AYURCTMS.',
        })
    return jsonify({
        'success': False,
        'error': 'Invalid Staff ID or Password. Demo credentials: Staff ID: AIIA001, Password: AIIA@123',
    }), 401


@app.route('/api/ayur/trials/create', methods=['POST'])
def ayur_trials_create():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify(db_service.create_ayur_trial(body))


@app.route('/api/ayur/pv/report', methods=['POST'])
def ayur_pv_report():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify(db_service.report_ayur_adverse_event(body))


@app.route('/api/ayur/approvals/update', methods=['POST'])
def ayur_approvals_update():
    body = request.get_json(force=True, silent=True) or {}
    approval_id = body.get('approval_id', '')
    status = body.get('status', 'Approved')
    notes = body.get('notes', 'Reviewed by ethics/regulatory board.')
    reviewed_by = body.get('reviewed_by', 'Ethics Committee Officer')
    return jsonify(db_service.update_ayur_approval(approval_id, status, notes, reviewed_by))


@app.route('/api/ayur/approvals/<approval_id>', methods=['POST'])
def ayur_approvals_by_id(approval_id):
    body = request.get_json(force=True, silent=True) or {}
    status = body.get('status', 'Approved')
    notes = body.get('notes', 'Reviewed by ethics/regulatory board.')
    reviewed_by = body.get('reviewed_by', 'Ethics Committee Officer')
    return jsonify(db_service.update_ayur_approval(approval_id, status, notes, reviewed_by))


@app.route('/api/ayur/gcp/toggle', methods=['POST'])
def ayur_gcp_toggle():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify(db_service.toggle_ayur_gcp_item(
        int(body.get('item_id', 1)),
        int(body.get('is_completed', 1)),
        body.get('reviewed_by', 'Dr. Research Admin'),
    ))


@app.route('/api/ayur/notifications/read', methods=['POST'])
def ayur_notifications_read():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify(db_service.mark_ayur_notification_read(int(body.get('notification_id', 1))))


# ===================================================================
# Static file serving (for production when running behind gunicorn)
# ===================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React frontend from the dist/ directory."""
    dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
    if not path or path == 'index.html':
        return send_from_directory(dist_dir, 'index.html')
    # Try serving static files first
    full_path = os.path.join(dist_dir, path)
    if os.path.isfile(full_path):
        return send_from_directory(dist_dir, path)
    # SPA fallback — serve index.html for any unmatched route
    return send_from_directory(dist_dir, 'index.html')


# ===================================================================
# Entrypoint
# ===================================================================

def create_app():
    """Application factory for gunicorn / testing."""
    db_service.init_indexes()
    return app


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    db_service.init_indexes()
    print(f'AIIA Dashboard Server (Flask) running at http://{HOST}:{PORT}')
    app.run(host=HOST, port=PORT, debug=os.environ.get('FLASK_DEBUG', '0') == '1')
