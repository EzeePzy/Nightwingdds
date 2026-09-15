import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, Gem, Moon, Star, Clock, MapPin, ArrowRight, Shield } from "lucide-react";
import StarField from "../components/StarField";
import { RASHIS } from "../data/rashis";

const FEATURES = [
  { icon: Moon, title: "Accurate Rashi", desc: "Your true Vedic Moon-sign computed from date, exact 24h time and birth place." },
  { icon: Sparkles, title: "AI Horoscope", desc: "Personalised readings across career, love, health & wealth powered by Vedic logic + AI." },
  { icon: Gem, title: "Gemstone Remedy", desc: "The exact stone that empowers your ruling planet — with wear rituals & mantras." },
  { icon: Star, title: "Full Kundali", desc: "North-Indian birth chart with planetary placements, Nakshatra & Lagna." },
];

export default function Landing() {
  return (
    <div className="relative rs-cosmic">
      <StarField count={70} />
      <div className="relative z-10">
        {/* Hero */}
        <section className="mx-auto max-w-7xl px-5 pt-16 pb-20 sm:pt-24">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <span className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-4 py-1.5 text-xs uppercase tracking-[0.2em] text-amber-300">
                <Sparkles className="h-3.5 w-3.5" /> Vedic Astrology · Reimagined
              </span>
              <h1 data-testid="hero-headline" className="mt-6 font-serif text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
                <span className="rs-gold-text">Discover Your Cosmic</span><br />
                <span className="text-slate-100">Alignment & True Rashi</span>
              </h1>
              <p data-testid="hero-subtitle" className="mt-5 max-w-lg text-base leading-relaxed text-slate-300 sm:text-lg">
                Enter your birth date, exact time and place. Rashisense reveals your real Vedic Rashi, a personalised horoscope, and the precise gemstone that can turn your situation around.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link to="/calculator" data-testid="hero-calculate-cta-button" className="rs-gold-btn flex items-center gap-2 rounded-full px-7 py-3.5 text-base">
                  Calculate My Rashi <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/gemstones" data-testid="hero-gemstone-cta-button" className="flex items-center gap-2 rounded-full border border-amber-500/30 px-7 py-3.5 text-base text-amber-100 hover:border-amber-400/60 transition-colors">
                  <Gem className="h-4 w-4" /> Explore Gemstones
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
                <div className="absolute inset-0 rounded-full border border-amber-500/20 rs-spin-slow" />
                <div className="absolute inset-6 rounded-full border border-amber-500/10" />
                <img src="https://images.unsplash.com/photo-1729335511904-9b8690184935?crop=entropy&cs=srgb&fm=jpg&q=85&w=800" alt="Zodiac wheel" className="absolute inset-3 h-[calc(100%-1.5rem)] w-[calc(100%-1.5rem)] rounded-full object-cover opacity-90 shadow-[0_0_60px_rgba(226,158,56,0.25)]" />
                <div className="absolute inset-0 rounded-full bg-gradient-to-t from-[#0B0D1B] via-transparent to-transparent" />
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
