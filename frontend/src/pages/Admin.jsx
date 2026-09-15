import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { Users, Sparkles, Activity, Trash2, Shield, Gem, ScrollText } from "lucide-react";
import api, { formatApiError } from "../lib/api";
import StarField from "../components/StarField";

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [gems, setGems] = useState([]);
  const [tab, setTab] = useState("users");

  const load = () => {
    Promise.all([
      api.get("/admin/stats").then((r) => setStats(r.data)),
      api.get("/admin/users").then((r) => setUsers(r.data)),
      api.get("/admin/logs").then((r) => setLogs(r.data)),
      api.get("/gemstones").then((r) => setGems(r.data)),
    ]).catch((err) => toast.error(formatApiError(err.response?.data?.detail)));
  };
  useEffect(load, []);

  const delUser = async (id) => {
    try {
      await api.delete(`/admin/users/${id}`);
      setUsers((u) => u.filter((x) => x.id !== id));
      toast.success("User removed");
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const TABS = [
    { key: "users", label: "Users", icon: Users },
    { key: "logs", label: "Calculation Logs", icon: ScrollText },
    { key: "gems", label: "Gemstone Catalog", icon: Gem },
  ];

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={40} />
      <div className="relative z-10 mx-auto max-w-6xl px-5 py-12">
        <div className="mb-8 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-500/15"><Shield className="h-6 w-6 text-amber-300" /></span>
          <div>
            <h1 className="font-serif text-4xl text-amber-100">Admin Control Hub</h1>
            <p className="text-sm text-slate-400">Manage the Rashisense platform</p>
          </div>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard icon={Users} label="Registered Users" value={stats?.total_users ?? "—"} testid="admin-stats-total-users" />
          <StatCard icon={Sparkles} label="Saved Readings" value={stats?.total_readings ?? "—"} testid="admin-stats-total-readings" />
          <StatCard icon={Activity} label="Total Calculations" value={stats?.total_calculations ?? "—"} testid="admin-stats-total-calcs" />
        </div>

        <div className="mb-5 flex flex-wrap gap-2">
          {TABS.map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors ${tab === t.key ? "rs-gold-btn" : "border border-amber-500/25 text-slate-300 hover:text-amber-200"}`}>
              <t.icon className="h-4 w-4" /> {t.label}
            </button>
          ))}
        </div>

        {tab === "users" && (
          <div className="rs-card overflow-hidden">
            <div className="overflow-x-auto rs-scrollbar">
              <table data-testid="admin-dashboard-users-table" className="w-full text-left text-sm">
                <thead className="border-b border-amber-500/20 text-amber-400/80">
                  <tr>
                    <th className="px-5 py-3 font-medium">Name</th>
                    <th className="px-5 py-3 font-medium">Email / Username</th>
                    <th className="px-5 py-3 font-medium">Role</th>
                    <th className="px-5 py-3 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="px-5 py-3 text-slate-100">{u.name}</td>
                      <td className="px-5 py-3 text-slate-300">{u.username || u.email}</td>
                      <td className="px-5 py-3">
                        <span className={`rounded-full px-2.5 py-0.5 text-xs ${u.role === "admin" ? "bg-amber-500/20 text-amber-200" : "bg-white/10 text-slate-300"}`}>{u.role}</span>
                      </td>
                      <td className="px-5 py-3 text-right">
                        {u.role !== "admin" && (
                          <button onClick={() => delUser(u.id)} className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-rose-500/30 text-rose-300 hover:bg-rose-500/10"><Trash2 className="h-4 w-4" /></button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && <tr><td colSpan={4} className="px-5 py-8 text-center text-slate-400">No users yet.</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === "logs" && (
          <div data-testid="admin-dashboard-logs-list" className="rs-card overflow-hidden">
            <div className="overflow-x-auto rs-scrollbar">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-amber-500/20 text-amber-400/80">
                  <tr><th className="px-5 py-3 font-medium">Name</th><th className="px-5 py-3 font-medium">Place</th><th className="px-5 py-3 font-medium">Rashi</th><th className="px-5 py-3 font-medium">Gemstone</th><th className="px-5 py-3 font-medium">Time</th></tr>
                </thead>
                <tbody>
                  {logs.map((l) => (
                    <tr key={l.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="px-5 py-3 text-slate-100">{l.name}</td>
                      <td className="px-5 py-3 text-slate-300">{l.place}</td>
                      <td className="px-5 py-3 text-amber-200">{l.moon_sign}</td>
                      <td className="px-5 py-3 text-slate-300">{l.gemstone}</td>
                      <td className="px-5 py-3 text-slate-400">{new Date(l.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                  {logs.length === 0 && <tr><td colSpan={5} className="px-5 py-8 text-center text-slate-400">No calculations logged yet.</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === "gems" && (
          <div data-testid="admin-dashboard-gemstone-editor" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {gems.map((g) => (
              <div key={g.planet} className="rs-card p-5">
                <div className="flex items-center justify-between">
                  <h3 className="font-serif text-xl text-amber-50">{g.name}</h3>
                  <span className="rounded-full bg-amber-500/15 px-2.5 py-0.5 text-xs text-amber-200">{g.planet}</span>
                </div>
                <p className="mt-0.5 text-sm text-amber-300/70">{g.name_sa}</p>
                <div className="mt-3 space-y-1 text-xs text-slate-400">
                  <p>Metal: <span className="text-slate-200">{g.metal}</span></p>
                  <p>Finger: <span className="text-slate-200">{g.finger}</span></p>
                  <p>Day: <span className="text-slate-200">{g.day}</span></p>
                  <p>Mantra: <span className="text-amber-200/90">{g.mantra}</span></p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, testid }) {
  return (
    <div data-testid={testid} className="rs-card p-5">
      <Icon className="h-5 w-5 text-amber-400" />
      <div className="mt-2 font-serif text-3xl text-amber-50">{value}</div>
      <div className="text-xs uppercase tracking-wider text-amber-400/70">{label}</div>
    </div>
  );
}
