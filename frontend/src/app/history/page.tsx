"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getT, type Lang } from "@/lib/i18n";
import { getLang, setLang, getToken, clearToken } from "@/lib/auth";
import { api, type HistoryItem } from "@/lib/api";
import { LangSwitcher } from "@/components/LangSwitcher";

const TOOL_ICONS: Record<string, string> = {
  description: "🏠",
  instagram: "📸",
  telegram: "✈️",
  "cold-call": "📞",
  "incoming-call": "📲",
  objection: "🛡️",
  followup: "💬",
};

export default function HistoryPage() {
  const [lang, setLangState] = useState<Lang>("ru");
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const t = getT(lang);

  useEffect(() => {
    if (!getToken()) { router.push("/"); return; }
    setLangState(getLang() as Lang);
    api.history.list()
      .then(setItems)
      .catch(() => { clearToken(); router.push("/"); })
      .finally(() => setLoading(false));
  }, [router]);

  const handleLangChange = (l: Lang) => { setLang(l); setLangState(l); };

  const toggleExpand = (id: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleDelete = async (id: number) => {
    await api.history.delete(id);
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="sticky top-0 z-10 bg-gray-950/90 backdrop-blur border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="font-bold text-gold text-xl">RealEstate AI</Link>
          <nav className="hidden md:flex items-center gap-4 text-sm text-gray-400">
            <Link href="/dashboard" className="hover:text-white">{t.nav.dashboard}</Link>
            <Link href="/history" className="text-white font-medium">{t.nav.history}</Link>
            <Link href="/billing" className="hover:text-white">{t.nav.billing}</Link>
          </nav>
          <LangSwitcher current={lang} onChange={handleLangChange} />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">{t.history.title}</h1>

        {loading && <div className="text-gray-400">Loading...</div>}

        {!loading && items.length === 0 && (
          <div className="text-center text-gray-500 py-16">{t.history.empty}</div>
        )}

        <div className="space-y-3">
          {items.map((item) => {
            const isExpanded = expanded.has(item.id);
            const date = new Date(item.created_at).toLocaleDateString(lang === "en" ? "en-US" : "ru-RU", {
              day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
            });

            return (
              <div key={item.id} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
                <div
                  className="flex items-center justify-between p-4 cursor-pointer"
                  onClick={() => toggleExpand(item.id)}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{TOOL_ICONS[item.tool_type] ?? "📝"}</span>
                    <div>
                      <div className="text-sm font-medium text-white">
                        {item.output_preview}
                        {!isExpanded && "…"}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">{date} · {item.language.toUpperCase()}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4 shrink-0">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                      className="text-xs text-red-400 hover:text-red-300 transition-colors"
                    >
                      {t.history.delete}
                    </button>
                    <span className="text-gray-600">{isExpanded ? "▲" : "▼"}</span>
                  </div>
                </div>
                {isExpanded && (
                  <div className="border-t border-gray-800 p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-200 font-sans">
                      {item.output_text}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
