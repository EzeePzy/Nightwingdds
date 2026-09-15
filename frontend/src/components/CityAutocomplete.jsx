import React, { useEffect, useRef, useState } from "react";
import { MapPin } from "lucide-react";
import api from "../lib/api";

export default function CityAutocomplete({ value, onChange, placeholder, testid, className }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const boxRef = useRef(null);
  const timer = useRef(null);

  useEffect(() => {
    const onDoc = (e) => { if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const handle = (v) => {
    onChange(v);
    clearTimeout(timer.current);
    if (v.trim().length < 2) { setSuggestions([]); setOpen(false); return; }
    timer.current = setTimeout(async () => {
      try {
        const { data } = await api.get(`/cities?q=${encodeURIComponent(v.trim())}`);
        setSuggestions(data.results || []);
        setOpen((data.results || []).length > 0);
        setActive(-1);
      } catch (e) { /* ignore */ }
    }, 220);
  };

  const pick = (s) => { onChange(s); setOpen(false); setSuggestions([]); };

  const onKey = (e) => {
    if (!open) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => Math.min(a + 1, suggestions.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === "Enter" && active >= 0) { e.preventDefault(); pick(suggestions[active]); }
    else if (e.key === "Escape") setOpen(false);
  };

  return (
    <div className="relative" ref={boxRef}>
      <MapPin className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-amber-400/70" />
      <input
        data-testid={testid}
        value={value}
        onChange={(e) => handle(e.target.value)}
        onFocus={() => suggestions.length && setOpen(true)}
        onKeyDown={onKey}
        placeholder={placeholder}
        autoComplete="off"
        className={className}
        style={{ paddingLeft: "2.75rem" }}
      />
      {open && (
        <ul data-testid="city-suggestions" className="absolute z-30 mt-1 max-h-60 w-full overflow-auto rounded-xl border border-amber-500/25 bg-[#13102B] py-1 shadow-2xl rs-scrollbar">
          {suggestions.map((s, i) => (
            <li key={s}>
              <button type="button" onMouseDown={(e) => { e.preventDefault(); pick(s); }}
                data-testid={`city-suggestion-${i}`}
                className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm ${i === active ? "bg-amber-500/20 text-amber-100" : "text-slate-200 hover:bg-white/5"}`}>
                <MapPin className="h-3.5 w-3.5 text-amber-400/70" /> {s}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
