import React, { useState } from 'react';
import StaffHeader from './StaffHeader';
import StaffSidebar from './StaffSidebar';
import CreateTrialModal from './CreateTrialModal';

import DashboardView from './DashboardView';
import ActiveTrialsView from './ActiveTrialsView';
import SitesExplorerView from './SitesExplorerView';
import TrialInfoView from './TrialInfoView';
import ApprovalsView from './ApprovalsView';
import GcpChecklistView from './GcpChecklistView';
import DoctorsView from './DoctorsView';
import PatientsView from './PatientsView';
import PharmacovigilanceView from './PharmacovigilanceView';
import ReportsView from './ReportsView';
import InteropView from './InteropView';
import CtriExplorerView from './CtriExplorerView';

export default function StaffPortal({ currentUser, onLogout }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [createTrialOpen, setCreateTrialOpen] = useState(false);

  const handleGlobalSearchResultSelect = (type, item) => {
    if (type === 'patient') {
      setActiveTab('patients');
    } else if (type === 'trial') {
      setActiveTab('trial-info');
    } else if (type === 'doctor') {
      setActiveTab('doctors');
    } else if (type === 'site') {
      setActiveTab('sites');
    }
  };

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <DashboardView
            onNavigate={(tab) => setActiveTab(tab)}
            onOpenCreateTrial={() => setCreateTrialOpen(true)}
          />
        );
      case 'active-trials':
        return <ActiveTrialsView onOpenCreateTrial={() => setCreateTrialOpen(true)} />;
      case 'sites':
        return <SitesExplorerView onNavigateToTrial={() => setActiveTab('trial-info')} />;
      case 'trial-info':
        return <TrialInfoView onOpenCreateTrial={() => setCreateTrialOpen(true)} />;
      case 'approvals':
        return <ApprovalsView currentUser={currentUser} />;
      case 'gcp':
        return <GcpChecklistView currentUser={currentUser} />;
      case 'doctors':
        return <DoctorsView />;
      case 'patients':
        return <PatientsView />;
      case 'pv':
        return <PharmacovigilanceView currentUser={currentUser} />;
      case 'reports':
        return <ReportsView />;
      case 'interop':
        return <InteropView />;
      case 'ctri-extractor':
        return <CtriExplorerView />;
      default:
        return (
          <DashboardView
            onNavigate={(tab) => setActiveTab(tab)}
            onOpenCreateTrial={() => setCreateTrialOpen(true)}
          />
        );
    }
  };

  return (
    <div className="staff-portal-shell" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <StaffHeader
        currentUser={currentUser}
        onLogout={onLogout}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onSelectNav={(tab) => setActiveTab(tab)}
        onGlobalSearchResultSelect={handleGlobalSearchResultSelect}
      />

      <div className="staff-body" style={{ display: 'flex', flex: 1 }}>
        <StaffSidebar
          activeTab={activeTab}
          onSelectTab={(tab) => setActiveTab(tab)}
          isOpen={sidebarOpen}
        />

        <main className="staff-main-viewport" id="staff-main-content" style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
          {renderActiveView()}
        </main>
      </div>

      <CreateTrialModal
        isOpen={createTrialOpen}
        onClose={() => setCreateTrialOpen(false)}
        onTrialCreated={() => setActiveTab('trial-info')}
      />
    </div>
  );
}
