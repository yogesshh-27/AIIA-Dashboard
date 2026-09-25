import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { Search, Bell, LogOut, User, Check, X, Shield, Hospital, Stethoscope, AlertTriangle } from 'lucide-react';

export default function StaffHeader({
  currentUser,
  onLogout,
  onToggleSidebar,
  onSelectNav,
  onGlobalSearchResultSelect,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);

  const [notifications, setNotifications] = useState([]);
  const [showNotifDrawer, setShowNotifDrawer] = useState(false);

  const searchRef = useRef(null);
  const notifRef = useRef(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSearchDropdown(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setShowNotifDrawer(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch initial notifications
  useEffect(() => {
    async function loadNotifications() {
      try {
        const data = await api.getPvSummary();
        if (data.success && data.summary) {
          setNotifications([
            { id: 1, text: 'Safety signal: 7 rash cases detected in AYU-002', time: '10m ago', urgent: true },
            { id: 2, text: 'IEC approval pending for Delhi Osteoarthritis protocol', time: '1h ago', urgent: false },
            { id: 3, text: 'Ramlal Sharma completed Stage 4 formulation dispensation', time: '2h ago', urgent: false },
            { id: 4, text: 'CTRI registry synchronization completed (75 trials indexed)', time: '4h ago', urgent: false },
            { id: 5, text: 'Annual GCP Compliance Audit scheduled for next Tuesday', time: '1d ago', urgent: false },
          ]);
        }
      } catch (e) {
        // Fallback notifications
        setNotifications([
          { id: 1, text: 'Safety signal: 7 rash cases detected in AYU-002', time: '10m ago', urgent: true },
          { id: 2, text: 'IEC approval pending for Delhi trial renewal', time: '1h ago', urgent: false },
        ]);
      }
    }
    loadNotifications();
  }, []);

  // Debounced global search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      setShowSearchDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const data = await api.globalSearch(searchQuery);
        if (data.success) {
          setSearchResults(data.results);
          setShowSearchDropdown(true);
        }
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setSearchLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleResultClick = (type, item) => {
    setShowSearchDropdown(false);
    setSearchQuery('');
    if (onGlobalSearchResultSelect) {
      onGlobalSearchResultSelect(type, item);
    }
  };

  return (
    <header className="staff-header">
      <div className="header-left">
        <button
          className="sidebar-toggle-btn"
          onClick={onToggleSidebar}
          aria-label="Toggle Navigation Sidebar"
        >
          ☰
        </button>
        <div className="header-logo-group">
          <div className="header-emblem-small">AIIA</div>
          <div className="header-title-text">
            <span className="header-main-name">अखिल भारतीय आयुर्वेद संस्थान | AIIA</span>
            <span className="header-sub-name">AYURCTMS • Clinical Trial Management & Research Portal</span>
          </div>
        </div>
      </div>

      {/* GLOBAL SEARCH BAR */}
      <div className="header-center" ref={searchRef}>
        <div className="global-search-container">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="global-search-input"
            placeholder="Search patients, doctors, trials or sites..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchQuery.trim() && setShowSearchDropdown(true)}
          />

          {showSearchDropdown && searchResults && (
            <div className="global-search-dropdown" style={{ display: 'block' }}>
              {searchResults.patients?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">Patients</div>
                  {searchResults.patients.map((p) => (
                    <div
                      key={p.patient_id}
                      className="search-item"
                      onClick={() => handleResultClick('patient', p)}
                    >
                      <User size={13} className="text-emerald-700 mr-2 inline" />
                      <strong>{p.full_name}</strong>
                      <span className="text-xs text-slate-500 ml-2">({p.patient_id} • {p.condition})</span>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.trials?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">Trials</div>
                  {searchResults.trials.map((t) => (
                    <div
                      key={t.trial_id}
                      className="search-item"
                      onClick={() => handleResultClick('trial', t)}
                    >
                      <Shield size={13} className="text-emerald-700 mr-2 inline" />
                      <strong>{t.trial_name}</strong>
                      <span className="text-xs text-slate-500 ml-2">({t.trial_id} • {t.condition})</span>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.doctors?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">Doctors</div>
                  {searchResults.doctors.map((d) => (
                    <div
                      key={d.doctor_id}
                      className="search-item"
                      onClick={() => handleResultClick('doctor', d)}
                    >
                      <Stethoscope size={13} className="text-emerald-700 mr-2 inline" />
                      <strong>{d.name}</strong>
                      <span className="text-xs text-slate-500 ml-2">({d.specialization})</span>
                    </div>
                  ))}
                </div>
              )}

              {(!searchResults.patients?.length && !searchResults.trials?.length && !searchResults.doctors?.length) && (
                <div className="p-3 text-center text-xs text-slate-500">
                  No matching records found for "{searchQuery}"
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="header-right">
        {/* NOTIFICATIONS BELL */}
        <div className="notification-wrapper" ref={notifRef}>
          <button
            className="header-icon-btn"
            onClick={() => setShowNotifDrawer(!showNotifDrawer)}
            aria-label="System Notifications"
            title="System Notifications"
          >
            <Bell size={18} />
            <span className="notification-badge">{notifications.length}</span>
          </button>

          {showNotifDrawer && (
            <div className="notifications-drawer" style={{ display: 'block' }}>
              <div className="notif-drawer-header">
                <h4>System Notifications</h4>
                <span className="badge badge-info">{notifications.length} Active</span>
              </div>
              <div className="notif-list">
                {notifications.map((n) => (
                  <div key={n.id} className={`notif-item ${n.urgent ? 'notif-urgent' : ''}`}>
                    <div className="notif-icon">
                      {n.urgent ? <AlertTriangle size={14} className="text-amber-600" /> : '📌'}
                    </div>
                    <div className="notif-content">
                      <p>{n.text}</p>
                      <span className="notif-time">{n.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* STAFF PROFILE CHIP */}
        <div className="staff-profile-chip">
          <div className="staff-avatar">
            {currentUser?.full_name ? currentUser.full_name.substring(0, 2).toUpperCase() : 'DA'}
          </div>
          <div className="staff-profile-info">
            <span className="staff-name">{currentUser?.full_name || 'Dr. Research Admin'}</span>
            <span className="staff-role-badge">{currentUser?.role || 'AIIA Authorized Staff'}</span>
          </div>
          <button className="btn btn-xs btn-outline" onClick={onLogout} title="Sign Out">
            <LogOut size={12} className="inline mr-1" />
            Exit
          </button>
        </div>
      </div>
    </header>
  );
}
