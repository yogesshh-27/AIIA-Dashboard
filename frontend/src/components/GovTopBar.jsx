import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Eye, Type } from 'lucide-react';

export default function GovTopBar() {
  const { t, i18n } = useTranslation();
  const [fontSize, setFontSize] = useState(() => localStorage.getItem('ayurctms_font_size') || 'md');
  const [contrast, setContrast] = useState(() => localStorage.getItem('ayurctms_contrast') || 'standard');
  const [currentLang, setCurrentLang] = useState(() => i18n.language || 'en');

  useEffect(() => {
    // Apply font size class to documentElement
    document.documentElement.classList.remove('font-size-sm', 'font-size-md', 'font-size-lg');
    document.documentElement.classList.add(`font-size-${fontSize}`);
    localStorage.setItem('ayurctms_font_size', fontSize);
  }, [fontSize]);

  useEffect(() => {
    // Apply contrast theme
    document.documentElement.classList.remove('contrast-standard', 'contrast-dark', 'contrast-yellow-black');
    document.documentElement.classList.add(`contrast-${contrast}`);
    document.documentElement.setAttribute('data-contrast', contrast);
    localStorage.setItem('ayurctms_contrast', contrast);
  }, [contrast]);

  const toggleLanguage = () => {
    const nextLang = currentLang === 'en' ? 'hi' : 'en';
    i18n.changeLanguage(nextLang);
    setCurrentLang(nextLang);
    localStorage.setItem('ayurctms_lang', nextLang);
  };

  return (
    <header className="gov-top-bar" role="banner">
      {/* GIGW Skip to content accessibility link */}
      <a href="#main-content" className="gov-skip-link">
        {t('gov.skipToContent', 'Skip to Main Content')}
      </a>

      <div className="gov-top-bar-inner">
        <div className="gov-identity">
          <img
            src="/logos/national-emblem.svg"
            alt="State Emblem of India"
            className="gov-emblem-img"
            width="20"
            height="26"
          />
          <span className="gov-text">
            <strong>{t('gov.india', 'भारत सरकार')}</strong> | Government of India
          </span>
          <span className="gov-sep" aria-hidden="true">•</span>
          <img
            src="/logos/ayush-emblem.svg"
            alt="Ministry of Ayush"
            className="gov-ayush-emblem-img"
            width="22"
            height="22"
          />
          <span className="gov-text">
            <strong>{t('gov.ayush', 'आयुष मंत्रालय')}</strong> | Ministry of Ayush
          </span>
        </div>

        <div className="gov-accessibility" role="toolbar" aria-label="Accessibility and Language Controls">
          {/* Font Size Controls */}
          <div className="gov-control-group" aria-label="Font size adjustment">
            <span className="gov-control-label" aria-hidden="true"><Type size={12} /></span>
            <button
              type="button"
              className={`gov-btn-ctrl ${fontSize === 'sm' ? 'active' : ''}`}
              onClick={() => setFontSize('sm')}
              title="Decrease Font Size (A-)"
              aria-label="Decrease Font Size"
            >
              A-
            </button>
            <button
              type="button"
              className={`gov-btn-ctrl ${fontSize === 'md' ? 'active' : ''}`}
              onClick={() => setFontSize('md')}
              title="Standard Font Size (A)"
              aria-label="Standard Font Size"
            >
              A
            </button>
            <button
              type="button"
              className={`gov-btn-ctrl ${fontSize === 'lg' ? 'active' : ''}`}
              onClick={() => setFontSize('lg')}
              title="Increase Font Size (A+)"
              aria-label="Increase Font Size"
            >
              A+
            </button>
          </div>

          <span className="gov-sep" aria-hidden="true">|</span>

          {/* Contrast Controls */}
          <div className="gov-control-group" aria-label="Contrast theme selection">
            <span className="gov-control-label" aria-hidden="true"><Eye size={12} /></span>
            <button
              type="button"
              className={`gov-btn-ctrl ${contrast === 'standard' ? 'active' : ''}`}
              onClick={() => setContrast('standard')}
              title="Standard Mode"
              aria-label="Standard Contrast Mode"
            >
              Standard
            </button>
            <button
              type="button"
              className={`gov-btn-ctrl ${contrast === 'dark' ? 'active' : ''}`}
              onClick={() => setContrast('dark')}
              title="High Contrast Dark Mode"
              aria-label="High Contrast Dark Mode"
            >
              Dark
            </button>
            <button
              type="button"
              className={`gov-btn-ctrl ${contrast === 'yellow-black' ? 'active' : ''}`}
              onClick={() => setContrast('yellow-black')}
              title="Yellow on Black (GIGW High Contrast)"
              aria-label="Yellow on Black High Contrast Mode"
              style={{ color: '#fbbf24', background: contrast === 'yellow-black' ? '#1e293b' : 'transparent' }}
            >
              Y/B
            </button>
          </div>

          <span className="gov-sep" aria-hidden="true">|</span>

          {/* Language Switcher */}
          <button
            type="button"
            className="gov-lang-switcher"
            onClick={toggleLanguage}
            aria-label={`Switch language to ${currentLang === 'en' ? 'Hindi' : 'English'}`}
          >
            <Globe size={12} aria-hidden="true" />
            <span style={{ fontWeight: 700 }}>
              {currentLang === 'en' ? 'हिन्दी' : 'English'}
            </span>
          </button>

          <span className="gov-sep" aria-hidden="true">|</span>

          <span className="gov-inst-link">
            <a href="https://aiia.gov.in" target="_blank" rel="noopener noreferrer">
              aiia.gov.in ↗
            </a>
          </span>
        </div>
      </div>
      <div className="gov-tricolor-line" aria-hidden="true" />
    </header>
  );
}
