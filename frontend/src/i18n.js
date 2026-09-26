import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      gov: {
        india: "Government of India",
        ayush: "Ministry of Ayush",
        institute: "All India Institute of Ayurveda",
        officialPortal: "Official Portal",
        skipToContent: "Skip to Main Content",
        fontSize: "Font Size",
        contrast: "Contrast",
        standardContrast: "Standard",
        highContrast: "High Contrast",
        yellowBlack: "Yellow on Black",
      },
      nav: {
        dashboard: "Executive Dashboard",
        activeTrials: "Active Clinical Trials",
        ctriExplorer: "CTRI Protocol Explorer",
        patients: "Patient Cohort Registry",
        doctors: "Investigators & Faculty",
        sites: "Participating Sites",
        approvals: "Ethics & Approvals",
        gcp: "GCP Compliance Audit",
        pharmacovigilance: "Pharmacovigilance (ADR)",
        interop: "Interoperability & FHIR",
        reports: "Regulatory Reports",
        logout: "Logout",
        staffPortal: "AIIA Staff CTMS",
        patientPortal: "Patient Trial Finder",
      },
      dashboard: {
        title: "Clinical Trial Operations Center",
        subtitle: "AIIA Central Protocol Monitoring • Ayush National CTMS Gateway",
        newTrialBtn: "+ New Trial Protocol",
        analytics: "Advanced Clinical Analytics",
        velocity: "Enrollment Velocity",
        doshaRadar: "Dosha Balance Radar",
        siteComparison: "Recruitment by Site",
        mapTitle: "Interactive India Clinical Trial Map",
        heatmapOn: "● Heatmap ON",
        heatmapOff: "○ Heatmap OFF",
      },
      patient: {
        title: "Ayurveda Clinical Trial Eligibility & Matching Portal",
        subtitle: "Find clinical research trials accredited by Ministry of Ayush & AIIA near you",
        voiceSearch: "Voice Search",
        listening: "Listening...",
        fullName: "Full Name",
        age: "Age",
        gender: "Gender",
        condition: "Health Condition",
        cities: "Accessible Cities",
        distancePref: "Travel Distance Preference",
        searchBtn: "Find Matching Clinical Trials",
        resetBtn: "Reset Form",
        resultsTitle: "Matching Clinical Trials",
      },
      common: {
        loading: "Loading...",
        viewAll: "View All",
        status: "Status",
        enrolled: "Enrolled",
        target: "Target",
        active: "Active",
        completed: "Completed",
        upcoming: "Upcoming",
      }
    }
  },
  hi: {
    translation: {
      gov: {
        india: "भारत सरकार",
        ayush: "आयुष मंत्रालय",
        institute: "अखिल भारतीय आयुर्वेद संस्थान",
        officialPortal: "आधिकारिक पोर्टल",
        skipToContent: "मुख्य सामग्री पर जाएं",
        fontSize: "फ़ॉन्ट आकार",
        contrast: "कंट्रास्ट",
        standardContrast: "सामान्य",
        highContrast: "उच्च कंट्रास्ट",
        yellowBlack: "काला पर पीला",
      },
      nav: {
        dashboard: "कार्यकारी डैशबोर्ड",
        activeTrials: "सक्रिय नैदानिक परीक्षण",
        ctriExplorer: "सीटीआरआई प्रोटोकॉल एक्सप्लोरर",
        patients: "रोगी समूह रजिस्ट्री",
        doctors: "अन्वेषक एवं संकाय",
        sites: "सहभागी केंद्र",
        approvals: "नैतिकता एवं स्वीकृतियां",
        gcp: "जीसीपी अनुपालन ऑडिट",
        pharmacovigilance: "फार्माकोविजिलेंस (एडीआर)",
        interop: "इंटरऑपरेबिलिटी एवं FHIR",
        reports: "नियामक रिपोर्ट",
        logout: "लॉगआउट",
        staffPortal: "एआईआईए स्टाफ सीटीएमएस",
        patientPortal: "रोगी परीक्षण खोजक",
      },
      dashboard: {
        title: "नैदानिक परीक्षण संचालन केंद्र",
        subtitle: "एआईआईए केंद्रीय प्रोटोकॉल निगरानी • आयुष राष्ट्रीय सीटीएमएस गेटवे",
        newTrialBtn: "+ नया परीक्षण प्रोटोकॉल",
        analytics: "उन्नत नैदानिक विश्लेषण",
        velocity: "नामांकन गति",
        doshaRadar: "दोष संतुलन रडार",
        siteComparison: "केंद्र अनुसार भर्ती",
        mapTitle: "इंटरैक्टिव भारत नैदानिक परीक्षण मानचित्र",
        heatmapOn: "● हीटमैप चालू",
        heatmapOff: "○ हीटमैप बंद",
      },
      patient: {
        title: "आयुर्वेद नैदानिक परीक्षण पात्रता एवं मिलान पोर्टल",
        subtitle: "अपने निकट आयुष मंत्रालय एवं एआईआईए द्वारा मान्यता प्राप्त परीक्षण खोजें",
        voiceSearch: "वॉयस सर्च",
        listening: "सुन रहे हैं...",
        fullName: "पूरा नाम",
        age: "आयु",
        gender: "लिंग",
        condition: "स्वास्थ्य स्थिति",
        cities: "सुलभ शहर",
        distancePref: "यात्रा दूरी प्राथमिकता",
        searchBtn: "उपयुक्त नैदानिक परीक्षण खोजें",
        resetBtn: "रीसेट करें",
        resultsTitle: "उपयुक्त नैदानिक परीक्षण",
      },
      common: {
        loading: "लोड हो रहा है...",
        viewAll: "सभी देखें",
        status: "स्थिति",
        enrolled: "नामांकित",
        target: "लक्ष्य",
        active: "सक्रिय",
        completed: "पूर्ण",
        upcoming: "आगामी",
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('ayurctms_lang') || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
