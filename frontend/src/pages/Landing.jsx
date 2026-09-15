import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, Gem, Moon, Sun, Star, Clock, MapPin, ArrowRight, Shield, Heart } from "lucide-react";
import StarField from "../components/StarField";
import { RASHIS } from "../data/rashis";
import { useTheme } from "../context/ThemeContext";
import { useI18n } from "../i18n";
import api from "../lib/api";

function DailyHoroscopeWidget() {
  const { t, lang } = useI18n();
  const [rashi, setRashi] = useState(RASHIS[0]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setLoading(true); setData(null);
    api.get(`/horoscope/${rashi.key}?period=daily&language=${lang}`).then((r) => setData(r.data)).finally(() => setLoading(false));
  }, [rashi, lang]);
  return (
    <div className="rs-card p-6" data-testid="home-daily-horoscope">
      <h3 className="flex items-center gap-2 font-serif text-2xl text-amber-100"><Sparkles className="h-5 w-5 text-amber-400" /> {t("home.dailyTitle")}</h3>
      <p className="mb-4 mt-1 text-sm text-slate-400">{t("home.dailyDesc")}</p>
      <div className="mb-4 flex flex-wrap gap-1.5">
        {RASHIS.map((r) => (
          <button key={r.key} onClick={() => setRashi(r)} data-testid={`home-rashi-${r.key}`}
            className={`rs-tap rounded-full px-2.5 py-1 text-xs transition-colors ${rashi.key === r.key ? "rs-gold-btn" : "border border-amber-500/20 text-slate-300 hover:text-amber-200"}`}>
            {r.glyph} {r.sa}
          </button>
        ))}
      </div>
      <div className="min-h-[72px] rounded-xl border border-amber-500/15 bg-[#090A15]/50 p-4 text-sm leading-relaxed text-slate-300">
        {loading ? <span className="text-slate-500">Reading the stars…</span> : data?.forecast?.overview}
      </div>
      <Link to="/horoscope" className="mt-3 inline-flex items-center gap-1 text-sm text-amber-300 hover:underline">Full weekly &amp; yearly forecast <ArrowRight className="h-3.5 w-3.5" /></Link>
    </div>
  );
}

const FEATURES = [
  { icon: Moon, title: "Accurate Rashi", desc: "Your true Vedic Moon-sign computed from date, exact 24h time and birth place." },
  { icon: Sparkles, title: "AI Horoscope", desc: "Personalised readings across career, love, health & wealth powered by Vedic logic + AI." },
  { icon: Gem, title: "Gemstone Remedy", desc: "The exact stone that empowers your ruling planet — with wear rituals & mantras." },
  { icon: Star, title: "Full Kundali", desc: "North-Indian birth chart with planetary placements, Nakshatra & Lagna." },
];

