import React, { useState } from "react";
import { motion } from "framer-motion";
import { Sun, Moon, ArrowUpRight, Star, Sparkles, Gem, Globe, Info, Hourglass, ChevronDown, ChevronUp, Download, FileText, Tag, Briefcase, Heart, Activity, Coins, Flower2, Palette, Hash } from "lucide-react";
import { toast } from "sonner";
import KundaliChart from "./KundaliChart";
import api, { API, formatApiError } from "../lib/api";
import { useAuth } from "../context/AuthContext";

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

export default function ResultView({ result, readingId }) {
  const { chart, gemstone, reading } = result;
  const { user } = useAuth();
  const [tab, setTab] = useState("career");
  const [chartMode, setChartMode] = useState("d1");
  const [openDasha, setOpenDasha] = useState(() => (chart.dasha || []).findIndex((d) => d.is_current));
  const activeTab = TABS.find((t) => t.key === tab);
  const gemImg = GEM_IMG[gemstone.name] || DEFAULT_GEM_IMG;

  const rid = readingId || result.id;
  const [discount, setDiscount] = useState("");
  const [discountInfo, setDiscountInfo] = useState(null);
  const [payBusy, setPayBusy] = useState(false);
  const PRICE = 199;
  const finalPrice = discountInfo?.valid ? Math.round(PRICE * (1 - discountInfo.percent / 100)) : PRICE;

  const applyDiscount = async () => {
    if (!discount.trim()) return;
    try {
      const { data } = await api.post("/pdf/validate-discount", { code: discount.trim() });
      setDiscountInfo(data);
      toast[data.valid ? "success" : "error"](data.valid ? `${data.percent}% discount applied!` : "Invalid or inactive code");
    } catch (e) {
      toast.error("Could not validate code");
    }
  };

  const buyPdf = async () => {
    if (!user || !rid) {
      toast.error("Please log in and save this reading to download the PDF.");
      return;
    }
    setPayBusy(true);
    try {
      const { data } = await api.post("/pdf/checkout", {
        reading_id: rid, origin_url: window.location.origin, discount_code: discountInfo?.valid ? discount.trim() : "",
      });
      if (data.free) {
        window.location.href = `${API}/pdf/download/${data.session_id}`;
        toast.success("Unlocked! Your PDF is downloading.");
      } else {
        window.location.href = data.checkout_url;
      }
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail) || "Checkout failed");
    } finally {
      setPayBusy(false);
    }
  };

  const displayChart = chartMode === "d9"
    ? { ascendant: chart.navamsa_ascendant, planet_positions: chart.navamsa_positions }
    : chart;

  return (
    <div className="space-y-8">
      {/* Signs summary */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <Stat icon={Moon} label="Rashi (Moon)" value={chart.moon_sign.sa} testid="rashi-result-moon-sign" />
        <Stat icon={Globe} label="Western Sign" value={chart.western_sun_sign ? chart.western_sun_sign.en : chart.sun_sign.en} testid="rashi-result-western-sign" />
        <Stat icon={Sun} label="Vedic Sun" value={chart.sun_sign.sa} testid="rashi-result-sun-sign" />
        <Stat icon={ArrowUpRight} label="Ascendant" value={chart.ascendant.sa} testid="rashi-result-ascendant" />
        <Stat icon={Star} label="Nakshatra" value={`${chart.nakshatra} (${chart.pada})`} testid="rashi-result-nakshatra" />
        <Stat icon={Sparkles} label="Ruling Planet" value={chart.ruling_planet} testid="rashi-result-ruling-planet" />
      </div>

      <div className="flex items-start gap-2 rounded-xl border border-amber-500/20 bg-amber-500/5 px-4 py-3 text-sm text-slate-300">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
        <p>
          Your true Vedic <b className="text-amber-200">Rashi (Janma Rashi)</b> is your Moon sign: <b className="text-amber-100">{chart.moon_sign.sa} ({chart.moon_sign.en})</b>.
          The popular "star sign" you may know (e.g. from newspapers) is the Western Sun sign shown above{chart.western_sun_sign ? <>: <b className="text-amber-100">{chart.western_sun_sign.en}</b></> : null}. In Vedic astrology, predictions are based on the Moon rashi.
        </p>
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
            <p className="mb-4 text-xs text-slate-500">📍 {chart.birth_location.matched} · {chart.birth_location.tz}{typeof chart.ayanamsa === "number" ? ` · Ayanamsa ${chart.ayanamsa}°` : ""}</p>
          )}
          {chart.navamsa_positions && (
            <div className="mb-4 flex gap-2">
              <button onClick={() => setChartMode("d1")} data-testid="chart-toggle-d1" className={`rounded-full px-4 py-1.5 text-xs font-medium transition-colors ${chartMode === "d1" ? "rs-gold-btn" : "border border-amber-500/25 text-slate-300 hover:text-amber-200"}`}>Rashi (D1)</button>
              <button onClick={() => setChartMode("d9")} data-testid="chart-toggle-d9" className={`rounded-full px-4 py-1.5 text-xs font-medium transition-colors ${chartMode === "d9" ? "rs-gold-btn" : "border border-amber-500/25 text-slate-300 hover:text-amber-200"}`}>Navamsa (D9)</button>
            </div>
          )}
          <div data-testid={chartMode === "d9" ? "navamsa-chart" : "rashi-chart"}>
            <KundaliChart chart={displayChart} />
          </div>
          <p className="mt-2 text-center text-xs text-slate-500">{chartMode === "d9" ? "Navamsa (D9) — depth of destiny, marriage & dharma" : "Rashi chart (D1) — the main birth chart"}</p>
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
            {Object.entries(chart.planet_positions).map(([p, s]) => (
              <div key={p} className="rounded-lg border border-amber-500/15 bg-white/5 px-2 py-1.5">
                <span className="text-amber-300">{p}</span>
                <span className="block text-slate-400">{chartMode === "d9" ? chart.navamsa_positions?.[p] : s}{chartMode === "d1" && typeof chart.planet_degrees?.[p] === "number" ? ` ${chart.planet_degrees[p]}°` : ""}</span>
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

      {/* Vimshottari Dasha timeline */}
      {chart.dasha && chart.dasha.length > 0 && (
        <div data-testid="dasha-timeline" className="rs-card p-6 sm:p-8">
          <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
            <h3 className="flex items-center gap-2 font-serif text-2xl text-amber-100"><Hourglass className="h-5 w-5 text-amber-400" /> Vimshottari Dasha</h3>
            {chart.current_dasha && (
              <span data-testid="dasha-current" className="rounded-full border border-amber-400/50 bg-amber-500/15 px-3 py-1 text-xs text-amber-200">
                Running now: <b>{chart.current_dasha.planet} Mahadasha</b> ({chart.current_dasha.start} → {chart.current_dasha.end})
              </span>
            )}
          </div>
          <p className="mb-5 text-sm text-slate-400">Planetary periods calculated from your Moon's nakshatra ({chart.nakshatra}) — the 120-year cycle that times life's chapters. Tap a period to see its Antardasha (sub-periods).</p>
          <div className="space-y-2">
            {chart.dasha.map((d, i) => (
              <div key={i} className={`rounded-xl border ${d.is_current ? "border-amber-400/60 bg-amber-500/10" : "border-amber-500/15 bg-white/5"}`}>
                <button onClick={() => setOpenDasha(openDasha === i ? -1 : i)} data-testid={`dasha-maha-${d.planet.toLowerCase()}`} className="flex w-full items-center justify-between px-4 py-3 text-left">
                  <div className="flex items-center gap-3">
                    <span className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold ${d.is_current ? "bg-amber-500/30 text-amber-100" : "bg-white/10 text-amber-300"}`}>{d.planet[0]}</span>
                    <div>
                      <div className="text-sm text-slate-100">{d.planet} Mahadasha {d.is_current && <span className="ml-1 rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] text-amber-200">running</span>}</div>
                      <div className="text-[11px] text-slate-400">{d.start} → {d.end} · {d.years} yrs</div>
                    </div>
                  </div>
                  {d.antardashas && d.antardashas.length > 0 && (openDasha === i ? <ChevronUp className="h-4 w-4 text-amber-300" /> : <ChevronDown className="h-4 w-4 text-slate-400" />)}
                </button>
                {openDasha === i && d.antardashas && (
                  <div className="grid grid-cols-2 gap-2 border-t border-amber-500/15 p-3 sm:grid-cols-3 lg:grid-cols-4">
                    {d.antardashas.map((a, j) => (
                      <div key={j} data-testid={a.is_current ? "antardasha-current" : undefined} className={`rounded-lg border px-2.5 py-2 text-xs ${a.is_current ? "border-amber-400/60 bg-amber-500/15" : "border-amber-500/10 bg-[#090A15]/50"}`}>
                        <div className="text-slate-100">{d.planet[0]}–{a.planet}{a.is_current && " ●"}</div>
                        <div className="text-[10px] text-slate-400">{a.start} → {a.end}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Paid PDF report */}
      <div data-testid="pdf-purchase-card" className="rs-card overflow-hidden p-6 sm:p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-4">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-500/15"><FileText className="h-6 w-6 text-amber-300" /></span>
            <div>
              <h3 className="font-serif text-2xl text-amber-100">Download Full Kundali PDF</h3>
              <p className="mt-1 max-w-md text-sm text-slate-400">A professional report with your Rashi &amp; Navamsa charts, all planetary positions, the complete Vimshottari Dasha, gemstone remedy and personalised reading.</p>
            </div>
          </div>
          <div className="shrink-0 text-center md:text-right">
            <div className="font-serif text-3xl rs-gold-text">
              ₹{finalPrice}
              {discountInfo?.valid && <span className="ml-2 align-middle text-base text-slate-500 line-through">₹{PRICE}</span>}
            </div>
            <div className="mt-3 flex items-center gap-2">
              <div className="relative">
                <Tag className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-amber-400/70" />
                <input data-testid="discount-code-input" value={discount} onChange={(e) => { setDiscount(e.target.value); setDiscountInfo(null); }} placeholder="Discount code" className="w-36 rounded-lg border border-amber-500/20 bg-[#090A15]/60 py-2 pl-8 pr-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-amber-400/60" />
              </div>
              <button onClick={applyDiscount} data-testid="apply-discount-button" className="rounded-lg border border-amber-500/30 px-3 py-2 text-sm text-amber-200 hover:border-amber-400/60">Apply</button>
            </div>
            <button onClick={buyPdf} disabled={payBusy} data-testid="buy-pdf-button" className="rs-gold-btn mt-3 flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm disabled:opacity-60 md:w-auto">
              {payBusy ? "Please wait…" : <><Download className="h-4 w-4" /> {finalPrice === 0 ? "Get PDF Free" : `Pay ₹${finalPrice} & Download`}</>}
            </button>
            {(!user || !rid) && <p className="mt-2 text-xs text-slate-500">Log in &amp; save this reading to buy the PDF.</p>}
          </div>
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
