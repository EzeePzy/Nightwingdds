import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Briefcase, Heart, Activity, Coins, Palette, Hash, Sparkles } from "lucide-react";
import api from "../lib/api";
import { RASHIS } from "../data/rashis";
import StarField from "../components/StarField";

const PERIODS = [
  { key: "daily", label: "Daily" },
  { key: "weekly", label: "Weekly" },
  { key: "yearly", label: "Yearly" },
];
const PILLARS = [
  { key: "career", label: "Career", icon: Briefcase },
  { key: "love", label: "Love", icon: Heart },
  { key: "health", label: "Health", icon: Activity },
  { key: "finance", label: "Finance", icon: Coins },
];

export default function Horoscope() {
  const [rashi, setRashi] = useState(RASHIS[0]);
  const [period, setPeriod] = useState("daily");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    setData(null);
    api.get(`/horoscope/${rashi.key}?period=${period}`)
      .then((r) => setData(r.data))
      .finally(() => setLoading(false));
  }, [rashi, period]);

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={50} />
      <div className="relative z-10 mx-auto max-w-5xl px-5 py-12">
        <div className="mb-8 text-center">
          <span className="text-xs uppercase tracking-[0.2em] text-amber-400/90">Forecast</span>
          <h1 className="mt-2 font-serif text-4xl text-amber-100 sm:text-5xl">Horoscope</h1>
          <p className="mx-auto mt-3 max-w-xl text-slate-400">Pick your rashi for a fresh daily, weekly or yearly forecast.</p>
        </div>

        {/* Rashi selector */}
        <div className="mb-6 grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-6">
          {RASHIS.map((r) => (
            <button key={r.key} onClick={() => setRashi(r)} data-testid={`horoscope-rashi-${r.key}`}
              className={`flex flex-col items-center gap-0.5 rounded-xl border px-2 py-3 transition-all ${rashi.key === r.key ? "border-amber-400/70 bg-amber-500/15" : "border-amber-500/15 bg-white/5 hover:border-amber-400/40"}`}>
              <span className="text-2xl text-amber-300">{r.glyph}</span>
              <span className="font-serif text-sm text-amber-100">{r.sa}</span>
              <span className="text-[10px] text-slate-400">{r.en}</span>
            </button>
          ))}
        </div>

        {/* Period tabs */}
        <div className="mb-8 flex justify-center gap-2">
          {PERIODS.map((p) => (
            <button key={p.key} onClick={() => setPeriod(p.key)} data-testid={`horoscope-period-${p.key}`}
              className={`rounded-full px-6 py-2 text-sm font-medium transition-colors ${period === p.key ? "rs-gold-btn" : "border border-amber-500/25 text-slate-300 hover:text-amber-200"}`}>
              {p.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><div className="h-10 w-10 animate-spin rounded-full border-2 border-amber-500/30 border-t-amber-400" /></div>
        ) : data ? (
          <motion.div key={`${rashi.key}-${period}`} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} data-testid="horoscope-forecast" className="space-y-6">
            <div className="rs-card p-6 sm:p-8">
              <div className="mb-3 flex items-center gap-3">
                <span className="text-4xl text-amber-300">{rashi.glyph}</span>
                <div>
                  <h2 className="font-serif text-2xl text-amber-100">{rashi.sa} · {rashi.en}</h2>
                  <p className="text-xs uppercase tracking-wider text-amber-400/70">{period} · {data.date_key} · Ruled by {rashi.planet}</p>
                </div>
              </div>
              <p className="text-base leading-relaxed text-slate-300">{data.forecast.overview}</p>
              <div className="mt-5 flex flex-wrap gap-3">
                <span className="flex items-center gap-2 rounded-lg border border-amber-500/20 bg-white/5 px-3 py-2 text-sm"><Palette className="h-4 w-4 text-amber-400" /> Lucky Colour: <b className="text-amber-100">{data.forecast.lucky_color}</b></span>
                <span className="flex items-center gap-2 rounded-lg border border-amber-500/20 bg-white/5 px-3 py-2 text-sm"><Hash className="h-4 w-4 text-amber-400" /> Lucky Number: <b className="text-amber-100">{data.forecast.lucky_number}</b></span>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {PILLARS.map((p) => (
                <div key={p.key} className="rs-card p-5">
                  <div className="mb-2 flex items-center gap-2 text-amber-300"><p.icon className="h-4 w-4" /><span className="font-medium">{p.label}</span></div>
                  <p className="text-sm leading-relaxed text-slate-300">{data.forecast[p.key]}</p>
                </div>
              ))}
            </div>
          </motion.div>
        ) : null}
      </div>
    </div>
  );
}
