import React, { createContext, useContext, useEffect, useState } from "react";

const T = {
  en: {
    "nav.calculator": "Calculator", "nav.horoscope": "Horoscope", "nav.gemstones": "Gemstones",
    "nav.matching": "Matching", "nav.dashboard": "Dashboard", "nav.admin": "Admin",
    "nav.login": "Login", "nav.getStarted": "Get Started", "nav.logout": "Logout",
    "nav.about": "About Rashify", "menu.theme": "Toggle day / night", "menu.language": "Language",
    "greet.morning": "Good morning, visitor!", "greet.evening": "Good evening, visitor!",
    "hero.badge": "Vedic Astrology · Reimagined", "hero.ctaCalculate": "Calculate My Rashi",
    "hero.ctaMatch": "Match Kundali",
    "home.dailyTitle": "Today's Horoscope", "home.dailyDesc": "Pick your rashi for a fresh daily reading.",
    "home.matchTitle": "Kundali Matching", "home.matchDesc": "Check 36-point Guna Milan compatibility for marriage.",
    "home.matchCta": "Match Two Kundalis",
    "calc.title": "Rashi Calculator", "calc.name": "Full Name", "calc.gender": "Gender",
    "calc.dob": "Date of Birth", "calc.time": "Birth Time (24-hour)", "calc.place": "Exact Birth Place",
    "calc.problem": "Current Situation / Problem (for gemstone match)", "calc.submit": "Reveal My Rashi & Gemstone",
    "match.title": "Kundali Matching", "match.subtitle": "36-point Ashtakoot Guna Milan for marriage compatibility.",
    "match.boy": "Boy's Details", "match.girl": "Girl's Details", "match.compute": "Match Kundalis",
    "match.of": "of", "match.points": "points",
    "common.dasha_insights": "Get AI insights for this period",
  },
  hi: {
    "nav.calculator": "कैलकुलेटर", "nav.horoscope": "राशिफल", "nav.gemstones": "रत्न",
    "nav.matching": "मिलान", "nav.dashboard": "डैशबोर्ड", "nav.admin": "एडमिन",
    "nav.login": "लॉगिन", "nav.getStarted": "शुरू करें", "nav.logout": "लॉगआउट",
    "nav.about": "Rashify के बारे में", "menu.theme": "दिन / रात बदलें", "menu.language": "भाषा",
    "greet.morning": "सुप्रभात, आगंतुक!", "greet.evening": "शुभ संध्या, आगंतुक!",
    "hero.badge": "वैदिक ज्योतिष · नए अंदाज़ में", "hero.ctaCalculate": "मेरी राशि जानें",
    "hero.ctaMatch": "कुंडली मिलान",
    "home.dailyTitle": "आज का राशिफल", "home.dailyDesc": "अपनी राशि चुनें और आज का फल पढ़ें।",
    "home.matchTitle": "कुंडली मिलान", "home.matchDesc": "विवाह के लिए 36 गुण मिलान जाँचें।",
    "home.matchCta": "दो कुंडलियाँ मिलाएँ",
    "calc.title": "राशि कैलकुलेटर", "calc.name": "पूरा नाम", "calc.gender": "लिंग",
    "calc.dob": "जन्म तिथि", "calc.time": "जन्म समय (24 घंटे)", "calc.place": "सटीक जन्म स्थान",
    "calc.problem": "वर्तमान समस्या (रत्न सुझाव हेतु)", "calc.submit": "मेरी राशि व रत्न बताएँ",
    "match.title": "कुंडली मिलान", "match.subtitle": "विवाह अनुकूलता हेतु 36 अष्टकूट गुण मिलान।",
    "match.boy": "वर का विवरण", "match.girl": "वधू का विवरण", "match.compute": "कुंडली मिलाएँ",
    "match.of": "में से", "match.points": "अंक",
    "common.dasha_insights": "इस दशा हेतु AI मार्गदर्शन पाएँ",
  },
  bn: {
    "nav.calculator": "ক্যালকুলেটর", "nav.horoscope": "রাশিফল", "nav.gemstones": "রত্ন",
    "nav.matching": "মিলন", "nav.dashboard": "ড্যাশবোর্ড", "nav.admin": "অ্যাডমিন",
    "nav.login": "লগইন", "nav.getStarted": "শুরু করুন", "nav.logout": "লগআউট",
    "nav.about": "Rashify সম্পর্কে", "menu.theme": "দিন / রাত পরিবর্তন", "menu.language": "ভাষা",
    "greet.morning": "সুপ্রভাত, অতিথি!", "greet.evening": "শুভ সন্ধ্যা, অতিথি!",
    "hero.badge": "বৈদিক জ্যোতিষ · নতুন রূপে", "hero.ctaCalculate": "আমার রাশি জানুন",
    "hero.ctaMatch": "কুণ্ডলী মিলন",
    "home.dailyTitle": "আজকের রাশিফল", "home.dailyDesc": "আপনার রাশি বেছে আজকের ফল পড়ুন।",
    "home.matchTitle": "কুণ্ডলী মিলন", "home.matchDesc": "বিবাহের জন্য ৩৬ গুণ মিলন যাচাই করুন।",
    "home.matchCta": "দুটি কুণ্ডলী মিলান",
    "calc.title": "রাশি ক্যালকুলেটর", "calc.name": "পুরো নাম", "calc.gender": "লিঙ্গ",
    "calc.dob": "জন্ম তারিখ", "calc.time": "জন্ম সময় (২৪ ঘণ্টা)", "calc.place": "সঠিক জন্মস্থান",
    "calc.problem": "বর্তমান সমস্যা (রত্ন নির্বাচনের জন্য)", "calc.submit": "আমার রাশি ও রত্ন দেখান",
    "match.title": "কুণ্ডলী মিলন", "match.subtitle": "বিবাহ সামঞ্জস্যের জন্য ৩৬ অষ্টকূট গুণ মিলন।",
    "match.boy": "বরের বিবরণ", "match.girl": "কনের বিবরণ", "match.compute": "কুণ্ডলী মিলান",
    "match.of": "এর মধ্যে", "match.points": "পয়েন্ট",
    "common.dasha_insights": "এই দশার জন্য AI দিকনির্দেশনা নিন",
  },
};

export const LANGS = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "bn", label: "বাংলা" },
];

const I18nContext = createContext(null);
export const useI18n = () => useContext(I18nContext);

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(() => localStorage.getItem("rs_lang") || "en");
  const setLang = (l) => { localStorage.setItem("rs_lang", l); setLangState(l); };
  const t = (key) => (T[lang] && T[lang][key]) || T.en[key] || key;
  return <I18nContext.Provider value={{ lang, setLang, t }}>{children}</I18nContext.Provider>;
}
