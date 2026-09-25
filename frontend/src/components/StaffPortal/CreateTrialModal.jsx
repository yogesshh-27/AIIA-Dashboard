import React, { useState } from 'react';
import { api } from '../../services/api';
import { X, AlertTriangle, CheckCircle, ShieldCheck } from 'lucide-react';

export default function CreateTrialModal({ isOpen, onClose, onTrialCreated }) {
  const [formData, setFormData] = useState({
    trial_name: '',
    trial_id: `AYU-TRIAL-00${Math.floor(Math.random() * 90 + 10)}`,
    condition: 'Arthritis',
    intervention: '',
    city: 'Mumbai',
    hospital_name: 'AIIA Regional Ayurvedic Center',
    pi_name: 'Dr. Ananya Sharma',
    target_participants: 100,
    duration_weeks: 12,
    description: '',
    ethics_approval_status: 'Approved',
    ctri_registration_status: 'Registered',
    regulatory_status: 'Approved',
  });

  const [overlapWarning, setOverlapWarning] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  if (!isOpen) return null;

  const handleFieldChange = (field, value) => {
    const updated = { ...formData, [field]: value };
    setFormData(updated);

    // Overlap Detection Logic
    const city = field === 'city' ? value : updated.city;
    const cond = field === 'condition' ? value : updated.condition;

    if ((city === 'Kolkata' || city === 'Mumbai') && cond === 'Arthritis') {
      setOverlapWarning(
        `Potential Overlap Detected: An active ${cond} trial already exists at ${city} Site 02. You may proceed or select an alternative regional facility.`
      );
    } else if (city === 'Delhi' && cond === 'Diabetes') {
      setOverlapWarning(
        `Potential Overlap Detected: An active Diabetes trial (AYU-TRIAL-002) is currently ongoing at Delhi Main Campus.`
      );
    } else {
      setOverlapWarning(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFeedback(null);
    try {
      const res = await api.createTrial(formData);
      if (res.success) {
        setFeedback({ type: 'success', message: `Trial ${res.trial_id || formData.trial_id} created successfully!` });
        setTimeout(() => {
          if (onTrialCreated) onTrialCreated(formData);
          onClose();
        }, 800);
      } else {
        setFeedback({ type: 'error', message: res.message || 'Error registering trial' });
      }
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Error registering trial' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" style={{ display: 'flex' }}>
      <div className="modal-card max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4 border-b pb-3">
          <div>
            <span className="badge badge-info text-xs">Protocol Planning & Registration</span>
            <h3 className="text-lg font-bold text-emerald-950 mt-1">
              + Register New Ayurvedic Clinical Trial
            </h3>
          </div>
          <button className="btn btn-ghost btn-xs text-slate-500" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* OVERLAP WARNING PLACEHOLDER */}
        {overlapWarning && (
          <div className="bg-amber-50 border border-amber-300 p-3 rounded text-xs text-amber-900 mb-4 flex items-start gap-2">
            <AlertTriangle size={16} className="text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong>⚠️ Overlap Alert:</strong>
              <p className="mt-0.5">{overlapWarning}</p>
            </div>
          </div>
        )}

        {feedback && (
          <div
            className={`p-3 rounded text-xs mb-4 ${
              feedback.type === 'success'
                ? 'bg-emerald-50 text-emerald-900 border border-emerald-300'
                : 'bg-rose-50 text-rose-900 border border-rose-300'
            }`}
          >
            {feedback.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div className="form-row-grid">
            <div className="form-group">
              <label className="font-semibold">Trial Name *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Randomized Clinical Evaluation of Rasayana in Arthritis"
                value={formData.trial_name}
                onChange={(e) => handleFieldChange('trial_name', e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="font-semibold">Trial ID *</label>
              <input
                type="text"
                className="form-input"
                value={formData.trial_id}
                onChange={(e) => handleFieldChange('trial_id', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row-grid">
            <div className="form-group">
              <label className="font-semibold">Condition / Illness *</label>
              <select
                className="form-select"
                value={formData.condition}
                onChange={(e) => handleFieldChange('condition', e.target.value)}
                required
              >
                <option value="Arthritis">Arthritis</option>
                <option value="Diabetes">Diabetes</option>
                <option value="Acne">Acne</option>
                <option value="Hypertension">Hypertension</option>
                <option value="Digestive Disorder">Digestive Disorder</option>
                <option value="Respiratory Disorders">Respiratory Disorders</option>
                <option value="Chronic Insomnia">Chronic Insomnia</option>
              </select>
            </div>
            <div className="form-group">
              <label className="font-semibold">Ayurvedic Intervention *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Shallaki & Guggulu Extract 500mg BD"
                value={formData.intervention}
                onChange={(e) => handleFieldChange('intervention', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row-grid">
            <div className="form-group">
              <label className="font-semibold">City / Location *</label>
              <select
                className="form-select"
                value={formData.city}
                onChange={(e) => handleFieldChange('city', e.target.value)}
                required
              >
                <option value="Mumbai">Mumbai</option>
                <option value="Delhi">Delhi</option>
                <option value="Kolkata">Kolkata</option>
                <option value="Kerala">Kerala</option>
                <option value="Lucknow">Lucknow</option>
                <option value="Noida">Noida</option>
                <option value="Jaipur">Jaipur</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Bengaluru">Bengaluru</option>
              </select>
            </div>
            <div className="form-group">
              <label className="font-semibold">Hospital / Clinical Site *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. AIIA Partner Clinical Hospital"
                value={formData.hospital_name}
                onChange={(e) => handleFieldChange('hospital_name', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row-grid">
            <div className="form-group">
              <label className="font-semibold">Principal Investigator *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Dr. Ananya Sharma"
                value={formData.pi_name}
                onChange={(e) => handleFieldChange('pi_name', e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="font-semibold">Target Participants *</label>
              <input
                type="number"
                className="form-input"
                min="10"
                max="1000"
                value={formData.target_participants}
                onChange={(e) => handleFieldChange('target_participants', parseInt(e.target.value))}
                required
              />
            </div>
            <div className="form-group">
              <label className="font-semibold">Duration (Weeks) *</label>
              <input
                type="number"
                className="form-input"
                min="1"
                max="104"
                value={formData.duration_weeks}
                onChange={(e) => handleFieldChange('duration_weeks', parseInt(e.target.value))}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="font-semibold">Trial Description & Protocol Synopsis</label>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="Describe therapeutic objectives and methodology..."
              value={formData.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
            />
          </div>

          <div className="form-row-grid">
            <div className="form-group">
              <label className="font-semibold">Ethics Approval Status</label>
              <select
                className="form-select"
                value={formData.ethics_approval_status}
                onChange={(e) => handleFieldChange('ethics_approval_status', e.target.value)}
              >
                <option value="Approved">Approved</option>
                <option value="Pending">Pending</option>
              </select>
            </div>
            <div className="form-group">
              <label className="font-semibold">CTRI Registration Status</label>
              <select
                className="form-select"
                value={formData.ctri_registration_status}
                onChange={(e) => handleFieldChange('ctri_registration_status', e.target.value)}
              >
                <option value="Registered">Registered</option>
                <option value="Submitted">Submitted</option>
              </select>
            </div>
            <div className="form-group">
              <label className="font-semibold">Regulatory Status (NDCT 2019)</label>
              <select
                className="form-select"
                value={formData.regulatory_status}
                onChange={(e) => handleFieldChange('regulatory_status', e.target.value)}
              >
                <option value="Approved">Approved</option>
                <option value="Under Review">Under Review</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t mt-4">
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary flex items-center gap-1"
              disabled={submitting}
            >
              {submitting ? 'Registering...' : 'Save & Register Trial'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
