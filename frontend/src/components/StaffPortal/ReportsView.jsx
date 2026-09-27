import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { FileText, Download, Printer, FileSpreadsheet } from 'lucide-react';

export default function ReportsView() {
  const [reportType, setReportType] = useState('trial_progress');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reportButtons = [
    { id: 'trial_progress', label: '1. Trial Progress' },
    { id: 'patient_enrollment', label: '2. Patient Enrollment' },
    { id: 'site_performance', label: '3. Site Performance' },
    { id: 'doctor_participation', label: '4. Doctor Participation' },
    { id: 'adverse_event', label: '5. Adverse Events' },
    { id: 'pending_approval', label: '6. Approvals' },
    { id: 'gcp_compliance', label: '7. GCP Compliance' },
  ];

  const fetchReport = async (type) => {
    try {
      if (!reportData) setLoading(true);
      setError(null);
      const res = await api.getReportData(type);
      if (res) setReportData(res);
    } catch (err) {
      if (!reportData) setError(err.message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(reportType);
  }, [reportType]);

  const handlePrint = () => {
    window.print();
  };

  const currentButtonLabel = reportButtons.find((b) => b.id === reportType)?.label || 'Clinical Trial Report';
  const reportTitle = reportData?.report_title || reportData?.title || `${currentButtonLabel.replace(/^\d+\.\s*/, '')} Report`;
  const generatedAt = reportData?.generated_at || reportData?.date || new Date().toISOString().split('T')[0];
  const institution = reportData?.institution || 'All India Institute of Ayurveda (AIIA), New Delhi';

  const columns = reportData?.columns && reportData.columns.length > 0
    ? reportData.columns
    : (reportData?.rows && reportData.rows[0] ? Object.keys(reportData.rows[0]) : ['Trial ID', 'Title', 'Status']);

  const rows = reportData?.rows || reportData?.records || reportData?.data || [];

  return (
    <div className="reports-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Clinical Trial & Governance Reports</h2>
          <p>Institutional summaries for AIIA Leadership, Ethics Committees, and Regulators</p>
        </div>
      </div>

      {/* Report Switcher Tabs */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        marginBottom: '16px'
      }}>
        {reportButtons.map((btn) => (
          <button
            key={btn.id}
            className={`btn btn-sm ${
              reportType === btn.id ? 'btn-primary' : 'btn-outline'
            }`}
            onClick={() => setReportType(btn.id)}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500" style={{ padding: '32px', textAlign: 'center' }}>
          <div className="badge badge-info animate-pulse" style={{ padding: '8px 16px', fontSize: '13px' }}>
            Generating Institutional Report...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger" style={{ padding: '10px 16px', fontSize: '13px', marginBottom: '16px' }}>{error}</div>
      ) : (
        <div className="active-trials-section-card bg-white rounded-lg border shadow-xs" style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px' }}>
          {/* Header toolbar */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '18px',
            paddingBottom: '16px',
            borderBottom: '1px solid #e2e8f0'
          }}>
            <div>
              <h4 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a', margin: '0 0 6px 0', letterSpacing: '-0.2px' }}>
                {reportTitle}
              </h4>
              <div style={{ fontSize: '12.5px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span><strong>Generated:</strong> {generatedAt}</span>
                <span>•</span>
                <span><strong>Institution:</strong> {institution}</span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <a
                href={`/api/ayur/reports/export?type=${reportType}&format=csv`}
                className="btn btn-outline btn-sm"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontWeight: '600' }}
                download
              >
                <Download size={14} />
                <span>EXPORT CSV</span>
              </a>
              <button
                className="btn btn-primary btn-sm"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontWeight: '600' }}
                onClick={handlePrint}
              >
                <Printer size={14} />
                <span>PRINT / PDF</span>
              </button>
            </div>
          </div>

          {/* Data Table */}
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  {columns.map((col, idx) => (
                    <th key={idx}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                      No records found for this reporting domain.
                    </td>
                  </tr>
                ) : (
                  rows.map((row, rIdx) => (
                    <tr key={rIdx}>
                      {columns.map((col, cIdx) => {
                        const keys = Object.keys(row);
                        const val = row[col] !== undefined
                          ? row[col]
                          : (row[keys[cIdx]] !== undefined ? row[keys[cIdx]] : '');
                        
                        return (
                          <td key={cIdx}>
                            {cIdx === 0 ? (
                              <span className="trial-id-badge" style={{ fontSize: '11px', whiteSpace: 'nowrap' }}>
                                {String(val)}
                              </span>
                            ) : typeof val === 'boolean' ? (
                              <span className={`badge ${val ? 'badge-success' : 'badge-danger'}`} style={{ fontSize: '10px' }}>
                                {val ? 'Completed' : 'Pending'}
                              </span>
                            ) : (
                              String(val)
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
