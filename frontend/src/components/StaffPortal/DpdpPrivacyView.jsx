import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Lock, FileCheck, Shield, AlertCircle, RefreshCw, UserCheck, UserX, Globe, CheckCircle2 } from 'lucide-react';

export default function DpdpPrivacyView({ currentUser }) {
  const [dpoLog, setDpoLog] = useState(null);
  const [notice, setNotice] = useState(null);
  const [noticeLang, setNoticeLang] = useState('en');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // New consent form state
  const [newSubjectId, setNewSubjectId] = useState('SUBJ-005');
  const [newAbhaId, setNewAbhaId] = useState('91-4521-8890-1122');
  const [newTrialId, setNewTrialId] = useState('CTRI/2017/12/010899');
  const [actionMsg, setActionMsg] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [logData, noticeData] = await Promise.all([
        api.getDpoAuditLog(),
        api.getPrivacyNotice(noticeLang)
      ]);
      setDpoLog(logData);
      setNotice(noticeData);
    } catch (err) {
      setError(err.message || 'Error loading DPDP governance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [noticeLang]);

  const handleGrantConsent = async (e) => {
    e.preventDefault();
    setActionMsg('');
    try {
      const res = await api.recordDpdpConsent({
        trial_id: newTrialId,
        subject_id: newSubjectId,
        abha_id: newAbhaId,
        language: noticeLang,
        purposes_granted: ['CLINICAL_EVALUATION', 'PRAKRITI_DOSHA_STRATIFICATION', 'PHARMACOVIGILANCE_REPORTING']
      });
      if (res.success) {
        setActionMsg(`Consent tokenized: ${res.consent.consent_id}`);
        await loadData();
      }
    } catch (err) {
      alert('Failed to grant consent: ' + err.message);
    }
  };

  const handleWithdrawConsent = async (consentId) => {
    if (!window.confirm(`Revoke consent for ${consentId} under DPDP Section 6(4)?`)) return;
    try {
      const res = await api.withdrawDpdpConsent(consentId, 'Participant requested revocation');
      if (res.success) {
        setActionMsg(`Consent ${consentId} successfully revoked.`);
        await loadData();
      }
    } catch (err) {
      alert('Failed to revoke consent: ' + err.message);
    }
  };

  return (
    <div className="dpdp-privacy-view" style={{ maxWidth: '1400px', margin: '0 auto' }}>
      {/* View Header */}
      <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ background: '#f0fdf4', padding: '10px', borderRadius: '8px', color: '#16a34a', display: 'flex' }}>
              <Lock size={28} />
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: '#0f172a' }}>
                DPDP Act (2023) Privacy & Consent Governance
              </h2>
              <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
                Digital Personal Data Protection Act, 2023 — Data Principal Rights & DPO Oversight
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div className="lang-toggle" style={{ display: 'inline-flex', background: '#f1f5f9', borderRadius: '6px', padding: '2px' }}>
            <button
              type="button"
              onClick={() => setNoticeLang('en')}
              style={{
                padding: '6px 14px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                background: noticeLang === 'en' ? '#16a34a' : 'transparent',
                color: noticeLang === 'en' ? '#fff' : '#475569'
              }}
            >
              English Notice
            </button>
            <button
              type="button"
              onClick={() => setNoticeLang('hi')}
              style={{
                padding: '6px 14px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                background: noticeLang === 'hi' ? '#16a34a' : 'transparent',
                color: noticeLang === 'hi' ? '#fff' : '#475569'
              }}
            >
              हिन्दी सूचना
            </button>
          </div>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={loadData}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '7px 14px', borderRadius: '6px', border: '1px solid #cbd5e1', background: '#fff', cursor: 'pointer', fontSize: '13px' }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {actionMsg && (
        <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', color: '#065f46', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
          <CheckCircle2 size={18} />
          {actionMsg}
        </div>
      )}

      {/* Summary KPI Cards */}
      {dpoLog && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b' }}>Active Consents</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#16a34a', marginTop: '6px' }}>
              {dpoLog.total_active_consents}
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>Tokenized & Purpose-Limited</div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b' }}>Withdrawn Consents</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#d97706', marginTop: '6px' }}>
              {dpoLog.total_withdrawn_consents}
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>Masked under Section 6(4)</div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b' }}>Rights Requests</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#0284c7', marginTop: '6px' }}>
              {dpoLog.rights_requests?.length || 0}
            </div>
            <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>Access / Correction / Erasure</div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b' }}>DPO Compliance</div>
            <div style={{ fontSize: '16px', fontWeight: 800, color: '#16a34a', marginTop: '10px' }}>
              FULLY COMPLIANT
            </div>
            <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>Act No. 22 of 2023</div>
          </div>
        </div>
      )}

      {/* Multilingual Notice Box */}
      {notice && (
        <div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '20px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Globe size={18} color="#16a34a" />
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
              {notice.title}
            </h3>
          </div>
          <div style={{ fontSize: '13px', color: '#475569', marginBottom: '12px' }}>
            <strong>Data Fiduciary:</strong> {notice.data_fiduciary} | <strong>DPO:</strong> {notice.dpo_contact}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '13px', color: '#1e293b', marginBottom: '8px' }}>Specified Purposes:</div>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: '#475569', lineHeight: 1.5 }}>
                {notice.specified_purposes?.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>

            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '13px', color: '#1e293b', marginBottom: '8px' }}>Data Principal Rights:</div>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: '#475569', lineHeight: 1.5 }}>
                {notice.data_principal_rights?.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          </div>

          <div style={{ marginTop: '14px', fontSize: '12px', color: '#64748b', fontStyle: 'italic', borderTop: '1px solid #f1f5f9', paddingTop: '10px' }}>
            {notice.withdrawal_clause}
          </div>
        </div>
      )}

      {/* Consent Artifacts Table */}
      <div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #e2e8f0', overflow: 'hidden', marginBottom: '24px' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#1e293b' }}>
            Active Consent Registry & Token Chain
          </h3>
          <span style={{ fontSize: '12px', color: '#64748b' }}>
            Cryptographically Chained Consent Tokens
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: '#f1f5f9', color: '#475569' }}>
                <th style={{ padding: '10px 14px' }}>Consent ID</th>
                <th style={{ padding: '10px 14px' }}>Subject ID</th>
                <th style={{ padding: '10px 14px' }}>ABHA Number</th>
                <th style={{ padding: '10px 14px' }}>Trial ID</th>
                <th style={{ padding: '10px 14px' }}>Purposes Granted</th>
                <th style={{ padding: '10px 14px' }}>Status</th>
                <th style={{ padding: '10px 14px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {dpoLog?.consent_records?.map((c, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '10px 14px', fontWeight: 600, color: '#0f172a' }}>{c.consent_id}</td>
                  <td style={{ padding: '10px 14px', color: '#334155' }}>{c.subject_id}</td>
                  <td style={{ padding: '10px 14px', color: '#0284c7', fontFamily: 'monospace' }}>{c.abha_id || 'N/A'}</td>
                  <td style={{ padding: '10px 14px', color: '#475569' }}>{c.trial_id}</td>
                  <td style={{ padding: '10px 14px', color: '#64748b' }}>
                    {Array.isArray(c.purposes_granted) ? c.purposes_granted.join(', ') : c.purposes_granted}
                  </td>
                  <td style={{ padding: '10px 14px' }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 700,
                      background: c.status === 'ACTIVE' ? '#ecfdf5' : '#fef2f2',
                      color: c.status === 'ACTIVE' ? '#16a34a' : '#dc2626'
                    }}>
                      {c.status}
                    </span>
                  </td>
                  <td style={{ padding: '10px 14px' }}>
                    {c.status === 'ACTIVE' && (
                      <button
                        type="button"
                        onClick={() => handleWithdrawConsent(c.consent_id)}
                        style={{ background: '#fee2e2', color: '#dc2626', border: '1px solid #fca5a5', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', fontWeight: 600 }}
                      >
                        Revoke Consent
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
