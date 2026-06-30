"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getT, type Lang } from "@/lib/i18n";
import { getLang, setLang, getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { LangSwitcher } from "@/components/LangSwitcher";

export default function BillingPage() {
  const [lang, setLangState] = useState<Lang>("ru");
  const [status, setStatus] = useState<{ is_premium: boolean; subscription_expires_at: string | null } | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const t = getT(lang);

  useEffect(() => {
    if (!getToken()) { router.push("/"); return; }
    setLangState(getLang() as Lang);
    api.billing.status().then(setStatus).catch(() => router.push("/"));
  }, [router]);

  const handleLangChange = (l: Lang) => { setLang(l); setLangState(l); };

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const origin = window.location.origin;
      const result = await api.billing.createInvoice(
        `${origin}/billing?success=1`,
        `${process.env.NEXT_PUBLIC_API_URL}/billing/webhook`,
      );
      window.location.href = result.invoice_url;
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const expiresDate = status?.subscription_expires_at
    ? new Date(status.subscription_expires_at).toLocaleDateString(lang === "en" ? "en-US" : "ru-RU", {
        day: "2-digit", month: "long", year: "numeric",
      })
    : null;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="sticky top-0 z-10 bg-gray-950/90 backdrop-blur border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="font-bold text-gold text-xl">RealEstate AI</Link>
          <nav className="hidden md:flex items-center gap-4 text-sm text-gray-400">
            <Link href="/dashboard" className="hover:text-white">{t.nav.dashboard}</Link>
            <Link href="/history" className="hover:text-white">{t.nav.history}</Link>
            <Link href="/billing" className="text-white font-medium">{t.nav.billing}</Link>
          </nav>
          <LangSwitcher current={lang} onChange={handleLangChange} />
        </div>
      </header>

      <main className="max-w-md mx-auto px-4 py-12">
        <h1 className="text-2xl font-bold mb-8">{t.billing.title}</h1>

        {status && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            {status.is_premium ? (
              <div>
                <div className="flex items-center gap-2 text-gold font-semibold">
                  <span>⭐</span>
                  <span>Premium</span>
                </div>
                <p className="text-gray-400 text-sm mt-2">
                  {t.billing.active}: <span className="text-white">{expiresDate}</span>
                </p>
              </div>
            ) : (
              <div>
                <p className="text-gray-400 text-sm mb-5">{t.billing.inactive}</p>
                <button
                  onClick={handleSubscribe}
                  disabled={loading}
                  className="w-full py-3 rounded-lg bg-gold text-black font-semibold hover:bg-gold-light disabled:opacity-50 transition-colors"
                >
                  {loading ? "..." : t.billing.subscribe}
                </button>
                <p className="text-xs text-gray-500 mt-3 text-center">
                  Оплата через Monobank · Безопасно
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
