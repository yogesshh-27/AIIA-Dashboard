import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Activity, Users, FlaskConical } from 'lucide-react';

// Fix default marker icon issue in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// India trial site coordinates with metadata
const INDIA_TRIAL_SITES = [
  { city: 'Delhi', lat: 28.6139, lng: 77.2090, trials: 3, enrolled: 8, target: 10, hospital: 'AIIA New Delhi' },
  { city: 'Mumbai', lat: 19.0760, lng: 72.8777, trials: 2, enrolled: 6, target: 8, hospital: 'KEM Hospital' },
  { city: 'Kolkata', lat: 22.5726, lng: 88.3639, trials: 1, enrolled: 4, target: 6, hospital: 'IPGMER Kolkata' },
  { city: 'Kerala', lat: 10.8505, lng: 76.2711, trials: 2, enrolled: 5, target: 7, hospital: 'Govt. Ayurveda College' },
  { city: 'Lucknow', lat: 26.8467, lng: 80.9462, trials: 1, enrolled: 3, target: 5, hospital: 'SGPGIMS Lucknow' },
  { city: 'Noida', lat: 28.5355, lng: 77.3910, trials: 1, enrolled: 2, target: 3, hospital: 'AIIA Research Extension' },
  { city: 'Jaipur', lat: 26.9124, lng: 75.7873, trials: 1, enrolled: 2, target: 4, hospital: 'NIA Jaipur' },
  { city: 'Hyderabad', lat: 17.3850, lng: 78.4867, trials: 1, enrolled: 3, target: 5, hospital: 'CCRYN Hyderabad' },
  { city: 'Bengaluru', lat: 12.9716, lng: 77.5946, trials: 1, enrolled: 4, target: 6, hospital: 'SDM Ayurveda Hospital' },
];

