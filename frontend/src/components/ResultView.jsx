import React, { useState } from "react";
import { motion } from "framer-motion";
import { Sun, Moon, ArrowUpRight, Star, Sparkles, Gem, Briefcase, Heart, Activity, Coins, Flower2, Palette, Hash } from "lucide-react";
import KundaliChart from "./KundaliChart";

const GEM_IMG = {
  Ruby: "https://images.unsplash.com/photo-1653405507161-da7d205d86f4?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
  Emerald: "https://images.unsplash.com/photo-1600119612651-0db31b3a7baa?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
  Diamond: "https://images.unsplash.com/photo-1679531751641-79f78cbb5c0b?crop=entropy&cs=srgb&fm=jpg&q=85&w=400",
};
const DEFAULT_GEM_IMG = "https://images.unsplash.com/photo-1653405507161-da7d205d86f4?crop=entropy&cs=srgb&fm=jpg&q=85&w=400";

const TABS = [
  { key: "career", label: "Career & Finance", icon: Briefcase, testid: "horoscope-content-career" },
  { key: "love", label: "Love & Relationships", icon: Heart, testid: "horoscope-content-love" },
  { key: "health", label: "Health & Energy", icon: Activity, testid: "horoscope-content-health" },
  { key: "wealth", label: "Wealth & Prosperity", icon: Coins, testid: "horoscope-content-wealth" },
  { key: "spiritual", label: "Spiritual Guidance", icon: Flower2, testid: "horoscope-content-spiritual" },
];

function Stat({ icon: Icon, label, value, testid }) {
  return (
    <div data-testid={testid} className="rs-card p-4 text-center">
      <Icon className="mx-auto mb-2 h-5 w-5 text-amber-400" />
      <div className="text-[11px] uppercase tracking-widest text-amber-400/80">{label}</div>
      <div className="mt-1 font-serif text-xl text-amber-50">{value}</div>
    </div>
  );
}

