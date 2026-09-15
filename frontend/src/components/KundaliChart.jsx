import React from "react";

// North Indian style Kundali (diamond) chart with planetary placements
const RASHI_NUM = {
  Mesha: 1, Vrishabha: 2, Mithuna: 3, Karka: 4, Simha: 5, Kanya: 6,
  Tula: 7, Vrishchika: 8, Dhanu: 9, Makara: 10, Kumbha: 11, Meena: 12,
};
const ABBR = {
  Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju",
  Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke",
};

export default function KundaliChart({ chart }) {
  const ascNum = RASHI_NUM[chart.ascendant.sa] || 1;
  // 12 houses; house i holds sign (ascNum + i - 1)
  const houses = Array.from({ length: 12 }, (_, i) => ((ascNum - 1 + i) % 12) + 1);
  const planetsBySign = {};
  Object.entries(chart.planet_positions).forEach(([p, signSa]) => {
    const n = RASHI_NUM[signSa];
    if (!planetsBySign[n]) planetsBySign[n] = [];
    planetsBySign[n].push(ABBR[p] || p.slice(0, 2));
  });

  // Positions (percentage) for the 12 triangular houses in a North-Indian chart
  const pos = [
    { x: 50, y: 25 }, { x: 25, y: 12 }, { x: 12, y: 25 }, { x: 25, y: 50 },
    { x: 12, y: 75 }, { x: 25, y: 88 }, { x: 50, y: 75 }, { x: 75, y: 88 },
    { x: 88, y: 75 }, { x: 75, y: 50 }, { x: 88, y: 25 }, { x: 75, y: 12 },
  ];

  return (
    <div data-testid="kundali-chart-container" className="relative mx-auto aspect-square w-full max-w-sm rounded-xl border-2 border-amber-500/40 bg-[#090A15] p-1 shadow-[0_0_30px_rgba(226,158,56,0.1)]">
      <svg viewBox="0 0 100 100" className="h-full w-full">
        <rect x="2" y="2" width="96" height="96" fill="none" stroke="rgba(226,158,56,0.5)" strokeWidth="0.6" />
        <line x1="2" y1="2" x2="98" y2="98" stroke="rgba(226,158,56,0.35)" strokeWidth="0.5" />
        <line x1="98" y1="2" x2="2" y2="98" stroke="rgba(226,158,56,0.35)" strokeWidth="0.5" />
        <polygon points="50,2 98,50 50,98 2,50" fill="none" stroke="rgba(226,158,56,0.35)" strokeWidth="0.5" />
      </svg>
      {houses.map((sign, i) => (
        <div key={i} className="absolute -translate-x-1/2 -translate-y-1/2 text-center" style={{ left: `${pos[i].x}%`, top: `${pos[i].y}%` }}>
          <div className="text-[9px] font-semibold text-amber-500/70">{sign}</div>
          <div className="text-[10px] font-bold leading-tight text-amber-100">{(planetsBySign[sign] || []).join(" ")}</div>
        </div>
      ))}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-amber-500/10 px-2 py-0.5 text-[8px] font-display uppercase tracking-widest text-amber-400/80">Lagna</div>
    </div>
  );
}
