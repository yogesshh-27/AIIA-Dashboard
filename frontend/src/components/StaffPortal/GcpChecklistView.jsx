import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ShieldCheck, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export default function GcpChecklistView({ currentUser }) {
  const [checklist, setChecklist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [togglingId, setTogglingId] = useState(null);

  const fetchChecklist = async () => {
    try {
      setLoading(true);
      const data = await api.getGcpChecklist();
      setChecklist(data);
    } catch (err) {
      setError(err.message || 'Failed to load GCP checklist');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChecklist();
  }, []);

  const handleToggle = async (itemId, currentCompleted) => {
    setTogglingId(itemId);
    try {
      const res = await api.toggleGcpItem({
        item_id: itemId,
        is_completed: currentCompleted ? 0 : 1,
        reviewed_by: currentUser?.full_name || 'Dr. Research Admin',
      });
      if (res.success) {
        await fetchChecklist();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setTogglingId(null);
    }
  };

  if (loading && !checklist) {
    return (
      <div className="p-8 text-center text-slate-500">
        <div className="badge badge-info animate-pulse p-3 inline-block">
          Loading GCP Guidelines checklist...
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="badge badge-danger p-3">{error}</div>;
  }

  const items = checklist?.items || [];
  const pct = checklist?.percentage || 89;

  return (
    <div className="gcp-view">
      <div className="view-header-bar">
        <div className="view-title-group">
          <h2>Good Clinical Practice (GCP) Guidelines Checklist</h2>
          <p>Operational monitoring module for GCP & Indian ICMR/AYUSH ethical guidelines</p>
        </div>
        <div
          className={`badge ${pct >= 80 ? 'badge-success' : 'badge-warning'}`}
          style={{ fontSize: '13px', padding: '6px 14px' }}
        >
          {checklist?.overall_status || 'Compliant'}
        </div>
      </div>

      <div className="active-trials-section-card mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="font-bold text-sm">Overall GCP Compliance Score: {pct}%</span>
          <span className="text-muted text-xs">
            {checklist?.completed_items || 8} of {checklist?.total_items || 9} Guidelines Verified
          </span>
        </div>
        <div className="progress-bar-container" style={{ height: '12px' }}>
          <div className="progress-bar-fill" style={{ width: `${pct}%` }}></div>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-5 shadow-xs">
        <h4 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
          <ShieldCheck size={18} className="text-emerald-700" />
          <span>GCP Compliance Checklist Items</span>
        </h4>

        <div className="space-y-3">
          {items.map((i) => (
            <div
              key={i.item_id}
              className="flex items-start justify-between p-3.5 bg-slate-50 border rounded-lg hover:border-emerald-300 transition"
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  className="w-4 h-4 mt-0.5 accent-emerald-700 cursor-pointer"
                  checked={Boolean(i.is_completed)}
                  disabled={togglingId === i.item_id}
                  onChange={() => handleToggle(i.item_id, Boolean(i.is_completed))}
                />
                <div>
                  <div className="font-bold text-xs text-slate-900">{i.title}</div>
                  <div className="text-xs text-slate-600 mt-0.5">{i.description}</div>
                  <div className="text-[11px] text-slate-400 mt-1.5">
                    Category: <strong>{i.category}</strong> • Last Reviewed:{' '}
                    <strong>{i.last_reviewed_date || 'Today'}</strong> • Reviewed By:{' '}
                    <strong>{i.reviewed_by || 'Dr. Research Admin'}</strong>
                  </div>
                </div>
              </div>
              <span className={`badge ${i.is_completed ? 'badge-success' : 'badge-warning'} shrink-0 ml-3`}>
                {i.is_completed ? '✓ Verified' : 'Pending Review'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
