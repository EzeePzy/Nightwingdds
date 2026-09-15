import React from "react";
import { Link } from "react-router-dom";
import { XCircle } from "lucide-react";
import StarField from "../components/StarField";

export default function PaymentCancel() {
  return (
    <div className="relative flex min-h-[calc(100vh-64px)] items-center justify-center rs-cosmic px-5">
      <StarField count={40} />
      <div className="relative z-10 w-full max-w-md rs-card p-8 text-center">
        <XCircle className="mx-auto h-12 w-12 text-amber-400/70" />
        <h1 className="mt-5 font-serif text-2xl text-amber-100">Payment cancelled</h1>
        <p className="mt-2 text-sm text-slate-400">No charge was made. You can download your PDF anytime from your reading.</p>
        <Link to="/dashboard" className="rs-gold-btn mt-5 inline-flex rounded-full px-6 py-3">Back to dashboard</Link>
      </div>
    </div>
  );
}
