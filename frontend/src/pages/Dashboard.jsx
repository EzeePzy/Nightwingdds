import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Sparkles, Trash2, Moon, Gem, ChevronDown, ChevronUp, Plus } from "lucide-react";
import api, { formatApiError } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import StarField from "../components/StarField";
import ResultView from "../components/ResultView";

export default function Dashboard() {
  const { user } = useAuth();
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState(null);

  const load = () => {
    setLoading(true);
    api.get("/readings").then((r) => setReadings(r.data)).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const remove = async (id) => {
    try {
      await api.delete(`/readings/${id}`);
      setReadings((r) => r.filter((x) => x.id !== id));
      toast.success("Reading removed");
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={45} />
      <div data-testid="dashboard-container" className="relative z-10 mx-auto max-w-6xl px-5 py-12">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/90">Namaste, {user?.name}</span>
            <h1 className="mt-1 font-serif text-4xl text-amber-100">Your Dashboard</h1>
          </div>
          <Link to="/calculator" data-testid="dashboard-add-profile-button" className="rs-gold-btn flex items-center gap-2 rounded-full px-5 py-2.5"><Plus className="h-4 w-4" /> New Reading</Link>
        </div>

        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3">
          <StatCard icon={Sparkles} label="Saved Readings" value={readings.length} />
          <StatCard icon={Moon} label="Latest Rashi" value={readings[0]?.chart?.moon_sign?.sa || "—"} />
          <StatCard icon={Gem} label="Latest Gemstone" value={readings[0]?.gemstone?.name || "—"} />
        </div>

        <h2 className="mb-4 font-serif text-2xl text-amber-100">Reading History</h2>
        {loading ? (
          <div className="flex justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-2 border-amber-500/30 border-t-amber-400" /></div>
        ) : readings.length === 0 ? (
          <div className="rs-card p-10 text-center">
            <Moon className="mx-auto h-10 w-10 text-amber-400/60" />
            <p className="mt-3 text-slate-300">No readings yet.</p>
            <Link to="/calculator" className="rs-gold-btn mt-4 inline-flex rounded-full px-6 py-2.5">Create your first reading</Link>
          </div>
        ) : (
          <div data-testid="dashboard-past-readings-list" className="space-y-4">
            {readings.map((r) => (
              <div key={r.id} className="rs-card overflow-hidden">
                <div className="flex flex-wrap items-center justify-between gap-3 p-5">
                  <div className="flex items-center gap-4">
                    <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-500/15 font-serif text-lg text-amber-200">{r.chart?.moon_sign?.sa?.[0]}</span>
                    <div>
                      <div className="font-serif text-lg text-amber-50">{r.input?.name} · {r.chart?.moon_sign?.sa}</div>
                      <div className="text-xs text-slate-400">{r.input?.dob} · {r.input?.time} · {r.input?.place} · Gem: {r.gemstone?.name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => setOpenId(openId === r.id ? null : r.id)} className="flex items-center gap-1 rounded-full border border-amber-500/30 px-3 py-1.5 text-sm text-amber-200 hover:border-amber-400/60">
                      {openId === r.id ? <>Hide <ChevronUp className="h-4 w-4" /></> : <>View <ChevronDown className="h-4 w-4" /></>}
                    </button>
                    <button onClick={() => remove(r.id)} data-testid="dashboard-delete-profile-button" className="flex h-9 w-9 items-center justify-center rounded-full border border-rose-500/30 text-rose-300 hover:bg-rose-500/10"><Trash2 className="h-4 w-4" /></button>
                  </div>
                </div>
                {openId === r.id && (
                  <div className="border-t border-amber-500/15 p-5"><ResultView result={r} /></div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="rs-card p-5">
      <Icon className="h-5 w-5 text-amber-400" />
      <div className="mt-2 text-2xl font-serif text-amber-50">{value}</div>
      <div className="text-xs uppercase tracking-wider text-amber-400/70">{label}</div>
    </div>
  );
}
