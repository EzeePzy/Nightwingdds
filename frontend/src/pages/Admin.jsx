import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { Users, Sparkles, Activity, Trash2, Shield, Gem, ScrollText, Ticket, Plus, Power, Settings, Save } from "lucide-react";
import api, { formatApiError } from "../lib/api";
import StarField from "../components/StarField";

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [gems, setGems] = useState([]);
  const [discounts, setDiscounts] = useState([]);
  const [settings, setSettings] = useState(null);
  const [newCode, setNewCode] = useState("");
  const [newPct, setNewPct] = useState(10);
  const [tab, setTab] = useState("users");

  const load = () => {
    Promise.all([
      api.get("/admin/stats").then((r) => setStats(r.data)),
      api.get("/admin/users").then((r) => setUsers(r.data)),
      api.get("/admin/logs").then((r) => setLogs(r.data)),
      api.get("/gemstones").then((r) => setGems(r.data)),
      api.get("/admin/discounts").then((r) => setDiscounts(r.data)),
      api.get("/settings").then((r) => setSettings(r.data)),
    ]).catch((err) => toast.error(formatApiError(err.response?.data?.detail)));
  };
  useEffect(load, []);

  const saveSettings = async () => {
    try {
      const { data } = await api.put("/admin/settings", settings);
      setSettings(data);
      toast.success("Site settings saved");
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const delUser = async (id) => {
    try {
      await api.delete(`/admin/users/${id}`);
      setUsers((u) => u.filter((x) => x.id !== id));
      toast.success("User removed");
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const createDiscount = async () => {
    if (!newCode.trim()) { toast.error("Enter a code"); return; }
    try {
      const { data } = await api.post("/admin/discounts", { code: newCode.trim(), percent: Number(newPct) });
      setDiscounts((d) => [data, ...d]);
      setNewCode("");
      toast.success(`Code ${data.code} created`);
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const toggleDiscount = async (id) => {
    try {
      const { data } = await api.patch(`/admin/discounts/${id}`);
      setDiscounts((d) => d.map((x) => (x.id === id ? { ...x, active: data.active } : x)));
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const deleteDiscount = async (id) => {
    try {
      await api.delete(`/admin/discounts/${id}`);
      setDiscounts((d) => d.filter((x) => x.id !== id));
      toast.success("Code deleted");
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail));
    }
  };

  const TABS = [
    { key: "users", label: "Users", icon: Users },
    { key: "logs", label: "Calculation Logs", icon: ScrollText },
    { key: "gems", label: "Gemstone Catalog", icon: Gem },
    { key: "discounts", label: "Discount Codes", icon: Ticket },
    { key: "settings", label: "Site Settings", icon: Settings },
  ];

  return (
    <div className="relative min-h-screen rs-cosmic">
      <StarField count={40} />
      <div className="relative z-10 mx-auto max-w-6xl px-5 py-12">
        <div className="mb-8 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-500/15"><Shield className="h-6 w-6 text-amber-300" /></span>
          <div>
            <h1 className="font-serif text-4xl text-amber-100">Admin Control Hub</h1>
            <p className="text-sm text-slate-400">Manage the Rashify platform</p>
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

        {tab === "discounts" && (
          <div data-testid="admin-discounts-panel" className="space-y-5">
            <div className="rs-card p-5">
              <h3 className="mb-3 font-serif text-lg text-amber-100">Create a discount code</h3>
              <div className="flex flex-wrap items-end gap-3">
                <div>
                  <label className="mb-1 block text-xs uppercase tracking-wider text-amber-400/80">Code</label>
                  <input data-testid="discount-code-new" value={newCode} onChange={(e) => setNewCode(e.target.value.toUpperCase())} placeholder="DIWALI50" className="rounded-lg border border-amber-500/20 bg-[#090A15]/60 px-3 py-2 text-sm text-slate-100 uppercase placeholder:text-slate-500 outline-none focus:border-amber-400/60" />
                </div>
                <div>
                  <label className="mb-1 block text-xs uppercase tracking-wider text-amber-400/80">Discount %</label>
                  <input data-testid="discount-percent-new" type="number" min={0} max={100} value={newPct} onChange={(e) => setNewPct(e.target.value)} className="w-24 rounded-lg border border-amber-500/20 bg-[#090A15]/60 px-3 py-2 text-sm text-slate-100 outline-none focus:border-amber-400/60" />
                </div>
                <button onClick={createDiscount} data-testid="discount-create-button" className="rs-gold-btn flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm"><Plus className="h-4 w-4" /> Create</button>
              </div>
              <p className="mt-2 text-xs text-slate-500">Set 100% to give a free PDF. Toggle a code off anytime to disable it instantly.</p>
            </div>

            <div className="rs-card overflow-hidden">
              <div className="overflow-x-auto rs-scrollbar">
                <table data-testid="admin-discounts-table" className="w-full text-left text-sm">
                  <thead className="border-b border-amber-500/20 text-amber-400/80">
                    <tr><th className="px-5 py-3 font-medium">Code</th><th className="px-5 py-3 font-medium">Discount</th><th className="px-5 py-3 font-medium">Status</th><th className="px-5 py-3 font-medium text-right">Actions</th></tr>
                  </thead>
                  <tbody>
                    {discounts.map((d) => (
                      <tr key={d.id} className="border-b border-white/5 hover:bg-white/5">
                        <td className="px-5 py-3 font-mono text-amber-100">{d.code}</td>
                        <td className="px-5 py-3 text-slate-300">{d.percent}% off</td>
                        <td className="px-5 py-3">
                          <span className={`rounded-full px-2.5 py-0.5 text-xs ${d.active ? "bg-emerald-500/20 text-emerald-300" : "bg-white/10 text-slate-400"}`}>{d.active ? "Active" : "Off"}</span>
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex items-center justify-end gap-2">
                            <button onClick={() => toggleDiscount(d.id)} data-testid={`discount-toggle-${d.code}`} title="Toggle on/off" className={`flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs ${d.active ? "border-emerald-500/40 text-emerald-300" : "border-slate-500/40 text-slate-400"} hover:bg-white/5`}>
                              <Power className="h-3.5 w-3.5" /> {d.active ? "On" : "Off"}
                            </button>
                            <button onClick={() => deleteDiscount(d.id)} data-testid={`discount-delete-${d.code}`} className="flex h-8 w-8 items-center justify-center rounded-full border border-rose-500/30 text-rose-300 hover:bg-rose-500/10"><Trash2 className="h-4 w-4" /></button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {discounts.length === 0 && <tr><td colSpan={4} className="px-5 py-8 text-center text-slate-400">No discount codes yet.</td></tr>}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {tab === "settings" && settings && (
          <div data-testid="admin-settings-panel" className="rs-card max-w-2xl p-6">
            <h3 className="mb-4 font-serif text-xl text-amber-100">Edit website content</h3>
            <div className="space-y-4">
              {[
                ["brand_name", "Brand Name"],
                ["hero_title_gold", "Hero Title (gold line)"],
                ["hero_title_plain", "Hero Title (plain line)"],
                ["hero_subtitle", "Hero Subtitle"],
                ["pdf_price_inr", "PDF Price (₹)"],
              ].map(([key, label]) => (
                <div key={key}>
                  <label className="mb-1 block text-xs uppercase tracking-wider text-amber-400/80">{label}</label>
                  {key === "hero_subtitle" ? (
                    <textarea data-testid={`settings-${key}`} value={settings[key] || ""} onChange={(e) => setSettings({ ...settings, [key]: e.target.value })} rows={3} className="w-full resize-none rounded-xl border border-amber-500/20 bg-[#090A15]/60 px-4 py-3 text-sm text-slate-100 outline-none focus:border-amber-400/60" />
                  ) : (
                    <input data-testid={`settings-${key}`} value={settings[key] || ""} onChange={(e) => setSettings({ ...settings, [key]: key === "pdf_price_inr" ? Number(e.target.value) : e.target.value })} type={key === "pdf_price_inr" ? "number" : "text"} className="w-full rounded-xl border border-amber-500/20 bg-[#090A15]/60 px-4 py-3 text-sm text-slate-100 outline-none focus:border-amber-400/60" />
                  )}
                </div>
              ))}
              <button onClick={saveSettings} data-testid="settings-save-button" className="rs-gold-btn flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm"><Save className="h-4 w-4" /> Save Settings</button>
            </div>
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
