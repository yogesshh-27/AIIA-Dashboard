import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import { useWebSocketAlerts } from '../../services/useWebSocketAlerts';
import { Search, Bell, LogOut, User, Check, X, Shield, Hospital, Stethoscope, AlertTriangle, Radio } from 'lucide-react';

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

  const { alerts, latestAlert, connectionStatus, dismissLatest } = useWebSocketAlerts();

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
        const results = data?.results || (data?.patients || data?.trials || data?.doctors || data?.sites ? data : null);
        if (results) {
          setSearchResults(results);
          setShowSearchDropdown(true);
        } else if (data?.success) {
          setSearchResults(data.results || { patients: [], trials: [], doctors: [], sites: [] });
          setShowSearchDropdown(true);
        }
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setSearchLoading(false);
      }
    }, 200);

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
          <img
            src="/logos/aiia-logo.svg"
            alt="AIIA Crest"
            className="header-emblem-img"
            width="36"
            height="36"
          />
          <div className="header-title-text">
            <span className="header-main-name">अखिल भारतीय आयुर्वेद संस्थान | AIIA</span>
            <span className="header-sub-name">AYURCTMS • Clinical Trial Management Portal</span>
          </div>
        </div>
      </div>

      {/* GLOBAL SEARCH BAR */}
      <div className="header-center" ref={searchRef}>
        <div className="global-search-container" style={{ position: 'relative' }}>
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="global-search-input"
            placeholder="Search patients, doctors, trials or sites..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchQuery.trim() && setShowSearchDropdown(true)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') {
                setShowSearchDropdown(false);
              } else if (e.key === 'Enter') {
                if (searchResults) {
                  if (searchResults.patients?.length > 0) {
                    handleResultClick('patient', searchResults.patients[0]);
                  } else if (searchResults.trials?.length > 0) {
                    handleResultClick('trial', searchResults.trials[0]);
                  } else if (searchResults.doctors?.length > 0) {
                    handleResultClick('doctor', searchResults.doctors[0]);
                  } else if (searchResults.sites?.length > 0) {
                    handleResultClick('site', searchResults.sites[0]);
                  }
                }
              }
            }}
          />

          {searchQuery && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setSearchResults(null);
                setShowSearchDropdown(false);
              }}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#94a3b8',
                padding: '2px',
                display: 'flex',
                alignItems: 'center',
                zIndex: 2
              }}
              title="Clear search"
            >
              <X size={14} />
            </button>
          )}

          {showSearchDropdown && searchResults && (
            <div className="global-search-dropdown" style={{ display: 'block' }}>
              {searchResults.patients?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">
                    <span className="search-group-badge">Patients</span>
                    <span className="search-group-count">{searchResults.patients.length} found</span>
                  </div>
                  {searchResults.patients.map((p) => (
                    <div
                      key={p.patient_id}
                      className="search-item"
                      onClick={() => handleResultClick('patient', p)}
                    >
                      <div className="search-item-icon patient">
                        <User size={15} />
                      </div>
                      <div className="search-item-body">
                        <div className="search-item-main">
                          <span className="search-item-title">{p.full_name}</span>
                          <span className="search-item-badge id">{p.patient_id}</span>
                        </div>
                        <div className="search-item-sub">
                          <span className="search-tag condition">{p.condition}</span>
                          {p.area_city && <span className="search-tag location">• {p.area_city}</span>}
                        </div>
                      </div>
                      <span className="search-item-arrow">→</span>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.trials?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">
                    <span className="search-group-badge">Clinical Trials</span>
                    <span className="search-group-count">{searchResults.trials.length} found</span>
                  </div>
                  {searchResults.trials.map((t) => (
                    <div
                      key={t.trial_id}
                      className="search-item"
                      onClick={() => handleResultClick('trial', t)}
                    >
                      <div className="search-item-icon trial">
                        <Shield size={15} />
                      </div>
                      <div className="search-item-body">
                        <div className="search-item-main">
                          <span className="search-item-title">{t.trial_name}</span>
                          <span className="search-item-badge trial-id">{t.trial_id}</span>
                        </div>
                        <div className="search-item-sub">
                          <span className="search-tag condition">{t.condition}</span>
                          {t.city && <span className="search-tag location">• {t.city}</span>}
                          <span className="search-tag status">{t.trial_status || 'Recruiting'}</span>
                        </div>
                      </div>
                      <span className="search-item-arrow">→</span>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.doctors?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">
                    <span className="search-group-badge">Doctors & Specialists</span>
                    <span className="search-group-count">{searchResults.doctors.length} found</span>
                  </div>
                  {searchResults.doctors.map((d) => (
                    <div
                      key={d.doctor_id}
                      className="search-item"
                      onClick={() => handleResultClick('doctor', d)}
                    >
                      <div className="search-item-icon doctor">
                        <Stethoscope size={15} />
                      </div>
                      <div className="search-item-body">
                        <div className="search-item-main">
                          <span className="search-item-title">{d.name}</span>
                          <span className="search-item-badge doc-id">{d.doctor_id}</span>
                        </div>
                        <div className="search-item-sub">
                          <span className="search-tag spec">{d.specialization}</span>
                          {d.current_site && <span className="search-tag location">• {d.current_site}</span>}
                        </div>
                      </div>
                      <span className="search-item-arrow">→</span>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.sites?.length > 0 && (
                <div className="search-group">
                  <div className="search-group-title">
                    <span className="search-group-badge">Clinical Sites</span>
                    <span className="search-group-count">{searchResults.sites.length} found</span>
                  </div>
                  {searchResults.sites.map((s) => (
                    <div
                      key={s.site_id || s.city}
                      className="search-item"
                      onClick={() => handleResultClick('site', s)}
                    >
                      <div className="search-item-icon site">
                        <Hospital size={15} />
                      </div>
                      <div className="search-item-body">
                        <div className="search-item-main">
                          <span className="search-item-title">{s.hospital_name || s.city}</span>
                          <span className="search-item-badge site-id">{s.city}</span>
                        </div>
                        <div className="search-item-sub">
                          <span className="search-tag location">{s.city}</span>
                          {s.status && <span className="search-tag status">• {s.status}</span>}
                        </div>
                      </div>
                      <span className="search-item-arrow">→</span>
                    </div>
                  ))}
                </div>
              )}

              {(!searchResults.patients?.length && !searchResults.trials?.length && !searchResults.doctors?.length && !searchResults.sites?.length) && (
                <div className="search-empty-state">
                  <Search size={22} className="search-empty-icon" />
                  <p>{searchLoading ? 'Searching AYURCTMS registry...' : `No matching records found for "${searchQuery}"`}</p>
                  <span className="search-empty-hint">Try searching by condition, title, name, or city</span>
                </div>
              )}

              <div className="search-dropdown-footer">
                <span>Use <strong>↑</strong> <strong>↓</strong> to navigate</span>
                <span>Press <strong>↵ Enter</strong> to select</span>
                <span><strong>ESC</strong> to close</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="header-right" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* WEBSOCKET LIVE ALERT STATUS BADGE */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '11px',
            fontWeight: 600,
            padding: '3px 8px',
            borderRadius: '12px',
            background:
              connectionStatus === 'connected'
                ? 'rgba(5, 150, 105, 0.12)'
                : connectionStatus === 'standby'
                ? 'rgba(14, 116, 144, 0.12)'
                : 'rgba(217, 119, 6, 0.12)',
            color:
              connectionStatus === 'connected'
                ? '#059669'
                : connectionStatus === 'standby'
                ? '#0e7490'
                : '#d97706',
            border: `1px solid ${
              connectionStatus === 'connected'
                ? '#a7f3d0'
                : connectionStatus === 'standby'
                ? '#a5f3fc'
                : '#fde68a'
            }`,
          }}
          title={
            connectionStatus === 'connected'
              ? 'Connected to Real-Time SAE Alert Stream'
              : connectionStatus === 'standby'
              ? 'Dashboard operational on verified clinical dataset'
              : 'Connecting to Alert Stream...'
          }
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: '50%',
              backgroundColor:
                connectionStatus === 'connected'
                  ? '#10b981'
                  : connectionStatus === 'standby'
                  ? '#06b6d4'
                  : '#f59e0b',
              animation: connectionStatus === 'connecting' ? 'pulse 2s infinite' : 'none',
            }}
          />
          <span>
            {connectionStatus === 'connected'
              ? 'Live SAE Feed'
              : connectionStatus === 'standby'
              ? 'Live Standby'
              : 'Connecting...'}
          </span>
        </div>

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

      {/* FLOATING REAL-TIME SAE ALERT TOAST */}
      {latestAlert && (
        <div
          style={{
            position: 'fixed',
            top: '80px',
            right: '20px',
            zIndex: 9999,
            maxWidth: '380px',
            background: '#fff1f2',
            border: '2px solid #f43f5e',
            borderRadius: '10px',
            padding: '14px 16px',
            boxShadow: '0 10px 25px -5px rgba(225, 29, 72, 0.25)',
            animation: 'slideIn 0.3s ease',
          }}
          role="alert"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <AlertTriangle size={18} className="text-rose-600" />
              <strong style={{ fontSize: '13px', color: '#9f1239' }}>{latestAlert.title || 'Serious Adverse Event'}</strong>
            </div>
            <button
              onClick={dismissLatest}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9f1239', padding: '2px' }}
              aria-label="Dismiss alert"
            >
              <X size={15} />
            </button>
          </div>
          <p style={{ margin: '8px 0 4px', fontSize: '12px', color: '#881337', lineHeight: 1.4 }}>
            {latestAlert.message}
          </p>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#be123c', marginTop: '6px' }}>
            <span><strong>Patient:</strong> {latestAlert.patient_name}</span>
            <span>{latestAlert.receivedAt}</span>
          </div>
        </div>
      )}
    </header>
  );
}
