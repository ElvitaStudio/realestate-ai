"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getT, type Lang } from "@/lib/i18n";
import { getLang, setLang, getToken, clearToken } from "@/lib/auth";
import { api, type User, type GenerationResult, type SubscriptionStatus } from "@/lib/api";
import { TOOLS, type ToolConfig } from "@/lib/toolsConfig";
import { LangSwitcher } from "@/components/LangSwitcher";
import { UsageCounter } from "@/components/UsageCounter";
import { ToolCard } from "@/components/ToolCard";
import { Sidebar } from "@/components/Sidebar";
import { UpgradeModal } from "@/components/UpgradeModal";
import { SubscriptionExpiredModal } from "@/components/SubscriptionExpiredModal";

const DISMISS_KEY = "sub_modal_dismissed_at";
const DISMISS_TTL_MS = 24 * 60 * 60 * 1000;

function shouldShowModal(daysLeft: number): boolean {
  if (daysLeft <= 0) return true;
  if (daysLeft > 3) return false;
  const raw = typeof window !== "undefined" ? localStorage.getItem(DISMISS_KEY) : null;
  if (!raw) return true;
  return Date.now() - Number(raw) > DISMISS_TTL_MS;
}

export default function DashboardPage() {
  const [lang, setLangState] = useState<Lang>("ru");
  const [user, setUser] = useState<User | null>(null);
  const [activeTool, setActiveTool] = useState<ToolConfig | null>(null);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [subStatus, setSubStatus] = useState<SubscriptionStatus | null>(null);
  const [showSubModal, setShowSubModal] = useState(false);
  const [renewLoading, setRenewLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const router = useRouter();
  const t = getT(lang);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/");
      return;
    }
    setLangState(getLang() as Lang);
    api.auth.me()
      .then(setUser)
      .catch(() => { clearToken(); router.push("/"); });
    api.stars.subscriptionStatus()
      .then((s) => {
        setSubStatus(s);
        if (s.is_premium && shouldShowModal(s.days_left)) {
          setShowSubModal(true);
        }
        if (!s.is_premium && s.days_left <= 0 && s.expires_at) {
          setShowSubModal(true);
        }
      })
      .catch(() => {});
  }, [router]);

  const handleLangChange = (l: Lang) => {
    setLang(l);
    setLangState(l);
  };

  const handleLogout = () => {
    clearToken();
    router.push("/");
  };

  const handleSuccess = useCallback((result: GenerationResult) => {
    setUser((prev) =>
      prev
        ? { ...prev, generations_used: result.generations_used }
        : prev
    );
  }, []);

  const handleLimitReached = useCallback(() => {
    setActiveTool(null);
    setShowUpgrade(true);
  }, []);

  const handleRenew = async () => {
    if (!user) return;
    setRenewLoading(true);
    try {
      await api.stars.createInvoice(user.id);
      setShowSubModal(false);
      setToast("⭐ Счёт отправлен в ваш Telegram!");
    } catch {
      setToast("Ошибка. Попробуйте ещё раз.");
    } finally {
      setRenewLoading(false);
    }
  };

  const handleDismissSubModal = () => {
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setShowSubModal(false);
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="sticky top-0 z-20 bg-gray-950/90 backdrop-blur border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-3">
          {/* Row 1: logo, nav (desktop), avatar/logout — always a single row */}
          <div className="flex items-center justify-between gap-3">
            <Link href="/" className="font-bold text-gold text-xl shrink-0">RealEstate AI</Link>

            <nav className="hidden md:flex items-center gap-4 text-sm text-gray-400">
              <Link href="/dashboard" className="text-white font-medium">{t.nav.dashboard}</Link>
              <Link href="/history" className="hover:text-white transition-colors">{t.nav.history}</Link>
              <Link href="/billing" className="hover:text-white transition-colors">{t.nav.billing}</Link>
            </nav>

            {/* Desktop: usage counter + lang switcher + avatar/logout inline */}
            <div className="hidden md:flex items-center gap-3">
              <UsageCounter
                used={user.generations_used}
                limit={user.generations_limit}
                isPremium={user.is_premium}
                t={t}
              />
              <LangSwitcher current={lang} onChange={handleLangChange} />
              <div className="flex items-center gap-2">
                {user.photo_url && (
                  <img src={user.photo_url} alt="avatar" className="w-8 h-8 rounded-full" />
                )}
                <button onClick={handleLogout} className="text-xs text-gray-400 hover:text-white transition-colors">
                  {t.nav.logout}
                </button>
              </div>
            </div>

            {/* Mobile: only avatar/logout stay on row 1 next to the logo */}
            <div className="flex md:hidden items-center gap-2 shrink-0">
              {user.photo_url && (
                <img src={user.photo_url} alt="avatar" className="w-8 h-8 rounded-full" />
              )}
              <button onClick={handleLogout} className="text-xs text-gray-400 hover:text-white transition-colors">
                {t.nav.logout}
              </button>
            </div>
          </div>

          {/* Row 2 (mobile only): usage counter + lang switcher, never overflow */}
          <div className="flex md:hidden items-center justify-between gap-3 mt-2">
            <UsageCounter
              used={user.generations_used}
              limit={user.generations_limit}
              isPremium={user.is_premium}
              t={t}
            />
            <LangSwitcher current={lang} onChange={handleLangChange} />
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">{t.dashboard.title}</h1>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {TOOLS.map((tool) => (
            <ToolCard
              key={tool.id}
              tool={tool}
              t={t}
              onClick={() => setActiveTool(tool)}
            />
          ))}
        </div>
      </main>

      <Sidebar
        tool={activeTool}
        t={t}
        lang={lang}
        onClose={() => setActiveTool(null)}
        onSuccess={handleSuccess}
        onLimitReached={handleLimitReached}
      />

      {showUpgrade && (
        <UpgradeModal t={t} onClose={() => setShowUpgrade(false)} />
      )}

      {showSubModal && subStatus && subStatus.expires_at && (
        <SubscriptionExpiredModal
          daysLeft={subStatus.days_left}
          expiresAt={subStatus.expires_at}
          onRenew={handleRenew}
          onDismiss={subStatus.days_left > 0 ? handleDismissSubModal : undefined}
        />
      )}

      {toast && (
        <div
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-gray-800 border border-gray-600 text-white text-sm px-5 py-3 rounded-xl shadow-xl"
          onClick={() => setToast(null)}
        >
          {toast}
        </div>
      )}
    </div>
  );
}
