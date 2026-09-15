import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Moon, Menu, X, LogOut, LayoutDashboard, Shield, Gem, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const [open, setOpen] = useState(false);

  const links = [
    { to: "/calculator", label: "Calculator", id: "nav-link-calculator" },
    { to: "/gemstones", label: "Gemstones", id: "nav-link-gemstones" },
  ];
  if (user) links.push({ to: "/dashboard", label: "Dashboard", id: "nav-link-dashboard" });
  if (user?.role === "admin") links.push({ to: "/admin", label: "Admin", id: "nav-link-admin" });

  const onLogout = () => { logout(); nav("/"); };
  const active = (to) => loc.pathname === to;

  return (
    <header className="sticky top-0 z-50 border-b border-amber-500/15 bg-[#0B0D1B]/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3.5">
        <Link to="/" data-testid="nav-logo" className="flex items-center gap-2.5 group">
          <span className="relative flex h-9 w-9 items-center justify-center rounded-full border border-amber-400/40 bg-gradient-to-br from-amber-500/20 to-purple-900/30">
            <Moon className="h-5 w-5 text-amber-300 rs-spin-slow" />
          </span>
          <span className="font-display text-xl tracking-wide rs-gold-text">Rashisense</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              data-testid={l.id}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                active(l.to) ? "text-amber-300 bg-amber-500/10" : "text-slate-300 hover:text-amber-200 hover:bg-white/5"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {user ? (
            <div className="flex items-center gap-3" data-testid="nav-user-menu">
              <span className="flex items-center gap-2 text-sm text-slate-200">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-500/20 text-amber-200 font-semibold uppercase">
                  {user.name?.[0] || user.email[0]}
                </span>
                {user.role === "admin" ? <Shield className="h-4 w-4 text-amber-400" /> : null}
              </span>
              <button onClick={onLogout} data-testid="nav-logout-button" className="flex items-center gap-1.5 rounded-full border border-amber-500/30 px-3 py-1.5 text-sm text-slate-300 hover:text-amber-200 hover:border-amber-400/60 transition-colors">
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          ) : (
            <>
              <Link to="/auth?mode=login" data-testid="nav-auth-login-button" className="rounded-full px-4 py-2 text-sm font-medium text-slate-200 hover:text-amber-200 transition-colors">Login</Link>
              <Link to="/auth?mode=signup" data-testid="nav-auth-signup-button" className="rs-gold-btn rounded-full px-5 py-2 text-sm">Get Started</Link>
            </>
          )}
        </div>

        <button className="md:hidden text-amber-200" onClick={() => setOpen(!open)} data-testid="nav-mobile-toggle">
          {open ? <X /> : <Menu />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-amber-500/15 bg-[#0B0D1B]/95 px-5 py-4 space-y-1">
          {links.map((l) => (
            <Link key={l.to} to={l.to} onClick={() => setOpen(false)} className="block rounded-lg px-3 py-2.5 text-slate-200 hover:bg-white/5">{l.label}</Link>
          ))}
          <div className="rs-divider my-3" />
          {user ? (
            <button onClick={() => { setOpen(false); onLogout(); }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-slate-200 hover:bg-white/5"><LogOut className="h-4 w-4" /> Logout</button>
          ) : (
            <div className="flex flex-col gap-2">
              <Link to="/auth?mode=login" onClick={() => setOpen(false)} className="rounded-lg px-3 py-2.5 text-slate-200 hover:bg-white/5">Login</Link>
              <Link to="/auth?mode=signup" onClick={() => setOpen(false)} className="rs-gold-btn rounded-full px-4 py-2.5 text-center">Get Started</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
