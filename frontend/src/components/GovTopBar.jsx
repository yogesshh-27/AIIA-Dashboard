import React from 'react';

export default function GovTopBar() {
  return (
    <header className="gov-top-bar" role="banner">
      <div className="gov-top-bar-inner">
        <div className="gov-identity">
          <span className="gov-emblem" aria-hidden="true">🏛️</span>
          <span className="gov-text">
            <strong>भारत सरकार</strong> | Government of India
          </span>
          <span className="gov-sep">•</span>
          <span className="gov-text">
            <strong>आयुष मंत्रालय</strong> | Ministry of Ayush
          </span>
        </div>
        <div className="gov-accessibility">
          <span className="gov-inst-link">
            Official Portal: <a href="https://aiia.gov.in" target="_blank" rel="noopener noreferrer">aiia.gov.in ↗</a>
          </span>
          <span className="gov-sep">|</span>
          <span className="gov-pill-lang">अखिल भारतीय आयुर्वेद संस्थान</span>
        </div>
      </div>
      <div className="gov-tricolor-line" aria-hidden="true" />
    </header>
  );
}
