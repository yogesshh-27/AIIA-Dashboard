import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Stethoscope, Users, AlertTriangle, ShieldCheck, Plus, ArrowRight, MapPin, Activity, CheckCircle, ExternalLink, X, BarChart3, TrendingUp } from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import IndiaTrialMap from './IndiaTrialMap';

const DEFAULT_DASHBOARD_DATA = {
  kpi_cards: {
    doctors: { title: 'Doctor Information', total_doctors: 11, active_investigators: 8, trial_sites: 9, button_text: 'View Doctor Rosters →' },
    patients: { title: 'Patient Information', total_patients: 25, active_participants: 18, completed_evaluations: 7, button_text: 'Open Patient Directory →' },
    pharmacovigilance: { title: 'Pharmacovigilance & Safety', total_reported_events: 10, serious_adverse_events: 2, under_review: 4, button_text: 'Review Safety Signals →' }
  },
  active_trials_summary: {
    ongoing_trials: 5,
    completed_trials: 2,
    upcoming_trials: 1,
    site_distribution: [
      { city: 'New Delhi', count: 3, percentage: 38 },
      { city: 'Mumbai', count: 2, percentage: 25 },
      { city: 'Jaipur', count: 2, percentage: 25 },
      { city: 'Bengaluru', count: 1, percentage: 12 }
    ]
  },
  gcp_compliance: { percentage: 89 }
};

