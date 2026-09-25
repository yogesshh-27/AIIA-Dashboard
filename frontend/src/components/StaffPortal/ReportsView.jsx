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
      setLoading(true);
      setError(null);
      const res = await api.getReportData(type);
      setReportData(res);
    } catch (err) {
      setError(err.message || 'Failed to generate report');
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

  return (
    <div className="reports-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Clinical Trial & Governance Reports</h2>
          <p>Institutional summaries for AIIA Leadership, Ethics Committees, and Regulators</p>
        </div>
      </div>

      {/* Report Switcher Tabs */}
      <div className="flex gap-2 mb-4 flex-wrap">
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
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Generating Institutional Report...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : reportData ? (
        <div className="active-trials-section-card bg-white rounded-lg border shadow-xs p-5">
          <div className="flex flex-wrap justify-between items-center gap-3 mb-4 pb-3 border-b">
            <div>
              <h4 className="text-base font-bold text-slate-900">{reportData.report_title}</h4>
              <span className="text-muted text-xs">
                Generated: {reportData.generated_at} • Institution: {reportData.institution}
              </span>
            </div>
            <div className="flex gap-2">
              <a
                href={`/api/ayur/reports/export?type=${reportType}&format=csv`}
                className="btn btn-outline btn-sm flex items-center gap-1.5"
                download
              >
                <Download size={14} />
                <span>EXPORT CSV</span>
              </a>
              <button
                className="btn btn-primary btn-sm flex items-center gap-1.5"
                onClick={handlePrint}
              >
                <Printer size={14} />
                <span>PRINT / PDF</span>
              </button>
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  {(reportData.columns || []).map((col, idx) => (
                    <th key={idx}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(reportData.rows || []).map((row, rIdx) => (
                  <tr key={rIdx}>
                    {(reportData.columns || []).map((col, cIdx) => (
                      <td key={cIdx}>{row[col] !== undefined ? String(row[col]) : ''}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
