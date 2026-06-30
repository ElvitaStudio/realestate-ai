"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getT, type Lang } from "@/lib/i18n";
import { getLang, setLang, getToken, clearToken } from "@/lib/auth";
import { api, type User, type GenerationResult } from "@/lib/api";
import { TOOLS, type ToolConfig } from "@/lib/toolsConfig";
import { LangSwitcher } from "@/components/LangSwitcher";
import { UsageCounter } from "@/components/UsageCounter";
import { ToolCard } from "@/components/ToolCard";
import { Sidebar } from "@/components/Sidebar";
import { UpgradeModal } from "@/components/UpgradeModal";

export default function DashboardPage() {
  const [lang, setLangState] = useState<Lang>("ru");
  const [user, setUser] = useState<User | null>(null);
  const [activeTool, setActiveTool] = useState<ToolConfig | null>(null);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const router = useRouter();
  const t = getT(lang);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/");
      return;
    }
    setLangState(getLang() as Lang);
    api.auth.me().then(setUser).catch(() => {
      clearToken();
      router.push("/");
    });
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
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="font-bold text-gold text-xl">RealEstate AI</Link>
          <nav className="hidden md:flex items-center gap-4 text-sm text-gray-400">
            <Link href="/dashboard" className="text-white font-medium">{t.nav.dashboard}</Link>
            <Link href="/history" className="hover:text-white transition-colors">{t.nav.history}</Link>
            <Link href="/billing" className="hover:text-white transition-colors">{t.nav.billing}</Link>
          </nav>
          <div className="flex items-center gap-3">
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
    </div>
  );
}
