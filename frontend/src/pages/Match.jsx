import React, { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Heart, User, Calendar, Clock, Sparkles, CheckCircle2, XCircle } from "lucide-react";
import api, { formatApiError } from "../lib/api";
import { useI18n } from "../i18n";
import StarField from "../components/StarField";
import CityAutocomplete from "../components/CityAutocomplete";

const inputCls = "w-full rounded-xl border border-amber-500/20 bg-[#090A15]/60 px-4 py-3 text-slate-100 placeholder:text-slate-500 outline-none transition-colors focus:border-amber-400/60 focus:ring-2 focus:ring-amber-500/20";
const empty = { name: "", dob: "", time: "", place: "" };

function PersonForm({ label, data, set, tint }) {
  const upd = (k) => (e) => set({ ...data, [k]: e.target.value });
  return (
    <div className="rs-card p-6">
      <h3 className={`mb-4 flex items-center gap-2 font-serif text-xl ${tint}`}><User className="h-5 w-5" /> {label}</h3>
      <div className="space-y-3">
        <input data-testid={`match-${label}-name`} value={data.name} onChange={upd("name")} placeholder="Name" className={inputCls} />
        <input data-testid={`match-${label}-dob`} type="date" value={data.dob} onChange={upd("dob")} className={inputCls} />
        <input data-testid={`match-${label}-time`} type="time" value={data.time} onChange={upd("time")} className={inputCls} />
        <CityAutocomplete testid={`match-${label}-place`} value={data.place} onChange={(v) => set({ ...data, place: v })} placeholder="Birth place (type 2+ letters)" className={inputCls} />
      </div>
    </div>
  );
}

export default function Match() {
  const { t } = useI18n();
  const [boy, setBoy] = useState(empty);
  const [girl, setGirl] = useState(empty);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!boy.dob || !boy.time || !boy.place || !girl.dob || !girl.time || !girl.place) {
      toast.error("Please fill date, time and place for both.");
      return;
    }
    setBusy(true);
    setResult(null);
    try {
      const { data } = await api.post("/match", { boy, girl });
      setResult(data);
      setTimeout(() => document.getElementById("match-result")?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail) || "Match failed");
    } finally {
      setBusy(false);
    }
  };

  const pct = result ? (result.total / result.max_total) * 100 : 0;
  const good = result && result.total >= 18;

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={50} />
      <div className="relative z-10 mx-auto max-w-5xl px-5 py-12">
        <div className="mb-10 text-center">
          <span className="text-xs uppercase tracking-[0.2em] text-amber-400/90">Guna Milan</span>
          <h1 className="mt-2 font-serif text-4xl text-amber-100 sm:text-5xl">{t("match.title")}</h1>
          <p className="mx-auto mt-3 max-w-xl text-slate-400">{t("match.subtitle")}</p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <PersonForm label={t("match.boy")} data={boy} set={setBoy} tint="text-sky-300" />
          <PersonForm label={t("match.girl")} data={girl} set={setGirl} tint="text-rose-300" />
        </div>

        <div className="mt-6 text-center">
          <button onClick={submit} disabled={busy} data-testid="match-submit-button" className="rs-gold-btn inline-flex items-center gap-2 rounded-full px-8 py-3.5 disabled:opacity-60">
            {busy ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-[#0B0D1B]/40 border-t-[#0B0D1B]" /> Matching…</> : <><Heart className="h-5 w-5" /> {t("match.compute")}</>}
          </button>
        </div>

        {result && (
          <motion.div id="match-result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mt-12">
            <div data-testid="match-result-card" className="rs-card p-6 sm:p-8 text-center">
              <div className="flex items-center justify-center gap-3 text-sm text-slate-300">
                <span className="text-sky-300">{result.boy.name || "Boy"} · {result.boy.rashi}</span>
                <Heart className="h-4 w-4 text-rose-400" />
                <span className="text-rose-300">{result.girl.name || "Girl"} · {result.girl.rashi}</span>
              </div>
              <div data-testid="match-total-score" className="mt-4 font-serif text-6xl rs-gold-text">{result.total}<span className="text-2xl text-slate-500">/{result.max_total}</span></div>
              <div className="mx-auto mt-4 h-3 max-w-md overflow-hidden rounded-full bg-white/10">
                <div className={`h-full rounded-full ${good ? "bg-emerald-400" : "bg-rose-400"}`} style={{ width: `${pct}%` }} />
              </div>
              <div className={`mt-4 inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm ${good ? "bg-emerald-500/15 text-emerald-300" : "bg-rose-500/15 text-rose-300"}`}>
                {good ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />} {result.verdict}
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {result.kootas.map((k) => (
                <div key={k.name} data-testid={`koota-${k.name.replace(/\s/g, "-").toLowerCase()}`} className="rs-card flex items-center justify-between p-4">
                  <div>
                    <div className="font-serif text-lg text-amber-50">{k.name}</div>
                    <div className="text-xs text-slate-400">{k.meaning}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-serif text-xl text-amber-200">{k.obtained}<span className="text-sm text-slate-500">/{k.max}</span></div>
                    <div className="mt-1 h-1.5 w-20 overflow-hidden rounded-full bg-white/10">
                      <div className="h-full rounded-full bg-amber-400" style={{ width: `${(k.obtained / k.max) * 100}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
