import pathlib

css_to_append = '''
/* ============================================================
   SECURITY, RBAC & HASH AUDIT STYLES
   ============================================================ */
.audit-verify-bar {
  background: #f8fafc;
  border: 1px solid var(--border-light, #e2e8f0);
  border-radius: var(--radius-sm, 6px);
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.audit-hash-chip {
  font-family: var(--font-mono, monospace);
  font-size: 10px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 2px 6px;
  color: #334155;
  display: inline-block;
  cursor: pointer;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.audit-hash-chip:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
}

.chain-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.chain-status-verified {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.chain-status-tampered {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.role-badge-pill {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

/* ============================================================
   INTEROPERABILITY & FHIR JSON VIEWER STYLES
   ============================================================ */
.fhir-json-box {
  background: #0f172a;
  color: #e2e8f0;
  font-family: var(--font-mono, monospace);
  font-size: 11px;
  line-height: 1.5;
  padding: 16px;
  border-radius: var(--radius-sm, 6px);
  max-height: 480px;
  overflow: auto;
  border: 1px solid #334155;
  white-space: pre-wrap;
  word-break: break-all;
}

.interop-tab-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-light, #e2e8f0);
  padding-bottom: 8px;
}

.interop-tab-btn {
  background: transparent;
  border: none;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary, #64748b);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.interop-tab-btn.active {
  background: var(--bg-surface-elevated, #e2e8f0);
  color: var(--text-primary, #0f172a);
  font-weight: 600;
}

/* ============================================================
   AIIA TRIAL ASSISTANT STYLES
   ============================================================ */
.assistant-shell {
  max-width: 900px;
  margin: 0 auto;
}

.assistant-chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0 16px;
}

.assistant-chip {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 6px 12px;
  font-size: 12px;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.assistant-chip:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
  color: #0f172a;
}

.assistant-input-box {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.assistant-response-card {
  background: var(--bg-surface, #ffffff);
  border: 1px solid var(--border-light, #e2e8f0);
  border-radius: var(--radius-sm, 6px);
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.assistant-metrics-grid {
  display: flex;
  gap: 12px;
  margin: 14px 0;
  flex-wrap: wrap;
}

.assistant-metric-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px 14px;
  min-width: 140px;
}

.assistant-metric-val {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent, #0f766e);
  font-family: var(--font-mono, monospace);
}

.assistant-metric-lbl {
  font-size: 11px;
  color: var(--text-muted, #64748b);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.assistant-source-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #475569;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  margin-top: 10px;
}
'''

fp = pathlib.Path("c:/Users/yoges/Documents/AIIA Dashboard/app.css")
content = fp.read_text(encoding="utf-8")
fp.write_text(content + css_to_append, encoding="utf-8")
print("app.css appended successfully!")
