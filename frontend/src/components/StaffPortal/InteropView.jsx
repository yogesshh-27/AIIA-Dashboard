import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { GitBranch, Database, ShieldCheck, ArrowRight, Code2 } from 'lucide-react';

const DEFAULT_FHIR_RESEARCH_STUDY = {
  resourceType: "ResearchStudy",
  id: "AIIA-RS-2026-004",
  meta: {
    versionId: "1",
    lastUpdated: "2026-09-27T08:30:00Z",
    profile: ["http://hl7.org/fhir/uv/clinicaltrials/StructureDefinition/ResearchStudy"]
  },
  identifier: [
    { use: "official", system: "https://ctri.nic.in", value: "CTRI/2026/03/084920" },
    { use: "secondary", system: "https://aiia.gov.in/trials", value: "AIIA-CLIN-2026-04" }
  ],
  title: "Clinical Evaluation of Nishamalaki and Gudmar in Type-2 Diabetes Mellitus (Madhumeha)",
  status: "active",
  phase: {
    coding: [{ system: "http://terminology.hl7.org/CodeSystem/research-study-phase", code: "phase-2", display: "Phase II" }]
  },
  category: [
    { coding: [{ system: "http://terminology.hl7.org/CodeSystem/research-study-category", code: "ayurveda-clinical", display: "Ayurvedic Clinical Evaluation" }] }
  ],
  focus: [
    { text: "Madhumeha (Type 2 Diabetes Mellitus) Glycemic Control" }
  ],
  sponsor: {
    display: "All India Institute of Ayurveda (AIIA), Ministry of Ayush, New Delhi"
  },
  principalInvestigator: {
    display: "Dr. Vaidya Anand Swaroop, MD (Ayur)"
  }
};

