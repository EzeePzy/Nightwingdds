import React, { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { toast } from "sonner";
import { Moon, Mail, Lock, User, Shield } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { formatApiError } from "../lib/api";
import StarField from "../components/StarField";

export default function Auth() {
  const [params, setParams] = useSearchParams();
  const mode = params.get("mode") === "signup" ? "signup" : "login";
  const { login, register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);

  const setMode = (m) => setParams({ mode: m });
  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const user = mode === "signup"
        ? await register(form.name, form.email, form.password)
        : await login(form.email, form.password);
      toast.success(mode === "signup" ? "Welcome to Rashisense!" : "Welcome back!");
      nav(user.role === "admin" ? "/admin" : "/dashboard");
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail) || err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="relative flex min-h-[calc(100vh-64px)] items-center justify-center rs-cosmic px-5 py-12">
      <StarField count={50} />
      <div className="relative z-10 w-full max-w-md rs-card p-8">
        <div className="mb-6 text-center">
          <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-amber-400/40 bg-amber-500/15"><Moon className="h-6 w-6 text-amber-300" /></span>
          <h1 className="mt-4 font-serif text-3xl text-amber-100">{mode === "signup" ? "Create your account" : "Welcome back"}</h1>
          <p className="mt-1 text-sm text-slate-400">{mode === "signup" ? "Begin your cosmic journey with Rashisense" : "Sign in to view your readings"}</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          {mode === "signup" && (
            <Field icon={User} testid="auth-name-input" type="text" placeholder="Full name" value={form.name} onChange={upd("name")} required />
          )}
          <Field icon={Mail} testid="auth-email-input" type="text" placeholder="Email or username" value={form.email} onChange={upd("email")} required />
          <Field icon={Lock} testid="auth-password-input" type="password" placeholder="Password" value={form.password} onChange={upd("password")} required />
          <button type="submit" disabled={busy} data-testid="auth-submit-button" className="rs-gold-btn w-full rounded-xl py-3 text-base disabled:opacity-60">
            {busy ? "Please wait…" : mode === "signup" ? "Create Account" : "Sign In"}
          </button>
        </form>

        <div className="rs-divider my-6" />
        <p className="text-center text-sm text-slate-400">
          {mode === "signup" ? "Already have an account? " : "New to Rashisense? "}
          <button onClick={() => setMode(mode === "signup" ? "login" : "signup")} data-testid="auth-toggle-mode" className="font-medium text-amber-300 hover:underline">
            {mode === "signup" ? "Sign in" : "Create one"}
          </button>
        </p>
        <div className="mt-4 flex items-center justify-center gap-1.5 rounded-lg border border-amber-500/15 bg-white/5 px-3 py-2 text-xs text-slate-400">
          <Shield className="h-3.5 w-3.5 text-amber-400" /> Admins can sign in here with their username.
        </div>
      </div>
    </div>
  );
}

function Field({ icon: Icon, testid, ...props }) {
  return (
    <div className="relative">
      <Icon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-amber-400/70" />
      <input {...props} data-testid={testid} className="w-full rounded-xl border border-amber-500/20 bg-[#090A15]/60 py-3 pl-11 pr-4 text-slate-100 placeholder:text-slate-500 outline-none transition-colors focus:border-amber-400/60 focus:ring-2 focus:ring-amber-500/20" />
    </div>
  );
}