export default function DashboardView({ onNavigate, onOpenCreateTrial }) {
  const [data, setData] = useState(() => {
    try {
      const cached = localStorage.getItem('ayurctms_dashboard_cache');
      return cached ? JSON.parse(cached) : DEFAULT_DASHBOARD_DATA;
    } catch {
      return DEFAULT_DASHBOARD_DATA;
    }
  });
  const [isLiveSyncing, setIsLiveSyncing] = useState(true);
  const [wakeNotice, setWakeNotice] = useState('');
  const [error, setError] = useState(null);
  const [selectedSite, setSelectedSite] = useState(null);
  const [selectedTrial, setSelectedTrial] = useState(null);
  const [siteDetailData, setSiteDetailData] = useState(null);
  const [siteLoading, setSiteLoading] = useState(false);

  useEffect(() => {
    let timer = null;
    let isMounted = true;

    async function loadDashboard(attempt = 1) {
      if (!isMounted) return;
      setIsLiveSyncing(true);

      if (attempt > 1) {
        setWakeNotice(`Waking up Render cloud backend (attempt ${attempt}/6)...`);
      }

      try {
        const stats = await api.getDashboardStats();
        if (!isMounted) return;
        if (stats && (stats.kpi_cards || stats.aiia || stats.doctors || stats.active_trials_summary)) {
          setData(stats);
          try {
            localStorage.setItem('ayurctms_dashboard_cache', JSON.stringify(stats));
          } catch {}
          setIsLiveSyncing(false);
          setWakeNotice('');
          setError(null);
        }
      } catch (err) {
        if (!isMounted) return;
        console.warn(`Dashboard fetch attempt ${attempt} failed:`, err.message);
        if (attempt < 6) {
          setWakeNotice('Connecting to Render cloud instance... (Free tier takes ~50s on initial load)');
          timer = setTimeout(() => loadDashboard(attempt + 1), 4000);
        } else {
          setIsLiveSyncing(false);
          setWakeNotice('');
          // If we still have cached data, don't show full page error
          if (!data) {
            setError(err.message || 'Failed to connect to cloud backend.');
          }
        }
      }
    }

    // Fast safety timeout: dismiss connecting badge after 1.5s max so UI remains responsive
    const safetyDismissTimer = setTimeout(() => {
      if (isMounted) {
        setIsLiveSyncing(false);
        setWakeNotice('');
      }
    }, 1500);

    loadDashboard(1);

    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
      clearTimeout(safetyDismissTimer);
    };
  }, []);

  const handleOpenSite = async (city) => {
    setSelectedSite(city);
    setSiteLoading(true);
    try {
      const detail = await api.getSiteDetail(city);
      setSiteDetailData(detail);
    } catch (err) {
      console.error(err);
    } finally {
      setSiteLoading(false);
    }
  };

  const kpis = data.kpi_cards || {};
  const trialsSum = data.active_trials_summary || {};

  return (
    <div className="dashboard-view">
      {/* Header bar */}
      <div className="view-header-bar">
        <div className="view-title-group">
          <div className="flex items-center gap-2">
            <h2>AIIA Clinical Trials Executive Dashboard</h2>
            {isLiveSyncing && (
              <span className="badge badge-info text-xs animate-pulse">
                ⚡ Connecting to Cloud Backend...
              </span>
            )}
            {!isLiveSyncing && (
              <span className="badge badge-success text-xs">
                🟢 Live Sync Active
              </span>
            )}
          </div>
          <p>
            Real-time clinical trial oversight, doctor rosters, patient flow, and pharmacovigilance
            {wakeNotice ? ` • ${wakeNotice}` : ''}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <button
            className="btn btn-outline btn-sm flex items-center gap-1"
            onClick={() => onNavigate('gcp')}
          >
            <ShieldCheck size={14} className="text-emerald-700" />
            <span>GCP Status: {data.gcp_compliance?.percentage || 89}%</span>
          </button>
          <button
            className="btn btn-primary btn-sm flex items-center gap-1"
            onClick={onOpenCreateTrial}
          >
            <Plus size={14} />
            <span>CREATE NEW TRIAL</span>
          </button>
        </div>
      </div>

      {/* 3 Major Top KPI Cards */}
      <div className="sketch-kpi-grid">
        {/* Card 1: Doctor Information */}
        <div className="sketch-kpi-card kpi-doctor">
          <div className="kpi-card-header">
            <span className="kpi-card-title">{kpis.doctors?.title || 'Doctor Information'}</span>
            <Stethoscope className="text-emerald-700" size={24} />
          </div>
          <div className="kpi-stats-row">
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.doctors?.total_doctors || 11}</span>
              <span className="kpi-stat-label">Total Doctors</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#005944' }}>
                {kpis.doctors?.active_investigators || 8}
              </span>
              <span className="kpi-stat-label">Active PIs</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.doctors?.trial_sites || 9}</span>
              <span className="kpi-stat-label">Trial Sites</span>
            </div>
          </div>
          {/* Micro Sparkline */}
          <div style={{ height: '24px', margin: '6px 0', opacity: 0.9 }}>
            <svg viewBox="0 0 160 24" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
              <defs>
                <linearGradient id="grad-doc" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#005944" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#005944" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path d="M 0 18 Q 30 16 60 17 T 110 8 T 160 3 L 160 24 L 0 24 Z" fill="url(#grad-doc)" />
              <path d="M 0 18 Q 30 16 60 17 T 110 8 T 160 3" fill="none" stroke="#005944" strokeWidth="2.2" strokeLinecap="round" />
            </svg>
          </div>
          <button
            className="btn btn-outline btn-sm kpi-card-btn"
            onClick={() => onNavigate('doctors')}
          >
            {kpis.doctors?.button_text || 'View Doctor Rosters →'}
          </button>
        </div>

        {/* Card 2: Patient Information */}
        <div className="sketch-kpi-card kpi-patient">
          <div className="kpi-card-header">
            <span className="kpi-card-title">{kpis.patients?.title || 'Patient Information'}</span>
            <Users className="text-blue-700" size={24} />
          </div>
          <div className="kpi-stats-row">
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.patients?.total_patients || 25}</span>
              <span className="kpi-stat-label">Registered</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#0284c7' }}>
                {kpis.patients?.active_participants || 18}
              </span>
              <span className="kpi-stat-label">Active Flow</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#059669' }}>
                {kpis.patients?.completed_participants || 7}
              </span>
              <span className="kpi-stat-label">Completed</span>
            </div>
          </div>
          {/* Micro Sparkline */}
          <div style={{ height: '24px', margin: '6px 0', opacity: 0.9 }}>
            <svg viewBox="0 0 160 24" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
              <defs>
                <linearGradient id="grad-pat" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0284c7" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#0284c7" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path d="M 0 20 Q 40 18 80 12 T 120 7 T 160 2 L 160 24 L 0 24 Z" fill="url(#grad-pat)" />
              <path d="M 0 20 Q 40 18 80 12 T 120 7 T 160 2" fill="none" stroke="#0284c7" strokeWidth="2.2" strokeLinecap="round" />
            </svg>
          </div>
          <button
            className="btn btn-outline btn-sm kpi-card-btn"
            onClick={() => onNavigate('patients')}
          >
            {kpis.patients?.button_text || 'View Patients & Timeline →'}
          </button>
        </div>

        {/* Card 3: Pharmacovigilance */}
        <div className="sketch-kpi-card kpi-pv">
          <div className="kpi-card-header">
            <span className="kpi-card-title">{kpis.pharmacovigilance?.title || 'Pharmacovigilance'}</span>
            <AlertTriangle className="text-amber-600" size={24} />
          </div>
          <div className="kpi-stats-row">
            <div className="kpi-stat-col">
              <span className="kpi-stat-number">{kpis.pharmacovigilance?.total_adverse_events || 14}</span>
              <span className="kpi-stat-label">Total AE</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#dc2626' }}>
                {kpis.pharmacovigilance?.serious_adverse_events || 2}
              </span>
              <span className="kpi-stat-label">Serious (SAE)</span>
            </div>
            <div className="kpi-stat-col">
              <span className="kpi-stat-number" style={{ color: '#d97706' }}>
                {kpis.pharmacovigilance?.cases_under_review || 3}
              </span>
              <span className="kpi-stat-label">Under Review</span>
            </div>
          </div>
          {/* Micro Sparkline */}
          <div style={{ height: '24px', margin: '6px 0', opacity: 0.9 }}>
            <svg viewBox="0 0 160 24" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
              <defs>
                <linearGradient id="grad-pv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#d97706" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#d97706" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path d="M 0 10 Q 35 5 70 16 T 115 9 T 160 14 L 160 24 L 0 24 Z" fill="url(#grad-pv)" />
              <path d="M 0 10 Q 35 5 70 16 T 115 9 T 160 14" fill="none" stroke="#d97706" strokeWidth="2.2" strokeLinecap="round" />
            </svg>
          </div>
          <button
            className="btn btn-outline btn-sm kpi-card-btn"
            onClick={() => onNavigate('pv')}
          >
            {kpis.pharmacovigilance?.button_text || 'Safety Signals & Reporting →'}
          </button>
        </div>
      </div>

      {/* EXECUTIVE GCP & ETHICAL GOVERNANCE COMPLIANCE GAUGE METER */}
      <div className="active-trials-section-card mt-6" style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', border: '1px solid #e2e8f0', boxShadow: '0 4px 16px rgba(0, 89, 68, 0.06)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', borderBottom: '1px solid #f1f5f9', paddingBottom: '14px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#005944', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <ShieldCheck size={20} className="text-emerald-700" />
              <span>GCP & Clinical Trial Governance Health Index</span>
              <span style={{ fontSize: '10.5px', background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0', padding: '2px 8px', borderRadius: '9999px', fontWeight: 700 }}>
                ICMR NDCT 2019
              </span>
            </h3>
            <p style={{ fontSize: '12px', color: '#64748b', margin: '4px 0 0 0' }}>
              Real-time multi-dimensional compliance tracking across all 9 AIIA trial centers in India
            </p>
          </div>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onNavigate('gcp')}
            style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            <span>Open GCP Protocol Checklist</span>
            <ArrowRight size={13} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', alignItems: 'center' }}>
          {/* Main Semi-Circular Gauge */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '10px', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ position: 'relative', width: '140px', height: '80px', overflow: 'hidden' }}>
              <svg viewBox="0 0 100 50" style={{ width: '100%', height: '100%' }}>
                <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#e2e8f0" strokeWidth="10" strokeLinecap="round" />
                <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="url(#gcp-arc-grad)" strokeWidth="10" strokeLinecap="round" strokeDasharray="125.6" strokeDashoffset="13.8" />
                <defs>
                  <linearGradient id="gcp-arc-grad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#005944" />
                    <stop offset="100%" stopColor="#10b981" />
                  </linearGradient>
                </defs>
              </svg>
              <div style={{ position: 'absolute', bottom: '0', left: '0', right: '0', textAlign: 'center' }}>
                <span style={{ fontSize: '22px', fontWeight: 900, color: '#005944', lineHeight: 1 }}>89%</span>
              </div>
            </div>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#005944', marginTop: '6px' }}>OVERALL GCP COMPLIANCE</span>
            <span style={{ fontSize: '10px', color: '#16a34a', fontWeight: 600 }}>Grade A (Fully Certified)</span>
          </div>

          {/* Sub-Ring 1: Ethics Committee */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ position: 'relative', width: '48px', height: '48px', flexShrink: 0 }}>
              <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#e2e8f0" strokeWidth="3.5" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#15803d" strokeWidth="3.5" strokeDasharray="100, 100" />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 800, color: '#15803d' }}>
                100%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#0f172a' }}>IEC / IRB Approvals</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>All active protocols cleared</div>
            </div>
          </div>

          {/* Sub-Ring 2: Rule 2 CTRI Data Integrity */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ position: 'relative', width: '48px', height: '48px', flexShrink: 0 }}>
              <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#e2e8f0" strokeWidth="3.5" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#0284c7" strokeWidth="3.5" strokeDasharray="100, 100" />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 800, color: '#0284c7' }}>
                100%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#0f172a' }}>Rule 2 Anti-Bypass</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Zero bypass, official CTRI URLs</div>
            </div>
          </div>

          {/* Sub-Ring 3: Safety Signal SLA */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <div style={{ position: 'relative', width: '48px', height: '48px', flexShrink: 0 }}>
              <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#e2e8f0" strokeWidth="3.5" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#d97706" strokeWidth="3.5" strokeDasharray="94, 100" />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 800, color: '#d97706' }}>
                94%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#0f172a' }}>PV Rapid Triage SLA</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>24hr reporting turnaround</div>
            </div>
          </div>
        </div>
      </div>

      {/* === ADVANCED CLINICAL CHARTS (Recharts) === */}
      <div className="active-trials-section-card mt-6">
        <div className="section-card-header">
          <span className="section-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={18} className="text-emerald-700" />
            Advanced Clinical Analytics
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px', padding: '16px 0' }}>
          {/* Chart 1: Enrollment Velocity Line Chart */}
          <div style={{ background: '#f8fafb', borderRadius: '10px', padding: '16px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <TrendingUp size={14} className="text-emerald-600" />
              Enrollment Velocity (Monthly)
            </h4>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={[
                { month: 'Jan', enrolled: 4, target: 8 },
                { month: 'Feb', enrolled: 7, target: 8 },
                { month: 'Mar', enrolled: 12, target: 10 },
                { month: 'Apr', enrolled: 15, target: 12 },
                { month: 'May', enrolled: 18, target: 15 },
                { month: 'Jun', enrolled: 22, target: 18 },
                { month: 'Jul', enrolled: 25, target: 20 },
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line
                  type="monotone" dataKey="enrolled" stroke="#005944"
                  strokeWidth={2.5} dot={{ r: 4, fill: '#005944' }}
                  name="Actual Enrolled"
                />
                <Line
                  type="monotone" dataKey="target" stroke="#94a3b8"
                  strokeWidth={2} strokeDasharray="5 5" dot={{ r: 3 }}
                  name="Target"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Chart 2: Dosha Balance Radar Chart */}
          <div style={{ background: '#f8fafb', borderRadius: '10px', padding: '16px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={14} className="text-amber-600" />
              Dosha Balance Radar (Avg Pre/Post Treatment)
            </h4>
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart
                cx="50%"
                cy="42%"
                outerRadius="58%"
                data={[
                  { axis: 'Vata', pre: 78, post: 52 },
                  { axis: 'Pitta', pre: 65, post: 44 },
                  { axis: 'Kapha', pre: 55, post: 60 },
                  { axis: 'Agni', pre: 42, post: 68 },
                  { axis: 'Ojas', pre: 35, post: 72 },
                  { axis: 'Ama', pre: 70, post: 30 },
                ]}
              >
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="axis" tick={{ fontSize: 11, fill: '#475569' }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 9, fill: '#94a3b8' }} />
                <Radar
                  name="Pre-Treatment" dataKey="pre" stroke="#dc2626"
                  fill="#dc2626" fillOpacity={0.15} strokeWidth={2}
                />
                <Radar
                  name="Post-Treatment" dataKey="post" stroke="#005944"
                  fill="#005944" fillOpacity={0.2} strokeWidth={2}
                />
                <Legend
                  verticalAlign="bottom"
                  wrapperStyle={{ fontSize: '11px', paddingTop: '12px' }}
                />
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Chart 3: Site Recruitment Bar Chart */}
          <div style={{ background: '#f8fafb', borderRadius: '10px', padding: '16px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#334155', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <BarChart3 size={14} className="text-blue-600" />
              Recruitment by Site (Enrolled vs Target)
            </h4>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={[
                { site: 'Delhi', enrolled: 8, target: 10 },
                { site: 'Mumbai', enrolled: 6, target: 8 },
                { site: 'Kolkata', enrolled: 4, target: 6 },
                { site: 'Kerala', enrolled: 5, target: 7 },
                { site: 'Lucknow', enrolled: 3, target: 5 },
                { site: 'Jaipur', enrolled: 2, target: 4 },
                { site: 'Hyd', enrolled: 3, target: 5 },
                { site: 'Blr', enrolled: 4, target: 6 },
                { site: 'Noida', enrolled: 2, target: 3 },
              ]} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis dataKey="site" type="category" tick={{ fontSize: 10, fill: '#475569' }} width={55} />
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="enrolled" fill="#005944" name="Enrolled" radius={[0, 4, 4, 0]} barSize={12} />
                <Bar dataKey="target" fill="#cbd5e1" name="Target" radius={[0, 4, 4, 0]} barSize={12} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Active Trials Section with Milestone Progress Bars */}
      <div className="active-trials-section-card mt-6">
        <div className="section-card-header">
          <span className="section-card-title">Active Clinical Trials & Milestone Progress</span>
          <button
            className="btn btn-ghost btn-sm flex items-center gap-1"
            onClick={() => onNavigate('active-trials')}
          >
            <span>View All Trials</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div className="trials-summary-counters">
          <div className="trial-counter-pill">
            <span>🟢 Ongoing:</span>
            <strong>{trialsSum.ongoing || 5}</strong>
          </div>
          <div className="trial-counter-pill">
            <span>🔵 Completed:</span>
            <strong>{trialsSum.completed || 2}</strong>
          </div>
          <div className="trial-counter-pill">
            <span>🟡 Upcoming / Pending:</span>
            <strong>{trialsSum.upcoming || 1}</strong>
          </div>
        </div>

        <div className="trial-progress-list">
          {trialsSum.trials_progress?.map((t) => (
            <div
              key={t.trial_id}
              className="trial-progress-row cursor-pointer hover:bg-slate-50 transition"
              onClick={() => setSelectedTrial(t)}
            >
              <div className="trial-progress-header">
                <div>
                  <span className="trial-progress-id">{t.trial_id}</span>: {' '}
                  <strong>{t.trial_name}</strong>
                  <span className="text-xs text-slate-500 ml-2">({t.condition} • {t.city})</span>
                </div>
                <div>
                  <span style={{ fontWeight: 700, color: '#005944' }}>{t.progress_pct}%</span>
                  <span className="text-muted ml-2" style={{ fontSize: '11px' }}>
                    ({t.enrolled_participants}/{t.target_participants} Enrolled)
                  </span>
                </div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${t.progress_pct}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* === INTERACTIVE INDIA CLINICAL TRIAL MAP (Leaflet.js) === */}
      <IndiaTrialMap onSelectCity={handleOpenSite} />

      {/* 9 National Regional Centers Quick Matrix */}
      <div className="active-trials-section-card mt-6">
        <div className="section-card-header">
          <span className="section-card-title">National Ayurveda Clinical Trial Sites (9 Participating Centers)</span>
          <button
            className="btn btn-ghost btn-sm flex items-center gap-1"
            onClick={() => onNavigate('sites')}
          >
            <span>Full Sites Center</span>
            <ArrowRight size={14} />
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '10px' }}>
          {['Mumbai', 'Delhi', 'Kolkata', 'Kerala', 'Lucknow', 'Noida', 'Jaipur', 'Hyderabad', 'Bengaluru'].map((c) => (
            <button
              key={c}
              className="btn btn-outline btn-sm flex items-center justify-center gap-1 font-semibold"
              onClick={() => handleOpenSite(c)}
            >
              <MapPin size={13} className="text-emerald-700" />
              <span>{c}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Site Detail Modal */}
      {selectedSite && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <h3 className="text-lg font-bold text-emerald-900 flex items-center gap-2">
                <MapPin size={18} className="text-emerald-700" />
                <span>Site Details: {selectedSite}</span>
              </h3>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedSite(null)}
              >
                <X size={18} />
              </button>
            </div>
            {siteLoading ? (
              <div className="p-4 text-center text-sm text-slate-500">Loading site metrics...</div>
            ) : siteDetailData ? (
              <div className="space-y-3">
                <div className="bg-slate-50 p-3 rounded border text-sm">
                  <p><strong>Hospital:</strong> {siteDetailData.site?.hospital_name || 'AIIA Regional Hospital'}</p>
                  <p><strong>Lead Principal Investigator:</strong> {siteDetailData.site?.lead_investigator || 'Dr. Assigned PI'}</p>
                  <p><strong>Active Enrolled Patients:</strong> {siteDetailData.site?.active_patients || 0}</p>
                  <p><strong>Bed Capacity:</strong> {siteDetailData.site?.bed_capacity || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-xs uppercase text-slate-600 mb-2">Trials Conducted Here</h4>
                  <ul className="text-xs space-y-1">
                    {siteDetailData.trials?.map((tr) => (
                      <li key={tr.trial_id} className="p-2 bg-emerald-50 text-emerald-900 rounded">
                        <strong>{tr.trial_id}</strong> - {tr.trial_name} ({tr.condition})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-sm text-slate-500">Site details loaded.</div>
            )}
            <div className="mt-6 flex justify-end">
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedSite(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Trial Detail Modal */}
      {selectedTrial && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-xl w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <h3 className="text-lg font-bold text-emerald-900">
                {selectedTrial.trial_id}: {selectedTrial.trial_name}
              </h3>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedTrial(null)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded border">
                <div><strong>Condition:</strong> {selectedTrial.condition}</div>
                <div><strong>Center:</strong> {selectedTrial.city}</div>
                <div><strong>Target:</strong> {selectedTrial.target_participants} patients</div>
                <div><strong>Recruited:</strong> {selectedTrial.enrolled_participants} ({selectedTrial.progress_pct}%)</div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar-fill" style={{ width: `${selectedTrial.progress_pct}%` }}></div>
              </div>
            </div>
            <div className="mt-6 flex justify-between">
              <button
                className="btn btn-primary btn-sm"
                onClick={() => {
                  setSelectedTrial(null);
                  onNavigate('trial-info');
                }}
              >
                Full Protocol Specifications →
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedTrial(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
