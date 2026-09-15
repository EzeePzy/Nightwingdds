import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Gem, ArrowRight } from "lucide-react";
import api from "../lib/api";
import StarField from "../components/StarField";

const IMG = {
  Ruby: "https://images.unsplash.com/photo-1653405507161-da7d205d86f4?crop=entropy&cs=srgb&fm=jpg&q=85&w=500",
  Emerald: "https://images.unsplash.com/photo-1600119612651-0db31b3a7baa?crop=entropy&cs=srgb&fm=jpg&q=85&w=500",
  Diamond: "https://images.unsplash.com/photo-1679531751641-79f78cbb5c0b?crop=entropy&cs=srgb&fm=jpg&q=85&w=500",
};
const FALLBACK = "https://images.unsplash.com/photo-1653405507161-da7d205d86f4?crop=entropy&cs=srgb&fm=jpg&q=85&w=500";

export default function Gemstones() {
  const [gems, setGems] = useState([]);
  useEffect(() => { api.get("/gemstones").then((r) => setGems(r.data)).catch(() => {}); }, []);

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={45} />
      <div className="relative z-10 mx-auto max-w-6xl px-5 py-12">
        <div className="mb-10 text-center">
          <span className="text-xs uppercase tracking-[0.2em] text-amber-400/90">Navaratna</span>
          <h1 className="mt-2 font-serif text-4xl text-amber-100 sm:text-5xl">The Nine Sacred Gemstones</h1>
          <p className="mx-auto mt-3 max-w-xl text-slate-400">Each planet governs a gemstone. Calculate your rashi to discover which one empowers you.</p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {gems.map((g, i) => (
            <motion.div key={g.planet} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: (i % 3) * 0.08 }} className="rs-card overflow-hidden p-0">
              <div className="relative h-44">
                <img src={IMG[g.name] || FALLBACK} alt={g.name} className="h-full w-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-[#13102B] via-transparent to-transparent" />
                <span className="absolute right-3 top-3 rounded-full bg-[#0B0D1B]/70 px-2.5 py-1 text-xs text-amber-200">{g.planet}</span>
              </div>
              <div className="p-5">
                <h3 className="font-serif text-2xl rs-gold-text">{g.name}</h3>
                <p className="text-sm text-amber-300/70">{g.name_sa}</p>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{g.benefits}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  <span className="rounded-full border border-amber-500/20 bg-white/5 px-2.5 py-1 text-slate-300">{g.metal}</span>
                  <span className="rounded-full border border-amber-500/20 bg-white/5 px-2.5 py-1 text-slate-300">{g.finger}</span>
                  <span className="rounded-full border border-amber-500/20 bg-white/5 px-2.5 py-1 text-slate-300">{g.day}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Link to="/calculator" className="rs-gold-btn inline-flex items-center gap-2 rounded-full px-8 py-3.5">Find My Gemstone <ArrowRight className="h-4 w-4" /></Link>
        </div>
      </div>
    </div>
  );
}
