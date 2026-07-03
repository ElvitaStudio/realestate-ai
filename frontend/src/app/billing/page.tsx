"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getT, type Lang } from "@/lib/i18n";
import { getLang, setLang, getToken } from "@/lib/auth";
import { api, type User, type SubscriptionStatus } from "@/lib/api";
import { LangSwitcher } from "@/components/LangSwitcher";

function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000);
    return () => clearTimeout(t);
  }, [onClose]);
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-gray-800 border border-gray-600 text-white text-sm px-5 py-3 rounded-xl shadow-xl">
      {message}
    </div>
  );
}

function CardModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 max-w-sm w-full shadow-2xl">
        <div className="text-2xl mb-3">🔧</div>
        <h2 className="text-lg font-bold text-white mb-2">В разработке</h2>
        <p className="text-gray-400 text-sm mb-6">
          Оплата картой скоро будет доступна. Используйте Telegram Stars.
        </p>
        <button
          onClick={onClose}
          className="w-full py-3 rounded-xl bg-gray-700 text-white font-semibold hover:bg-gray-600 transition-colors"
        >
          Понятно
        </button>
      </div>
    </div>
  );
}

export default function BillingPage() {
  const [lang, setLangState] = useState<Lang>("ru");
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [showCardModal, setShowCardModal] = useState(false);
  const router = useRouter();
  const t = getT(lang);

  useEffect(() => {
    if (!getToken()) { router.push("/"); return; }
    setLangState(getLang() as Lang);
    Promise.all([api.auth.me(), api.stars.subscriptionStatus()])
      .then(([u, s]) => { setUser(u); setStatus(s); })
      .catch(() => { router.push("/"); });
  }, [router]);

  const handleLangChange = (l: Lang) => { setLang(l); setLangState(l); };

  const handleStarsPay = async () => {
    if (!user) return;
    setLoading(true);
    try {
      await api.stars.createInvoice(user.id);
      setToast("⭐ Счёт отправлен в ваш Telegram!");
    } catch {
      setToast("Ошибка. Попробуйте ещё раз.");
    } finally {
      setLoading(false);
    }
  };

  const expiresFormatted = status?.expires_at
    ? new Date(status.expires_at).toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
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

      <main className="max-w-md mx-auto px-4 py-12 space-y-6">
        <h1 className="text-2xl font-bold">{t.billing.title}</h1>

        {status && (
          <>
            {/* Current status block */}
            {status.is_premium ? (
              <div className="bg-green-950/40 border border-green-700 rounded-xl p-4 flex items-center gap-3">
                <span className="text-green-400 text-xl">✅</span>
                <div>
                  <p className="text-green-300 font-semibold text-sm">Premium активен</p>
                  <p className="text-gray-400 text-xs mt-0.5">
                    до {expiresFormatted} · осталось {status.days_left} дн.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 flex items-center gap-3">
                <span className="text-gray-400 text-xl">🆓</span>
                <div>
                  <p className="text-gray-300 font-semibold text-sm">Бесплатный тариф</p>
                  {user && (
                    <p className="text-gray-500 text-xs mt-0.5">
                      Использовано {user.generations_used}/{user.generations_limit} генераций
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Telegram Stars payment */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-gold text-lg">⭐</span>
                <h2 className="text-white font-semibold">Оплата через Telegram Stars</h2>
              </div>
              <p className="text-gray-400 text-sm mb-5">750 Stars ≈ $15 / месяц</p>
              <button
                onClick={handleStarsPay}
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gold text-black font-semibold hover:bg-gold-light disabled:opacity-50 transition-colors"
              >
                {loading ? "Отправка..." : "⭐ Оплатить через Telegram"}
              </button>
            </div>

            {/* Card payment stub */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-gray-500 text-lg">💳</span>
                <h2 className="text-gray-500 font-semibold">Оплата картой</h2>
              </div>
              <p className="text-gray-600 text-sm mb-5">Скоро будет доступно</p>
              <button
                onClick={() => setShowCardModal(true)}
                className="w-full py-3 rounded-xl bg-gray-700 text-gray-500 font-semibold cursor-pointer transition-colors hover:bg-gray-600"
              >
                💳 Оплатить картой
              </button>
            </div>
          </>
        )}
      </main>

      {showCardModal && <CardModal onClose={() => setShowCardModal(false)} />}
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}