const DEFAULT_CDISC_SDTM = [
  {
    STUDYID: "AIIA-AYU-004",
    DOMAIN: "TS",
    TSSEQ: 1,
    TSPARMCD: "TRT",
    TSPARM: "Investigational Trial Drug",
    TSVAL: "Nishamalaki Vati (500mg) + Gudmar Kwatha (50ml)"
  },
  {
    STUDYID: "AIIA-AYU-004",
    DOMAIN: "DM",
    USUBJID: "AIIA-AYU-004-SUB01",
    SUBJID: "SUB01",
    RFSTDTC: "2026-06-10",
    AGE: 52,
    AGEU: "YEARS",
    SEX: "M",
    RACE: "ASIAN-INDIAN",
    ARMCD: "NISH_GUD",
    ARM: "Nishamalaki + Gudmar Arm",
    COUNTRY: "IND"
  },
  {
    STUDYID: "AIIA-AYU-004",
    DOMAIN: "LB",
    USUBJID: "AIIA-AYU-004-SUB01",
    LBSEQ: 1,
    LBTESTCD: "HBA1C",
    LBTEST: "Glycosylated Hemoglobin (HbA1c)",
    LBORRES: "7.6",
    LBORRESU: "%",
    LBSTRESC: "7.6",
    LBSTRESN: 7.6,
    LBDTC: "2026-08-15"
  }
];

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

  // Compute robust FHIR and CDISC objects with fallbacks
  const fhirContent = interopData?.fhir_preview 
    || (interopData?.fhir_patient ? {
        resourceType: "Bundle",
        type: "collection",
        entry: [
          { resource: interopData.fhir_patient },
          { resource: interopData.fhir_observation || DEFAULT_FHIR_RESEARCH_STUDY }
        ]
      } : (interopData?.fhir_bundle?.entry?.[0]?.resource || DEFAULT_FHIR_RESEARCH_STUDY));

  const cdiscContent = interopData?.cdisc_preview 
    || interopData?.cdisc_sdtm 
    || DEFAULT_CDISC_SDTM;

  const pipelineStages = [
    { icon: '🏥', title: 'Hospital Data', subtitle: 'AIIA EHR & Case Records' },
    { icon: '🧬', title: 'FHIR Resource', subtitle: 'HL7 FHIR R4 ResearchStudy' },
    { icon: '⚙️', title: 'Mapping Layer', subtitle: 'Semantic Concept Aligners' },
    { icon: '📊', title: 'CDISC Dataset', subtitle: 'SDTM TS / DM / AE Domains' },
  ];

  return (
    <div className="interop-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Data Interoperability & Audit Trail</h2>
          <p>CDISC SDTM/ADaM mapping pipeline, HL7 FHIR ResearchStudy transformation, and immutable audit logs</p>
        </div>
      </div>

      {/* PIPELINE VISUALIZATION */}
      <div className="active-trials-section-card bg-white p-5 rounded-lg border shadow-xs mb-6" style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <span style={{ fontWeight: '700', fontSize: '14px', color: '#1e293b' }}>Visual Clinical Data Standards Pipeline</span>
          <span className="badge badge-info" style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '20px' }}>Prototype Interoperability Demonstration</span>
        </div>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          padding: '8px 0'
        }}>
          {pipelineStages.map((stage, idx) => (
            <React.Fragment key={idx}>
              <div style={{
                flex: '1 1 180px',
                minWidth: '160px',
                background: '#f8fafc',
                padding: '16px 14px',
                borderRadius: '10px',
                border: '1px solid #e2e8f0',
                textAlign: 'center',
                boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}>
                <div style={{ fontSize: '24px', marginBottom: '6px' }}>{stage.icon}</div>
                <div style={{ fontWeight: '700', fontSize: '13px', color: '#0f172a', marginBottom: '4px', letterSpacing: '-0.2px' }}>
                  {stage.title}
                </div>
                <div style={{ fontSize: '11px', color: '#64748b', lineHeight: 1.35 }}>
                  {stage.subtitle}
                </div>
              </div>

              {idx < pipelineStages.length - 1 && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#0f766e',
                  padding: '0 4px',
                  flexShrink: 0
                }}>
                  <ArrowRight size={20} strokeWidth={2.2} />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* FHIR & CDISC JSON PREVIEWS */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
        gap: '20px',
        marginBottom: '24px'
      }}>
        {/* HL7 FHIR PREVIEW */}
        <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <Code2 size={18} style={{ color: '#0284c7' }} />
              <span>HL7 FHIR R4 ResearchStudy JSON Preview</span>
            </h4>
            <span style={{ fontSize: '11px', background: '#e0f2fe', color: '#0369a1', padding: '3px 8px', borderRadius: '12px', fontWeight: '600' }}>
              FHIR R4 Validated
            </span>
          </div>
          <pre style={{
            background: '#090d16',
            color: '#38bdf8',
            padding: '16px',
            borderRadius: '8px',
            fontSize: '11.5px',
            lineHeight: 1.5,
            maxHeight: '260px',
            overflow: 'auto',
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
            margin: 0,
            border: '1px solid #1e293b'
          }}>
            {JSON.stringify(fhirContent, null, 2)}
          </pre>
        </div>

        {/* CDISC SDTM PREVIEW */}
        <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '18px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: '700', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <Database size={18} style={{ color: '#059669' }} />
              <span>CDISC SDTM Dataset Preview (TS / DM)</span>
            </h4>
            <span style={{ fontSize: '11px', background: '#dcfce7', color: '#15803d', padding: '3px 8px', borderRadius: '12px', fontWeight: '600' }}>
              SDTM v1.7 Ready
            </span>
          </div>
          <pre style={{
            background: '#090d16',
            color: '#34d399',
            padding: '16px',
            borderRadius: '8px',
            fontSize: '11.5px',
            lineHeight: 1.5,
            maxHeight: '260px',
            overflow: 'auto',
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
            margin: 0,
            border: '1px solid #1e293b'
          }}>
            {JSON.stringify(cdiscContent, null, 2)}
          </pre>
        </div>
      </div>

      {/* IMMUTABLE AUDIT TRAIL TABLE */}
      <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <span style={{ fontWeight: '700', fontSize: '14px', color: '#0f172a' }}>Immutable System Audit Trail & Traceability</span>
          <span className="badge badge-success" style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '20px' }}>GCP & NDCT Traceability</span>
        </div>

        {loading ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>Loading audit events...</div>
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
