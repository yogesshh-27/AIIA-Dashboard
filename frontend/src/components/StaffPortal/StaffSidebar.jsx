import React from 'react';
import {
  LayoutDashboard,
  Activity,
  MapPin,
  FileSpreadsheet,
  FileCheck2,
  ShieldCheck,
  Stethoscope,
  Users,
  AlertTriangle,
  FileText,
  GitBranch,
  Database
} from 'lucide-react';

export default function StaffSidebar({ activeTab, onSelectTab, stats, isOpen }) {
  const navItems = [
    {
      group: 'CLINICAL TRIAL MANAGEMENT',
      items: [
        { id: 'dashboard', label: '1. Dashboard', icon: LayoutDashboard },
        { id: 'active-trials', label: '2. Active Trials', icon: Activity, badge: '5' },
        { id: 'sites', label: '3. Sites / Locations', icon: MapPin, badge: '9' },
        { id: 'trial-info', label: '4. Trial Information', icon: FileSpreadsheet, badge: '8' },
        { id: 'approvals', label: '5. Pending Approvals', icon: FileCheck2, badge: '2', badgeClass: 'warning-badge' },
        { id: 'gcp', label: '6. GCP Guidelines', icon: ShieldCheck, badge: '89%', badgeClass: 'success-badge' },
      ]
    },
    {
      group: 'RESEARCH PERSONNEL & SAFETY',
      items: [
        { id: 'doctors', label: '7. Doctor Information', icon: Stethoscope, badge: '11' },
        { id: 'patients', label: '8. Patient Information', icon: Users, badge: '25' },
        { id: 'pv', label: '9. Pharmacovigilance', icon: AlertTriangle, badge: 'Signal', badgeClass: 'danger-badge' },
      ]
    },
    {
      group: 'GOVERNANCE & STANDARDS',
      items: [
        { id: 'reports', label: '10. Reports', icon: FileText },
        { id: 'interop', label: '11. Interoperability & Audit', icon: GitBranch },
        { id: 'ctri-extractor', label: '12. CTRI Extractor Data', icon: Database, badge: '75 Trials', badgeClass: 'success-badge' },
      ]
    }
  ];

  return (
    <aside className={`staff-sidebar ${isOpen ? 'open' : ''}`} id="staff-sidebar">
      <nav className="sidebar-nav">
        {navItems.map((sec, idx) => (
          <div key={idx} className="sidebar-section">
            <div className="sidebar-section-title">{sec.group}</div>
            {sec.items.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectTab(item.id)}
                  style={{ width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  <span className="nav-icon" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <Icon size={16} />
                  </span>
                  <span className="nav-label">{item.label}</span>
                  {item.badge && (
                    <span className={`nav-badge ${item.badgeClass || ''}`}>{item.badge}</span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-text">
          <span>AIIA CTMS v2.4</span>
          <span>GCP & NDCT Compliant</span>
        </div>
      </div>
    </aside>
  );
}
