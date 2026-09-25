import React, { useState } from 'react';
import { api } from '../services/api';
import { Lock, User, Key, AlertCircle, Loader2 } from 'lucide-react';

export default function StaffAuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [staffId, setStaffId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleAutofill = () => {
    setStaffId('AIIA001');
    setPassword('AIIA@123');
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.loginStaff(staffId, password);
      if (data.success && data.user) {
        onLoginSuccess(data.user);
        onClose();
      } else {
        setError(data.message || 'Authentication failed. Please verify credentials.');
      }
    } catch (err) {
      setError(err.message || 'Server connection failed. Ensure backend server is active.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{ display: 'flex' }}>
      <div className="login-card-modal">
        <div className="login-header">
          <div className="login-emblem">AIIA</div>
          <h3>AIIA Staff Authentication</h3>
          <p>AYURCTMS Clinical Trial Management Portal</p>
        </div>

        <div className="demo-credentials-box">
          <div className="demo-cred-title">🔑 Demonstration Credentials:</div>
          <div className="demo-cred-row">
            <span>Staff ID: <strong>AIIA001</strong></span>
            <span>Password: <strong>AIIA@123</strong></span>
          </div>
          <button
            type="button"
            className="btn btn-xs btn-outline"
            onClick={handleAutofill}
            style={{ marginTop: '8px' }}
          >
            Autofill Demo Credentials
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="login-staff-id">Staff ID *</label>
            <input
              type="text"
              id="login-staff-id"
              className="form-input"
              placeholder="e.g. AIIA001"
              required
              value={staffId}
              onChange={(e) => setStaffId(e.target.value)}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="login-password">Password *</label>
            <input
              type="password"
              id="login-password"
              className="form-input"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="login-error" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="login-actions">
            <button
              type="submit"
              className="btn btn-primary btn-block"
              id="btn-login-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin inline mr-2" />
                  <span>AUTHENTICATING...</span>
                </>
              ) : (
                <span>LOGIN</span>
              )}
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-block"
              onClick={onClose}
              disabled={loading}
            >
              <span>CANCEL</span>
            </button>
          </div>
        </form>

        <div className="login-security-notice">
          <span>🔒 256-bit Encrypted Session • AIIA GCP Regulatory Portal</span>
        </div>
      </div>
    </div>
  );
}
