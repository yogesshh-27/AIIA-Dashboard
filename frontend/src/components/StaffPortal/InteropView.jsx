import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { GitBranch, Database, ShieldCheck, ArrowRight, Code2 } from 'lucide-react';

export default function InteropView() {
  const [interopData, setInteropData] = useState(null);
  const [auditData, setAuditData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [interopRes, auditRes] = await Promise.all([
          api.getInteropDemo(),
          api.getAuditTrail(),
        ]);
        setInteropData(interopRes);
        setAuditData(auditRes.audit_trail || []);
      } catch (err) {
        setError(err.message || 'Failed to load interoperability and audit data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="interop-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Data Interoperability & Audit Trail</h2>
          <p>CDISC SDTM/ADaM mapping pipeline, HL7 FHIR ResearchStudy transformation, and immutable audit logs</p>
        </div>
      </div>

      {/* PIPELINE VISUALIZATION */}
      <div className="active-trials-section-card bg-white p-5 rounded-lg border shadow-xs mb-6">
        <div className="section-card-header mb-4">
          <span className="section-card-title font-bold text-sm">Visual Clinical Data Standards Pipeline</span>
          <span className="badge badge-info text-xs">Prototype Interoperability Demonstration</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-7 items-center gap-2 my-4 text-center">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <div className="text-2xl mb-1">🏥</div>
            <strong className="text-xs text-slate-800 block">Hospital Data</strong>
            <span className="text-[11px] text-slate-500">AIIA EHR & Case Records</span>
          </div>

          <div className="flex justify-center text-emerald-700 font-bold">
            <ArrowRight size={20} className="hidden md:block" />
            <span className="md:hidden">↓</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <div className="text-2xl mb-1">🧬</div>
            <strong className="text-xs text-slate-800 block">FHIR Resource</strong>
            <span className="text-[11px] text-slate-500">HL7 FHIR R4 ResearchStudy</span>
          </div>

          <div className="flex justify-center text-emerald-700 font-bold">
            <ArrowRight size={20} className="hidden md:block" />
            <span className="md:hidden">↓</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <div className="text-2xl mb-1">⚙️</div>
            <strong className="text-xs text-slate-800 block">Mapping Layer</strong>
            <span className="text-[11px] text-slate-500">Semantic Concept Aligners</span>
          </div>

          <div className="flex justify-center text-emerald-700 font-bold">
            <ArrowRight size={20} className="hidden md:block" />
            <span className="md:hidden">↓</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <div className="text-2xl mb-1">📊</div>
            <strong className="text-xs text-slate-800 block">CDISC Dataset</strong>
            <span className="text-[11px] text-slate-500">SDTM TS / DM / AE Domains</span>
          </div>
        </div>
      </div>

      {/* FHIR & CDISC JSON PREVIEWS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="active-trials-section-card bg-white p-4 rounded-lg border shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-2 flex items-center gap-1.5">
            <Code2 size={16} className="text-sky-600" />
            <span>HL7 FHIR R4 ResearchStudy JSON Preview</span>
          </h4>
          <pre className="bg-slate-900 text-sky-400 p-3 rounded text-[11px] max-h-60 overflow-auto font-mono">
            {interopData?.fhir_preview
              ? JSON.stringify(interopData.fhir_preview, null, 2)
              : '// Loading FHIR Resource...'}
          </pre>
        </div>

        <div className="active-trials-section-card bg-white p-4 rounded-lg border shadow-xs">
          <h4 className="text-xs font-bold text-slate-800 mb-2 flex items-center gap-1.5">
            <Database size={16} className="text-emerald-600" />
            <span>CDISC SDTM Dataset Preview (TS / DM)</span>
          </h4>
          <pre className="bg-slate-900 text-emerald-400 p-3 rounded text-[11px] max-h-60 overflow-auto font-mono">
            {interopData?.cdisc_preview
              ? JSON.stringify(interopData.cdisc_preview, null, 2)
              : '// Loading CDISC Dataset...'}
          </pre>
        </div>
      </div>

      {/* IMMUTABLE AUDIT TRAIL TABLE */}
      <div className="active-trials-section-card bg-white p-5 rounded-lg border shadow-xs">
        <div className="flex justify-between items-center mb-3">
          <span className="font-bold text-sm text-slate-900">Immutable System Audit Trail & Traceability</span>
          <span className="badge badge-success text-xs">GCP & NDCT Traceability</span>
        </div>

        {loading ? (
          <div className="p-4 text-center text-slate-500 text-xs">Loading audit events...</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Audit ID</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Module</th>
                  <th>Previous Value</th>
                  <th>New Value</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {auditData.map((a) => (
                  <tr key={a.audit_id}>
                    <td>
                      <span className="trial-id-badge">{a.audit_id}</span>
                    </td>
                    <td>
                      <strong>{a.user_name}</strong>
                    </td>
                    <td>{a.action}</td>
                    <td>
                      <span className="badge badge-neutral">{a.module}</span>
                    </td>
                    <td className="text-muted text-xs">{a.previous_value}</td>
                    <td className="font-semibold text-xs text-slate-800">{a.new_value}</td>
                    <td className="text-xs whitespace-nowrap">{a.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
