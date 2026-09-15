import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { User, Calendar, Clock, MapPin, HelpCircle, Sparkles, Save, Users } from "lucide-react";
import api, { formatApiError } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import StarField from "../components/StarField";
import ResultView from "../components/ResultView";

const empty = { name: "", gender: "Male", dob: "", time: "", place: "", problem: "" };

export default function Calculator() {
  const { user, loading } = useAuth();
  const loc = useLocation();
  const [form, setForm] = useState(empty);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [profiles, setProfiles] = useState([]);
  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  useEffect(() => {
    if (loc.state?.profile) {
      const p = loc.state.profile;
      setForm({ name: p.name || "", gender: p.gender || "Male", dob: p.dob || "", time: p.time || "", place: p.place || "", problem: "" });
    }
  }, [loc.state]);

  const loadProfiles = () => {
    if (user) api.get("/profiles").then((r) => setProfiles(r.data)).catch(() => {});
  };
  useEffect(loadProfiles, [user]);

  const applyProfile = (p) => {
    setForm({ name: p.name || "", gender: p.gender || "Male", dob: p.dob || "", time: p.time || "", place: p.place || "", problem: form.problem });
    toast.success(`Loaded ${p.name}'s details`);
  };

  const saveProfile = async () => {
    if (!form.name || !form.dob || !form.time || !form.place) {
      toast.error("Fill name, date, time and place first.");
      return;
    }
    try {
      await api.post("/profiles", { name: form.name, relation: "Family", gender: form.gender, dob: form.dob, time: form.time, place: form.place });
      toast.success(`Saved ${form.name} to your profiles`);
      loadProfiles();
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!form.dob || !form.time || !form.place || !form.name) {
      toast.error("Please fill name, date, time and place.");
      return;
    }
    setBusy(true);
    setResult(null);
    try {
      const res = await api.post("/rashi/calculate", form);
      setResult(res.data);
      if (res.data.saved) toast.success("Reading saved to your dashboard!");
      setTimeout(() => document.getElementById("rs-result")?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail) || err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={50} />
      <div className="relative z-10 mx-auto max-w-6xl px-5 py-12">
        <div className="mb-10 text-center">
          <span className="text-xs uppercase tracking-[0.2em] text-amber-400/90">Birth Details</span>
          <h1 className="mt-2 font-serif text-4xl text-amber-100 sm:text-5xl">Rashi Calculator</h1>
          <p className="mx-auto mt-3 max-w-xl text-slate-400">Provide your exact birth information for an accurate Vedic reading and gemstone remedy.</p>
        </div>

        <form onSubmit={submit} className="rs-card mx-auto max-w-3xl p-6 sm:p-8">
          {user && profiles.length > 0 && (
            <div className="mb-5">
              <span className="mb-2 flex items-center gap-1.5 text-xs uppercase tracking-wider text-amber-400/80"><Users className="h-3.5 w-3.5" /> Load a saved profile</span>
              <div className="flex flex-wrap gap-2">
                {profiles.map((p) => (
                  <button key={p.id} type="button" onClick={() => applyProfile(p)} data-testid={`calc-profile-chip-${p.id}`}
                    className="rounded-full border border-amber-500/25 bg-white/5 px-3 py-1.5 text-sm text-slate-200 hover:border-amber-400/60 hover:text-amber-200 transition-colors">
                    {p.name} <span className="text-slate-500">· {p.relation}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Field label="Full Name" icon={User}>
              <input data-testid="birth-form-name-input" value={form.name} onChange={upd("name")} placeholder="e.g. Arjun Sharma" className={inputCls} />
            </Field>
            <Field label="Gender" icon={User}>
              <select data-testid="birth-form-gender-input" value={form.gender} onChange={upd("gender")} className={inputCls}>
                <option className="bg-[#13102B]">Male</option>
                <option className="bg-[#13102B]">Female</option>
                <option className="bg-[#13102B]">Other</option>
              </select>
            </Field>
            <Field label="Date of Birth" icon={Calendar}>
              <input data-testid="birth-form-dob-input" type="date" value={form.dob} onChange={upd("dob")} className={inputCls} />
            </Field>
            <Field label="Birth Time (24-hour)" icon={Clock}>
              <input data-testid="birth-form-time-input" type="time" value={form.time} onChange={upd("time")} className={inputCls} />
            </Field>
            <div className="sm:col-span-2">
              <Field label="Exact Birth Place" icon={MapPin}>
                <input data-testid="birth-form-location-input" value={form.place} onChange={upd("place")} placeholder="City, State, Country" className={inputCls} />
              </Field>
            </div>
            <div className="sm:col-span-2">
              <Field label="Current Situation / Problem (for gemstone match)" icon={HelpCircle}>
                <textarea data-testid="birth-form-problem-textarea" value={form.problem} onChange={upd("problem")} rows={3} placeholder="e.g. career growth is stuck, financial delays, health & stress…" className={`${inputCls} resize-none`} />
              </Field>
            </div>
          </div>

          {!user && !loading && (
            <p className="mt-4 text-center text-xs text-slate-400">Tip: <a href="/auth?mode=signup" className="text-amber-300 hover:underline">create a free account</a> to save your readings.</p>
          )}

          <button type="submit" disabled={busy} data-testid="birth-form-submit-button" className="rs-gold-btn mt-6 flex w-full items-center justify-center gap-2 rounded-xl py-3.5 text-base disabled:opacity-60">
            {busy ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-[#0B0D1B]/40 border-t-[#0B0D1B]" /> Consulting the stars…</> : <><Sparkles className="h-5 w-5" /> Reveal My Rashi & Gemstone</>}
          </button>
          {user && (
            <button type="button" onClick={saveProfile} data-testid="calc-save-profile-button" className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-amber-500/30 py-3 text-sm text-amber-200 hover:border-amber-400/60 transition-colors">
              <Save className="h-4 w-4" /> Save these details as a family profile
            </button>
          )}
        </form>

        {result && (
          <motion.div id="rs-result" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mt-14">
            <div className="mb-8 text-center">
              <h2 className="font-serif text-3xl text-amber-100">Reading for {result.input.name}</h2>
              <p className="text-sm text-slate-400">{result.input.dob} · {result.input.time} · {result.input.place}</p>
            </div>
            <ResultView result={result} />
          </motion.div>
        )}
      </div>
    </div>
  );
}

const inputCls = "w-full rounded-xl border border-amber-500/20 bg-[#090A15]/60 px-4 py-3 text-slate-100 placeholder:text-slate-500 outline-none transition-colors focus:border-amber-400/60 focus:ring-2 focus:ring-amber-500/20";

function Field({ label, icon: Icon, children }) {
  return (
    <label className="block">
      <span className="mb-1.5 flex items-center gap-1.5 text-xs uppercase tracking-wider text-amber-400/80"><Icon className="h-3.5 w-3.5" /> {label}</span>
      {children}
    </label>
  );
}
