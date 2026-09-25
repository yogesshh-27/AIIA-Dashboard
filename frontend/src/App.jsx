import React, { useState, useEffect } from 'react';
import GovTopBar from './components/GovTopBar';
import LandingGate from './components/LandingGate';
import PatientPortal from './components/PatientPortal';
import StaffAuthModal from './components/StaffAuthModal';
import StaffPortal from './components/StaffPortal/StaffPortal';

export default function App() {
  // Navigation states: 'gate' | 'patient' | 'staff'
  const [currentView, setCurrentView] = useState('gate');
  const [showStaffAuthModal, setShowStaffAuthModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  // Check persisted session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('ayurctms_user');
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        setCurrentUser(parsed);
      } catch (e) {
        localStorage.removeItem('ayurctms_user');
      }
    }
  }, []);

  const handleSelectPatientPortal = () => {
    setCurrentView('patient');
  };

  const handleOpenStaffLogin = () => {
    if (currentUser) {
      setCurrentView('staff');
    } else {
      setShowStaffAuthModal(true);
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    localStorage.setItem('ayurctms_user', JSON.stringify(user));
    setShowStaffAuthModal(false);
    setCurrentView('staff');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('ayurctms_user');
    setCurrentView('gate');
  };

  return (
    <div className="app-root-shell" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 1. GIGW Government Top Bar with Tricolor Ribbon */}
      <GovTopBar />

      {/* 2. Main Viewport Switching */}
      {currentView === 'gate' && (
        <LandingGate
          onSelectPatient={handleSelectPatientPortal}
          onSelectStaff={handleOpenStaffLogin}
        />
      )}

      {currentView === 'patient' && (
        <PatientPortal
          onBackToGate={() => setCurrentView('gate')}
          onOpenStaffLogin={handleOpenStaffLogin}
        />
      )}

      {currentView === 'staff' && (
        <StaffPortal
          currentUser={currentUser}
          onLogout={handleLogout}
        />
      )}

      {/* 3. Staff Authentication Modal */}
      <StaffAuthModal
        isOpen={showStaffAuthModal}
        onClose={() => setShowStaffAuthModal(false)}
        onLoginSuccess={handleLoginSuccess}
      />
    </div>
  );
}
