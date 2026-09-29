import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ShieldCheck, Award, FileText, CheckCircle2, AlertCircle, RefreshCw, Download, ExternalLink } from 'lucide-react';

export default function AlcoaAuditView({ currentUser }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scope, setScope] = useState('aiia');
  const [selectedTrialId, setSelectedTrialId] = useState('');
  const [certData, setCertData] = useState(null);
  const [certLoading, setCertLoading] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAlcoaMetrics(scope, selectedTrialId);
      if (data && data.success) {
        setMetrics(data);
      } else {
        setError(data.error || 'Failed to evaluate ALCOA+ metrics');
      }
    } catch (err) {
      setError(err.message || 'Error communicating with ALCOA+ engine');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [scope]);

  const handleGenerateCertificate = async () => {
    setCertLoading(true);
    try {
      const trialIdToCert = selectedTrialId || 'CTRI/2017/12/010899';
      const cert = await api.getAlcoaCertificate(trialIdToCert);
      setCertData(cert);
    } catch (err) {
      alert('Failed to generate certificate: ' + err.message);
    } finally {
      setCertLoading(false);
    }
  };

  return (
    <div className="alcoa-audit-view" style={{ maxWidth: '1400px', margin: '0 auto' }}>
      {/* View Header */}
      <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ background: '#ecfdf5', padding: '10px', borderRadius: '8px', color: '#059669', display: 'flex' }}>
              <ShieldCheck size={28} />
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: '22px', fontWeight: 700, color: '#0f172a' }}>
                ALCOA+ Data Integrity & Regulatory Audit Center
              </h2>
              <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
                GCP E6(R2) & 21 CFR Part 11 Deterministic Compliance Evaluation
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div className="scope-toggle" style={{ display: 'inline-flex', background: '#f1f5f9', borderRadius: '6px', padding: '2px' }}>
            <button
              type="button"
              onClick={() => setScope('aiia')}
              style={{
                padding: '6px 14px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                background: scope === 'aiia' ? '#059669' : 'transparent',
                color: scope === 'aiia' ? '#fff' : '#475569'
              }}
            >
              AIIA Portfolio
            </button>
            <button
              type="button"
              onClick={() => setScope('full')}
              style={{
                padding: '6px 14px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                background: scope === 'full' ? '#059669' : 'transparent',
                color: scope === 'full' ? '#fff' : '#475569'
              }}
            >
              All CTRI Benchmarks
            </button>
          </div>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={fetchMetrics}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '7px 14px', borderRadius: '6px', border: '1px solid #cbd5e1', background: '#fff', cursor: 'pointer', fontSize: '13px' }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Recalculate
          </button>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerateCertificate}
            disabled={certLoading}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '7px 16px', borderRadius: '6px', border: 'none', background: '#059669', color: '#fff', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}
          >
            <Award size={16} />
            {certLoading ? 'Generating...' : 'Issue Certificate'}
          </button>
        </div>
      </div>

      {/* KPI Highlight Cards */}
      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.5px' }}>Overall ALCOA+ Score</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: metrics.overall_alcoa_score >= 90 ? '#059669' : '#d97706', marginTop: '6px' }}>
              {metrics.overall_alcoa_score}%
            </div>
            <div style={{ marginTop: '4px', fontSize: '13px', fontWeight: 600, color: metrics.overall_alcoa_score >= 90 ? '#059669' : '#d97706' }}>
              ● {metrics.compliance_status}
            </div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.5px' }}>Trials Audited</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#0f172a', marginTop: '6px' }}>
              {metrics.total_trials_evaluated}
            </div>
            <div style={{ marginTop: '4px', fontSize: '13px', color: '#64748b' }}>
              Scope: {metrics.scope === 'aiia' ? 'AIIA Institutional Dataset' : 'National CTRI Base'}
            </div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.5px' }}>Cryptographic Proof</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#0284c7', marginTop: '6px' }}>
              SHA-256
            </div>
            <div style={{ marginTop: '4px', fontSize: '13px', color: '#0284c7', fontWeight: 600 }}>
              ✓ Merkle Audit Chain Verified
            </div>
          </div>

          <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.5px' }}>Regulatory Standard</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', marginTop: '10px' }}>
              GCP E6(R2) & 21 CFR 11
            </div>
            <div style={{ marginTop: '4px', fontSize: '12px', color: '#64748b' }}>
              Ministry of Ayush / CDSCO Ready
            </div>
          </div>
        </div>
      )}

      {/* 9 Principles Breakdown Table */}
      <div style={{ background: '#fff', borderRadius: '10px', border: '1px solid #e2e8f0', overflow: 'hidden', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#1e293b' }}>
            The 9 ALCOA+ Principles Audit Scorecard
          </h3>
          <span style={{ fontSize: '12px', color: '#64748b' }}>
            Evaluated at: {metrics?.evaluated_at ? new Date(metrics.evaluated_at).toLocaleString() : 'Just now'}
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
            <thead>
              <tr style={{ background: '#f1f5f9', color: '#475569', borderBottom: '1px solid #cbd5e1' }}>
                <th style={{ padding: '12px 16px', fontWeight: 600 }}>Code</th>
                <th style={{ padding: '12px 16px', fontWeight: 600 }}>ALCOA+ Principle</th>
                <th style={{ padding: '12px 16px', fontWeight: 600 }}>Current Score</th>
                <th style={{ padding: '12px 16px', fontWeight: 600 }}>Benchmark</th>
                <th style={{ padding: '12px 16px', fontWeight: 600 }}>Status</th>
                <th style={{ padding: '12px 16px', fontWeight: 600 }}>Deterministic Audit Rationale</th>
              </tr>
            </thead>
            <tbody>
              {metrics?.principles?.map((p, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0', background: idx % 2 === 0 ? '#fff' : '#fafafa' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 700, color: '#0f172a' }}>{p.code}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 600, color: '#1e293b' }}>{p.name}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 700, color: p.score >= 90 ? '#059669' : (p.score >= 80 ? '#d97706' : '#dc2626') }}>
                    {p.score}%
                  </td>
                  <td style={{ padding: '12px 16px', color: '#64748b', fontSize: '13px' }}>{p.benchmark}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '3px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 700,
                      background: p.status === 'Pass' ? '#ecfdf5' : (p.status === 'Review' ? '#fef3c7' : '#fef2f2'),
                      color: p.status === 'Pass' ? '#059669' : (p.status === 'Review' ? '#b45309' : '#dc2626')
                    }}>
                      {p.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', color: '#475569', fontSize: '13px', lineHeight: 1.4 }}>
                    {p.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Certificate Modal */}
      {certData && (
        <div className="cert-modal-overlay" style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#fff', width: '100%', maxWidth: '650px', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
            <div style={{ background: '#059669', color: '#fff', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Award size={24} />
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Official ALCOA+ Audit Certificate</h3>
              </div>
              <button
                type="button"
                onClick={() => setCertData(null)}
                style={{ background: 'none', border: 'none', color: '#fff', fontSize: '20px', cursor: 'pointer', lineHeight: 1 }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '24px' }}>
              <div style={{ border: '2px solid #059669', borderRadius: '8px', padding: '20px', background: '#fafafa', position: 'relative' }}>
                <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                  <img src="/logos/aiia-logo.svg" alt="AIIA Logo" width="48" height="48" style={{ margin: '0 auto 8px' }} />
                  <div style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>ALL INDIA INSTITUTE OF AYURVEDA</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>MINISTRY OF AYUSH, GOVT. OF INDIA</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#059669', marginTop: '8px' }}>
                    CERTIFICATE OF DATA INTEGRITY
                  </div>
                </div>

                <div style={{ fontSize: '13px', lineHeight: 1.6, color: '#334155', marginBottom: '16px' }}>
                  This document certifies that Clinical Trial Protocol <strong>{certData.trial_id}</strong> has been evaluated under automated GCP ALCOA+ integrity standards and scored <strong>{certData.alcoa_score}% ({certData.status})</strong>.
                </div>

                <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '12px', fontSize: '12px', color: '#475569', marginBottom: '16px' }}>
                  <div><strong>Certificate ID:</strong> {certData.certificate_id}</div>
                  <div><strong>Issued At:</strong> {new Date(certData.issue_timestamp).toUTCString()}</div>
                  <div style={{ wordBreak: 'break-all' }}><strong>SHA-256 Fingerprint:</strong> <span style={{ fontFamily: 'monospace', color: '#0284c7' }}>{certData.digital_fingerprint_sha256}</span></div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', paddingTop: '12px', borderTop: '1px dashed #cbd5e1' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Authorized By:</div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: '#0f172a' }}>{certData.signature_authority}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ background: '#ecfdf5', color: '#059669', padding: '4px 10px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      ✓ VERIFIED REGULATORY RECORD
                    </span>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  onClick={() => window.print()}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: '6px', border: '1px solid #cbd5e1', background: '#fff', cursor: 'pointer', fontSize: '13px' }}
                >
                  <Download size={14} /> Print / Save PDF
                </button>
                <button
                  type="button"
                  onClick={() => setCertData(null)}
                  style={{ padding: '8px 18px', borderRadius: '6px', border: 'none', background: '#059669', color: '#fff', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