export default function ResultView({ result }) {
  const { chart, gemstone, reading } = result;
  const [tab, setTab] = useState("career");
  const activeTab = TABS.find((t) => t.key === tab);
  const gemImg = GEM_IMG[gemstone.name] || DEFAULT_GEM_IMG;

  return (
    <div className="space-y-8">
      {/* Signs summary */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <Stat icon={Moon} label="Moon Rashi" value={`${chart.moon_sign.sa}`} testid="rashi-result-moon-sign" />
        <Stat icon={Sun} label="Sun Sign" value={chart.sun_sign.sa} testid="rashi-result-sun-sign" />
        <Stat icon={ArrowUpRight} label="Ascendant" value={chart.ascendant.sa} testid="rashi-result-ascendant" />
        <Stat icon={Star} label="Nakshatra" value={`${chart.nakshatra} (${chart.pada})`} testid="rashi-result-nakshatra" />
        <Stat icon={Sparkles} label="Ruling Planet" value={chart.ruling_planet} testid="rashi-result-ruling-planet" />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Kundali */}
        <div className="rs-card p-6">
          <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-serif text-2xl text-amber-100">Your Kundali</h3>
            {chart.accuracy === "swiss_ephemeris_lahiri" && (
              <span className="flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-[10px] uppercase tracking-wider text-amber-300">
                <Sparkles className="h-3 w-3" /> Swiss Ephemeris · Lahiri
              </span>
            )}
          </div>
          <p className="mb-1 text-sm text-slate-400">North Indian chart · {chart.moon_sign.en} Moon · {chart.moon_sign.element} element</p>
          {chart.birth_location && (
            <p className="mb-5 text-xs text-slate-500">📍 {chart.birth_location.matched} · {chart.birth_location.tz}{typeof chart.ayanamsa === "number" ? ` · Ayanamsa ${chart.ayanamsa}°` : ""}</p>
          )}
          <KundaliChart chart={chart} />
          <div className="mt-5 grid grid-cols-3 gap-2 text-center text-xs">
            {Object.entries(chart.planet_positions).map(([p, s]) => (
              <div key={p} className="rounded-lg border border-amber-500/15 bg-white/5 px-2 py-1.5">
                <span className="text-amber-300">{p}</span>
                <span className="block text-slate-400">{s}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Reading summary */}
        <div className="rs-card p-6">
          <h3 className="mb-4 font-serif text-2xl text-amber-100">Cosmic Reading</h3>
          <p className="mb-5 text-base leading-relaxed text-slate-300">{reading.summary}</p>
          <div className="grid grid-cols-2 gap-3 mb-5">
            <div className="flex items-center gap-2 rounded-lg border border-amber-500/15 bg-white/5 px-3 py-2.5">
              <Palette className="h-4 w-4 text-amber-400" />
              <div><div className="text-[10px] uppercase tracking-wider text-amber-400/70">Lucky Colour</div><div className="text-sm text-slate-100">{reading.lucky_color}</div></div>
            </div>
            <div className="flex items-center gap-2 rounded-lg border border-amber-500/15 bg-white/5 px-3 py-2.5">
              <Hash className="h-4 w-4 text-amber-400" />
              <div><div className="text-[10px] uppercase tracking-wider text-amber-400/70">Lucky Number</div><div className="text-sm text-slate-100">{reading.lucky_number}</div></div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {TABS.map((t) => (
              <button key={t.key} onClick={() => setTab(t.key)} data-testid={`horoscope-tab-${t.key}`}
                className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${tab === t.key ? "rs-gold-btn" : "border border-amber-500/25 text-slate-300 hover:text-amber-200"}`}>
                <t.icon className="h-3.5 w-3.5" /> {t.label.split(" ")[0]}
              </button>
            ))}
          </div>
          <motion.div key={tab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}
            data-testid={activeTab.testid} className="mt-4 rounded-xl border border-amber-500/15 bg-[#090A15]/60 p-4">
            <div className="mb-1 flex items-center gap-2 text-amber-300"><activeTab.icon className="h-4 w-4" /><span className="font-medium">{activeTab.label}</span></div>
            <p className="text-sm leading-relaxed text-slate-300">{reading[tab]}</p>
          </motion.div>
        </div>
      </div>

      {/* Gemstone recommendation */}
      <div data-testid="gemstone-recommendation-card" className="rs-card overflow-hidden p-0">
        <div className="grid grid-cols-1 md:grid-cols-5">
          <div className="relative md:col-span-2">
            <img data-testid="gemstone-image-preview" src={gemImg} alt={gemstone.name} className="h-56 w-full object-cover md:h-full" />
            <div className="absolute inset-0 bg-gradient-to-t from-[#0B0D1B] via-transparent to-transparent md:bg-gradient-to-r" />
          </div>
          <div className="p-6 sm:p-8 md:col-span-3">
            <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-amber-400/80"><Gem className="h-4 w-4" /> Recommended Gemstone</div>
            <h3 data-testid="gemstone-name-title" className="font-serif text-3xl rs-gold-text">{gemstone.name} <span className="text-amber-200/70 text-2xl">/ {gemstone.name_sa}</span></h3>
            <p data-testid="gemstone-problem-match-reason" className="mt-3 text-sm leading-relaxed text-slate-300">{reading.gemstone_reason}</p>

            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
              {[["Metal", gemstone.metal, "gemstone-metal-instruction"], ["Finger", gemstone.finger, "gemstone-finger-instruction"], ["Day", gemstone.day], ["Weight", gemstone.weight], ["Planet", gemstone.planet], ["Colour", gemstone.color]].map(([l, v, tid]) => (
                <div key={l} data-testid={tid} className="rounded-lg border border-amber-500/15 bg-white/5 px-3 py-2">
                  <div className="text-[10px] uppercase tracking-wider text-amber-400/70">{l}</div>
                  <div className="text-sm text-slate-100">{v}</div>
                </div>
              ))}
            </div>

            <div data-testid="gemstone-mantra-box" className="mt-4 rounded-xl border border-amber-500/25 bg-amber-500/5 p-4">
              <div className="text-[10px] uppercase tracking-widest text-amber-400/80">Activation Mantra</div>
              <div className="font-serif text-lg text-amber-100">{gemstone.mantra}</div>
              <p className="mt-2 text-xs text-slate-400"><span className="text-amber-300/90">Benefits:</span> {gemstone.benefits}</p>
              <p className="mt-1 text-xs text-slate-400"><span className="text-rose-300/90">Caution:</span> {gemstone.caution}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