export default function Landing() {
  const { mode, greetKey } = useTheme();
  const { t } = useI18n();
  const isLight = mode === "light";

  return (
    <div className="relative rs-cosmic">
      {!isLight && <StarField count={70} />}
      <div className="relative z-10">
        {/* Hero */}
        <section className="mx-auto max-w-7xl px-5 pt-16 pb-20 sm:pt-24">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <div data-testid="home-greeting" className="mb-3 font-serif text-2xl text-amber-300 sm:text-3xl">{t(greetKey)}</div>
              <span className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs uppercase tracking-[0.2em] ${isLight ? "border-amber-600/40 bg-amber-500/15 text-amber-700" : "border-amber-500/30 bg-amber-500/10 text-amber-300"}`}>
                <Sparkles className="h-3.5 w-3.5" /> {t("hero.badge")}
              </span>
              <h1 data-testid="hero-headline" className={`mt-6 font-serif text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl ${isLight ? "text-slate-800" : ""}`}>
                <span className="rs-gold-text">Discover Your Cosmic</span><br />
                <span className={isLight ? "text-slate-800" : "text-slate-100"}>Alignment & True Rashi</span>
              </h1>
              <p data-testid="hero-subtitle" className={`mt-5 max-w-lg text-base leading-relaxed sm:text-lg ${isLight ? "text-slate-600" : "text-slate-300"}`}>
                Enter your birth date, exact time and place. Rashify reveals your real Vedic Rashi, a personalised horoscope, and the precise gemstone that can turn your situation around.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link to="/calculator" data-testid="hero-calculate-cta-button" className="rs-gold-btn rs-tap flex items-center gap-2 rounded-full px-7 py-3.5 text-base">
                  {t("hero.ctaCalculate")} <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/matching" data-testid="hero-match-cta-button" className={`rs-tap flex items-center gap-2 rounded-full border px-7 py-3.5 text-base transition-colors ${isLight ? "border-amber-600/40 text-slate-700 hover:border-amber-500" : "border-amber-500/30 text-amber-100 hover:border-amber-400/60"}`}>
                  <Heart className="h-4 w-4" /> {t("hero.ctaMatch")}
                </Link>
              </div>
              <div className="mt-8 flex flex-wrap items-center gap-5 text-sm text-slate-400">
                <span className="flex items-center gap-1.5"><Clock className="h-4 w-4 text-amber-400" /> 24-hour precision</span>
                <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4 text-amber-400" /> Location aware</span>
                <span className="flex items-center gap-1.5"><Shield className="h-4 w-4 text-amber-400" /> Private & secure</span>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8 }} className="relative mx-auto">
              <div className="relative aspect-square w-72 sm:w-96">
                {isLight && <div className="rs-sun absolute -right-2 -top-2 h-28 w-28 rounded-full" />}
                <div className="absolute inset-0 rounded-full border border-amber-500/20 rs-spin-slow" />
                <div className="absolute inset-6 rounded-full border border-amber-500/10" />
                <img src="https://images.unsplash.com/photo-1729335511904-9b8690184935?crop=entropy&cs=srgb&fm=jpg&q=85&w=800" alt="Zodiac wheel" className="absolute inset-3 h-[calc(100%-1.5rem)] w-[calc(100%-1.5rem)] rounded-full object-cover opacity-90 shadow-[0_0_60px_rgba(226,158,56,0.25)]" />
                {!isLight && <div className="absolute inset-0 rounded-full bg-gradient-to-t from-[#0B0D1B] via-transparent to-transparent" />}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Rashi ticker */}
        <section className="border-y border-amber-500/15 bg-[#0B0D1B]/50 py-6 overflow-hidden">
          <div className="flex w-max rs-ticker gap-4">
            {[...RASHIS, ...RASHIS].map((r, i) => (
              <div key={i} data-testid={i < 12 ? `rashi-ticker-item-${r.key}` : undefined} className="flex items-center gap-3 rounded-full border border-amber-500/20 bg-white/5 px-5 py-2.5 whitespace-nowrap">
                <span className="text-2xl text-amber-300">{r.glyph}</span>
                <span className="font-serif text-lg text-amber-100">{r.sa}</span>
                <span className="text-xs text-slate-400">{r.en}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section className="mx-auto max-w-7xl px-5 py-20">
          <div className="mb-12 text-center">
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/90">What you get</span>
            <h2 className="mt-2 font-serif text-3xl text-amber-100 sm:text-4xl">Ancient wisdom, modern clarity</h2>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f, i) => (
              <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.08 }} className="rs-card p-6">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-500/15"><f.icon className="h-5 w-5 text-amber-300" /></span>
                <h3 className="mt-4 font-serif text-xl text-amber-50">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Home: Daily Horoscope + Matching */}
        <section className="mx-auto max-w-7xl px-5 pb-8">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <DailyHoroscopeWidget />
            <div className="rs-card relative flex flex-col justify-between overflow-hidden p-6" data-testid="home-matching-card">
              <div className="absolute -right-6 -top-6 opacity-10"><Heart className="h-40 w-40 text-rose-400" /></div>
              <div className="relative">
                <h3 className="flex items-center gap-2 font-serif text-2xl text-amber-100"><Heart className="h-5 w-5 text-rose-400" /> {t("home.matchTitle")}</h3>
                <p className="mt-1 max-w-sm text-sm text-slate-400">{t("home.matchDesc")}</p>
                <div className="mt-5 flex items-center gap-3 text-sm text-slate-300">
                  <span className="rounded-full bg-sky-500/15 px-3 py-1 text-sky-300">Boy</span>
                  <Heart className="h-4 w-4 text-rose-400" />
                  <span className="rounded-full bg-rose-500/15 px-3 py-1 text-rose-300">Girl</span>
                  <span className="ml-2 font-serif text-2xl rs-gold-text">36</span>
                  <span className="text-xs text-slate-500">{t("match.points")}</span>
                </div>
              </div>
              <Link to="/matching" data-testid="home-match-cta" className="rs-gold-btn rs-tap relative mt-6 inline-flex w-max items-center gap-2 rounded-full px-6 py-3">
                {t("home.matchCta")} <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="mx-auto max-w-4xl px-5 pb-24">
          <div className="rs-card relative overflow-hidden p-10 text-center">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 via-purple-900/10 to-teal-500/10" />
            <div className="relative">
              <h2 className="font-serif text-3xl text-amber-100 sm:text-4xl">Your stars are waiting</h2>
              <p className="mx-auto mt-3 max-w-md text-slate-300">Find your true rashi and the gemstone destined to lift your fortune — in under a minute.</p>
              <Link to="/calculator" className="rs-gold-btn mt-7 inline-flex items-center gap-2 rounded-full px-8 py-3.5">Begin Reading <ArrowRight className="h-4 w-4" /></Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
