import React, { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, Download, Loader2, XCircle } from "lucide-react";
import api, { API } from "../lib/api";
import StarField from "../components/StarField";

export default function PaymentSuccess() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const [state, setState] = useState("checking"); // checking | paid | failed
  const triggered = useRef(false);

  useEffect(() => {
    if (!sessionId) { setState("failed"); return; }
    let attempts = 0;
    let timer;
    const poll = async () => {
      attempts += 1;
      try {
        const { data } = await api.get(`/payments/status/${sessionId}`);
        if (data.payment_status === "paid") {
          setState("paid");
          if (!triggered.current) {
            triggered.current = true;
            window.location.assign(`${API}/pdf/download/${sessionId}`);
          }
          return;
        }
        if (["failed", "expired"].includes(data.payment_status)) { setState("failed"); return; }
      } catch (e) { /* keep polling */ }
      if (attempts >= 20) { setState("failed"); return; }
      timer = setTimeout(poll, 2000);
    };
    poll();
    return () => clearTimeout(timer);
  }, [sessionId]);

  return (
    <div className="relative flex min-h-[calc(100vh-64px)] items-center justify-center rs-cosmic px-5">
      <StarField count={50} />
      <div className="relative z-10 w-full max-w-md rs-card p-8 text-center">
        {state === "checking" && (
          <>
            <Loader2 className="mx-auto h-12 w-12 animate-spin text-amber-400" />
            <h1 className="mt-5 font-serif text-2xl text-amber-100">Confirming your payment…</h1>
            <p className="mt-2 text-sm text-slate-400">Please wait a moment while we verify with Stripe.</p>
          </>
        )}
        {state === "paid" && (
          <>
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-400" />
            <h1 className="mt-5 font-serif text-2xl text-amber-100">Payment successful!</h1>
            <p className="mt-2 text-sm text-slate-400">Your Kundali PDF download should start automatically.</p>
            <a href={`${API}/pdf/download/${sessionId}`} data-testid="manual-download-link" className="rs-gold-btn mt-5 inline-flex items-center gap-2 rounded-full px-6 py-3">
              <Download className="h-4 w-4" /> Download again
            </a>
            <div className="mt-4"><Link to="/dashboard" className="text-sm text-amber-300 hover:underline">Go to dashboard</Link></div>
          </>
        )}
        {state === "failed" && (
          <>
            <XCircle className="mx-auto h-12 w-12 text-rose-400" />
            <h1 className="mt-5 font-serif text-2xl text-amber-100">We couldn't confirm the payment</h1>
            <p className="mt-2 text-sm text-slate-400">If you were charged, contact support. You can try again from your reading.</p>
            <Link to="/dashboard" className="rs-gold-btn mt-5 inline-flex rounded-full px-6 py-3">Back to dashboard</Link>
          </>
        )}
      </div>
    </div>
  );
}
