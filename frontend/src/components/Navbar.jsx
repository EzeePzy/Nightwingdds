import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Moon, Sun, Menu, X, LogOut, Shield, MoreVertical, Globe, Check, LayoutDashboard } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { useI18n, LANGS } from "../i18n";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { mode, toggle } = useTheme();
  const { t, lang, setLang } = useI18n();
  const nav = useNavigate();
  const loc = useLocation();
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const onDoc = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenu(false); };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const links = [
    { to: "/calculator", label: t("nav.calculator"), id: "nav-link-calculator" },
    { to: "/horoscope", label: t("nav.horoscope"), id: "nav-link-horoscope" },
    { to: "/matching", label: t("nav.matching"), id: "nav-link-matching" },
    { to: "/gemstones", label: t("nav.gemstones"), id: "nav-link-gemstones" },
  ];
  if (user) links.push({ to: "/dashboard", label: t("nav.dashboard"), id: "nav-link-dashboard" });
  if (user?.role === "admin") links.push({ to: "/admin", label: t("nav.admin"), id: "nav-link-admin" });

  const onLogout = () => { logout(); setMenu(false); nav("/"); };
  const active = (to) => loc.pathname === to;
  const isLight = mode === "light";

  return (
    <header className={`sticky top-0 z-50 border-b backdrop-blur-xl ${isLight ? "border-amber-600/20 bg-white/70" : "border-amber-500/15 bg-[#0B0D1B]/80"}`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3.5">
        <Link to="/" data-testid="nav-logo" className="flex items-center gap-2.5 rs-tap">
          <span className="relative flex h-9 w-9 items-center justify-center rounded-full border border-amber-400/40 bg-gradient-to-br from-amber-500/20 to-purple-900/30">
            <Moon className="h-5 w-5 text-amber-400 rs-spin-slow" />
          </span>
          <span className="font-display text-xl tracking-wide rs-gold-text">Rashify</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link key={l.to} to={l.to} data-testid={l.id}
              className={`rs-tap rounded-full px-4 py-2 text-sm font-medium transition-colors ${active(l.to) ? "text-amber-500 bg-amber-500/10" : isLight ? "text-slate-700 hover:text-amber-600 hover:bg-black/5" : "text-slate-300 hover:text-amber-200 hover:bg-white/5"}`}>
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {!user && (
            <Link to="/auth?mode=signup" data-testid="nav-auth-signup-button" className="rs-gold-btn rs-tap hidden rounded-full px-5 py-2 text-sm sm:inline-flex">{t("nav.getStarted")}</Link>
          )}

          {/* Language selector */}
          <div className="relative" data-testid="language-selector-wrap">
            <select value={lang} onChange={(e) => setLang(e.target.value)} data-testid="language-selector"
              aria-label={t("menu.language")}
              className={`appearance-none rounded-full border px-3 py-1.5 pr-7 text-sm outline-none ${isLight ? "border-amber-600/30 bg-white text-slate-700" : "border-amber-500/30 bg-[#13102B] text-slate-200"}`}>
              {LANGS.map((l) => <option key={l.code} value={l.code} className="bg-[#13102B]">{l.label}</option>)}
            </select>
            <Globe className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-amber-400" />
          </div>

          {/* Three-dot menu */}
          <div className="relative" ref={menuRef}>
            <button onClick={() => setMenu(!menu)} data-testid="three-dot-menu-button"
              className={`rs-tap flex h-9 w-9 items-center justify-center rounded-full border ${isLight ? "border-amber-600/30 text-slate-700 hover:bg-black/5" : "border-amber-500/30 text-amber-200 hover:bg-white/5"}`}>
              <MoreVertical className="h-5 w-5" />
            </button>
            {menu && (
              <div data-testid="three-dot-menu" className="absolute right-0 mt-2 w-56 overflow-hidden rounded-xl border border-amber-500/25 bg-[#13102B] py-1 shadow-2xl">
                <button onClick={() => { toggle(); }} data-testid="theme-toggle-button" className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm text-slate-200 hover:bg-white/5">
                  {isLight ? <Moon className="h-4 w-4 text-amber-300" /> : <Sun className="h-4 w-4 text-amber-300" />} {t("menu.theme")}
                </button>
                <div className="my-1 border-t border-white/10" />
                <div className="px-4 py-1.5 text-[10px] uppercase tracking-wider text-amber-400/70">{t("menu.language")}</div>
                {LANGS.map((l) => (
                  <button key={l.code} onClick={() => { setLang(l.code); }} className="flex w-full items-center justify-between px-4 py-2 text-left text-sm text-slate-200 hover:bg-white/5">
                    {l.label} {lang === l.code && <Check className="h-4 w-4 text-emerald-400" />}
                  </button>
                ))}
                <div className="my-1 border-t border-white/10" />
                {user ? (
                  <>
                    <Link to="/dashboard" onClick={() => setMenu(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-200 hover:bg-white/5"><LayoutDashboard className="h-4 w-4 text-amber-300" /> {t("nav.dashboard")}</Link>
                    {user.role === "admin" && <Link to="/admin" onClick={() => setMenu(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-200 hover:bg-white/5"><Shield className="h-4 w-4 text-amber-300" /> {t("nav.admin")}</Link>}
                    <button onClick={onLogout} data-testid="nav-logout-button" className="flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm text-rose-300 hover:bg-white/5"><LogOut className="h-4 w-4" /> {t("nav.logout")}</button>
                  </>
                ) : (
                  <Link to="/auth?mode=login" onClick={() => setMenu(false)} data-testid="nav-auth-login-button" className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-200 hover:bg-white/5"><LogOut className="h-4 w-4 text-amber-300" /> {t("nav.login")}</Link>
                )}
              </div>
            )}
          </div>

          <button className={`md:hidden ${isLight ? "text-slate-700" : "text-amber-200"}`} onClick={() => setOpen(!open)} data-testid="nav-mobile-toggle">
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {open && (
        <div className={`md:hidden border-t px-5 py-4 space-y-1 ${isLight ? "border-amber-600/20 bg-white/95" : "border-amber-500/15 bg-[#0B0D1B]/95"}`}>
          {links.map((l) => (
            <Link key={l.to} to={l.to} onClick={() => setOpen(false)} className={`block rounded-lg px-3 py-2.5 ${isLight ? "text-slate-700 hover:bg-black/5" : "text-slate-200 hover:bg-white/5"}`}>{l.label}</Link>
          ))}
          {!user && <Link to="/auth?mode=signup" onClick={() => setOpen(false)} className="rs-gold-btn mt-2 block rounded-full px-4 py-2.5 text-center">{t("nav.getStarted")}</Link>}
        </div>
      )}
    </header>
  );
}