// Custom colored marker
function createCustomIcon(color, size = 28) {
  return L.divIcon({
    className: 'custom-map-marker',
    html: `<div style="
      background: ${color};
      width: ${size}px;
      height: ${size}px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      border: 2px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
    "><div style="
      transform: rotate(45deg);
      color: white;
      font-size: ${size * 0.4}px;
      font-weight: 700;
    ">${size > 30 ? '●' : ''}</div></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size],
  });
}

function getMarkerColor(enrolled, target) {
  const ratio = enrolled / target;
  if (ratio >= 0.8) return '#005944'; // Emerald — on track
  if (ratio >= 0.5) return '#d97706'; // Amber — moderate
  return '#dc2626'; // Red — behind
}

function getMarkerSize(trials) {
  if (trials >= 3) return 34;
  if (trials >= 2) return 28;
  return 22;
}

// Component to fit map bounds to India
function FitBounds() {
  const map = useMap();
  useEffect(() => {
    const bounds = L.latLngBounds(INDIA_TRIAL_SITES.map(s => [s.lat, s.lng]));
    map.fitBounds(bounds.pad(0.3));
  }, [map]);
  return null;
}

export default function IndiaTrialMap({ onSelectCity }) {
  const [selectedSite, setSelectedSite] = useState(null);
  const [showHeatmap, setShowHeatmap] = useState(false);

  return (
    <div className="active-trials-section-card mt-6">
      <div className="section-card-header">
        <span className="section-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MapPin size={18} className="text-emerald-700" />
          Interactive India Clinical Trial Map
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn btn-sm ${showHeatmap ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setShowHeatmap(!showHeatmap)}
            style={{ fontSize: '11px' }}
          >
            {showHeatmap ? '● Heatmap ON' : '○ Heatmap OFF'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '16px', padding: '12px 0' }}>
        {/* Map Container */}
        <div style={{ height: '420px', borderRadius: '10px', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
          <MapContainer
            center={[22.5, 78.5]}
            zoom={5}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <FitBounds />

            {INDIA_TRIAL_SITES.map((site) => (
              <React.Fragment key={site.city}>
                <Marker
                  position={[site.lat, site.lng]}
                  icon={createCustomIcon(
                    getMarkerColor(site.enrolled, site.target),
                    getMarkerSize(site.trials)
                  )}
                  eventHandlers={{
                    click: () => setSelectedSite(site),
                  }}
                >
                  <Popup>
                    <div style={{ minWidth: '200px', fontFamily: 'Inter, system-ui, sans-serif' }}>
                      <h4 style={{ margin: '0 0 8px', fontSize: '14px', fontWeight: 700, color: '#005944' }}>
                        📍 {site.city}
                      </h4>
                      <p style={{ margin: '2px 0', fontSize: '12px' }}>
                        <strong>Hospital:</strong> {site.hospital}
                      </p>
                      <p style={{ margin: '2px 0', fontSize: '12px' }}>
                        <strong>Active Trials:</strong> {site.trials}
                      </p>
                      <p style={{ margin: '2px 0', fontSize: '12px' }}>
                        <strong>Enrolled:</strong> {site.enrolled} / {site.target}
                        <span style={{
                          marginLeft: '6px',
                          color: getMarkerColor(site.enrolled, site.target),
                          fontWeight: 700,
                        }}>
                          ({Math.round(site.enrolled / site.target * 100)}%)
                        </span>
                      </p>
                    </div>
                  </Popup>
                </Marker>

                {/* Heatmap circles */}
                {showHeatmap && (
                  <CircleMarker
                    center={[site.lat, site.lng]}
                    radius={site.enrolled * 4}
                    pathOptions={{
                      fillColor: getMarkerColor(site.enrolled, site.target),
                      fillOpacity: 0.2,
                      stroke: true,
                      color: getMarkerColor(site.enrolled, site.target),
                      weight: 1,
                      opacity: 0.4,
                    }}
                  />
                )}
              </React.Fragment>
            ))}
          </MapContainer>
        </div>

        {/* Side Panel: Site Legend & Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
            Trial Sites Legend
          </div>
          <div style={{ display: 'flex', gap: '12px', fontSize: '10px', marginBottom: '8px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#005944', display: 'inline-block' }}></span>
              On Track (≥80%)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#d97706', display: 'inline-block' }}></span>
              Moderate
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#dc2626', display: 'inline-block' }}></span>
              Behind
            </span>
          </div>

          {/* Scrollable site list */}
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {INDIA_TRIAL_SITES.map((site) => (
              <button
                key={site.city}
                onClick={() => {
                  setSelectedSite(site);
                  if (onSelectCity) onSelectCity(site.city);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 10px',
                  background: selectedSite?.city === site.city ? '#f0fdf4' : '#f8fafc',
                  border: `1px solid ${selectedSite?.city === site.city ? '#86efac' : '#e2e8f0'}`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  width: '100%',
                  fontSize: '11px',
                  transition: 'all 0.15s ease',
                }}
              >
                <span style={{
                  width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                  background: getMarkerColor(site.enrolled, site.target),
                }}></span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, color: '#1e293b' }}>{site.city}</div>
                  <div style={{ color: '#64748b', fontSize: '10px' }}>
                    {site.trials} trial{site.trials > 1 ? 's' : ''} • {site.enrolled}/{site.target} enrolled
                  </div>
                </div>
                <span style={{
                  fontWeight: 700, fontSize: '11px',
                  color: getMarkerColor(site.enrolled, site.target),
                }}>
                  {Math.round(site.enrolled / site.target * 100)}%
                </span>
              </button>
            ))}
          </div>

          {/* Summary Stats */}
          <div style={{
            background: '#f0fdf4', borderRadius: '8px', padding: '10px',
            border: '1px solid #bbf7d0', marginTop: '4px',
          }}>
            <div style={{ fontSize: '10px', textTransform: 'uppercase', fontWeight: 700, color: '#166534', marginBottom: '6px' }}>
              National Summary
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', fontSize: '11px' }}>
              <div><strong>{INDIA_TRIAL_SITES.reduce((s, x) => s + x.trials, 0)}</strong> Total Trials</div>
              <div><strong>{INDIA_TRIAL_SITES.length}</strong> Sites</div>
              <div><strong>{INDIA_TRIAL_SITES.reduce((s, x) => s + x.enrolled, 0)}</strong> Enrolled</div>
              <div><strong>{INDIA_TRIAL_SITES.reduce((s, x) => s + x.target, 0)}</strong> Target</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
