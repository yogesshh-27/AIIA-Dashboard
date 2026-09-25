import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { CheckCircle2, Clock, AlertOctagon, X, MessageSquare, Check, Shield } from 'lucide-react';

export default function ApprovalsView({ currentUser }) {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [decision, setDecision] = useState('APPROVED');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.getApprovals();
      setApprovals(data.approvals || []);
    } catch (err) {
      setError(err.message || 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleOpenReview = (appr) => {
    setSelectedApproval(appr);
    setDecision(appr.status);
    setNotes(appr.notes || '');
  };

  const handleSubmitDecision = async (e) => {
    e.preventDefault();
    if (!selectedApproval) return;
    setSubmitting(true);
    try {
      const res = await api.updateApproval({
        approval_id: selectedApproval.approval_id,
        status: decision,
        notes,
        reviewed_by: currentUser?.full_name || 'Institutional Ethics Board Reviewer',
      });
      if (res.success) {
        setToast({ type: 'success', text: `Approval ${selectedApproval.approval_id} updated to ${decision}` });
        setSelectedApproval(null);
        await fetchApprovals();
      }
    } catch (err) {
      setToast({ type: 'error', text: err.message || 'Failed to update approval' });
    } finally {
      setSubmitting(false);
      setTimeout(() => setToast(null), 3000);
    }
  };

  return (
    <div className="approvals-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Institutional Ethics & Regulatory Approvals</h2>
          <p>Ethics Committees (IEC), CTRI, and CDSCO/NDCT Rules 2019 review workflow</p>
        </div>
      </div>

      {toast && (
        <div
          className={`p-3 rounded text-xs mb-4 ${
            toast.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border border-emerald-300'
              : 'bg-rose-50 text-rose-900 border border-rose-300'
          }`}
        >
          {toast.text}
        </div>
      )}

      {loading ? (
        <div className="p-8 text-center text-slate-500">
          <div className="badge badge-info animate-pulse p-3 inline-block">
            Loading ethics committee queue...
          </div>
        </div>
      ) : error ? (
        <div className="badge badge-danger p-3">{error}</div>
      ) : (
        <div className="table-responsive bg-white rounded-lg border shadow-xs">
          <table className="data-table">
            <thead>
              <tr>
                <th>Approval ID</th>
                <th>Location / Site</th>
                <th>Trial Protocol</th>
                <th>Approval Type</th>
                <th>Status</th>
                <th>Submission Date</th>
                <th>Decision Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {approvals.map((a) => (
                <tr key={a.approval_id}>
                  <td>
                    <span className="trial-id-badge">{a.approval_id}</span>
                  </td>
                  <td>
                    <strong>{a.site}</strong>
                  </td>
                  <td>{a.trial_id}</td>
                  <td>{a.approval_type}</td>
                  <td>
                    <span
                      className={`badge ${
                        a.status === 'APPROVED'
                          ? 'badge-success'
                          : a.status === 'PENDING'
                          ? 'badge-warning'
                          : 'badge-danger'
                      }`}
                    >
                      {a.status}
                    </span>
                  </td>
                  <td>{a.submission_date}</td>
                  <td>{a.decision_date || 'Pending Review'}</td>
                  <td>
                    <button
                      className="btn btn-outline btn-xs"
                      onClick={() => handleOpenReview(a)}
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Review Modal */}
      {selectedApproval && (
        <div className="modal-overlay" style={{ display: 'flex' }}>
          <div className="modal-card max-w-lg w-full p-6">
            <div className="flex justify-between items-center mb-4 border-b pb-3">
              <div>
                <span className="badge badge-warning text-xs">Ethics Board Review</span>
                <h3 className="text-lg font-bold text-emerald-950 mt-1">
                  Review Approval: {selectedApproval.approval_id}
                </h3>
              </div>
              <button
                className="btn btn-ghost btn-xs text-slate-500"
                onClick={() => setSelectedApproval(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="text-xs space-y-2 mb-4 bg-slate-50 p-3 rounded border">
              <div>
                <strong>Site:</strong> {selectedApproval.site}
              </div>
              <div>
                <strong>Trial Protocol:</strong> {selectedApproval.trial_id}
              </div>
              <div>
                <strong>Approval Category:</strong> {selectedApproval.approval_type}
              </div>
              <div>
                <strong>Current Status:</strong>{' '}
                <span
                  className={`badge ${
                    selectedApproval.status === 'APPROVED'
                      ? 'badge-success'
                      : selectedApproval.status === 'PENDING'
                      ? 'badge-warning'
                      : 'badge-danger'
                  }`}
                >
                  {selectedApproval.status}
                </span>
              </div>
            </div>

            <form onSubmit={handleSubmitDecision} className="space-y-3 text-xs">
              <div className="form-group">
                <label className="font-semibold">Review Decision *</label>
                <select
                  className="form-select"
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  required
                >
                  <option value="APPROVED">APPROVED (Ethical Clearance Granted)</option>
                  <option value="PENDING">PENDING (Further Documentation Requested)</option>
                  <option value="REJECTED">REJECTED / ACTION REQUIRED</option>
                </select>
              </div>

              <div className="form-group">
                <label className="font-semibold">Reviewer Remarks & Ethics Board Notes</label>
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder="Enter protocol compliance remarks or conditions..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t">
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setSelectedApproval(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Submitting...' : 'Submit Decision'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
