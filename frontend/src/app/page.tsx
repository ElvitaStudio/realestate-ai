"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getT, type Lang } from "@/lib/i18n";
import { getLang, setLang, getToken } from "@/lib/auth";
import { LangSwitcher } from "@/components/LangSwitcher";
import { TelegramLogin } from "@/components/TelegramLogin";
import { TOOLS } from "@/lib/toolsConfig";

export default function LandingPage() {
  const [lang, setLangState] = useState<Lang>("ru");
  const router = useRouter();
  const t = getT(lang);

  useEffect(() => {
    setLangState(getLang() as Lang);
    if (getToken()) router.push("/dashboard");
  }, [router]);

  const handleLangChange = (l: Lang) => {
    setLang(l);
    setLangState(l);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="sticky top-0 z-10 bg-gray-950/90 backdrop-blur border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="font-bold text-gold text-xl">RealEstate AI</div>
          <div className="flex items-center gap-4">
            <LangSwitcher current={lang} onChange={handleLangChange} />
            <TelegramLogin compact />
          </div>
        </div>
      </header>

      <section className="max-w-4xl mx-auto px-4 pt-20 pb-16 text-center">
        <h1 className="text-4xl md:text-5xl font-bold leading-tight">
          {t.landing.heroTitle}
        </h1>
        <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
          {t.landing.heroSubtitle}
        </p>
        <div className="mt-8">
          <TelegramLogin />
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 pb-16">
        <h2 className="text-2xl font-bold text-center mb-8">{t.landing.tools}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {TOOLS.map((tool) => {
            const tObj = t as unknown as Record<string, unknown>;
            const getVal = (path: string) =>
              path.split(".").reduce((a: unknown, k) =>
                a && typeof a === "object" ? (a as Record<string, unknown>)[k] : path, tObj) as string;
            return (
              <Link
                key={tool.id}
                href="/dashboard"
                className="bg-gray-900 border border-gray-800 hover:border-gold rounded-xl p-4 text-center transition-colors group"
              >
                <div className="text-3xl">{tool.icon}</div>
                <div className="mt-2 font-medium text-sm group-hover:text-gold transition-colors">{getVal(tool.titleKey)}</div>
                <div className="mt-1 text-xs text-gray-400">{getVal(tool.descKey)}</div>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-4 pb-16">
        <h2 className="text-2xl font-bold text-center mb-10">{t.landing.howItWorks}</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { num: "1", title: t.landing.step1Title, desc: t.landing.step1Desc },
            { num: "2", title: t.landing.step2Title, desc: t.landing.step2Desc },
            { num: "3", title: t.landing.step3Title, desc: t.landing.step3Desc },
          ].map((step) => (
            <div key={step.num} className="text-center">
              <div className="w-10 h-10 rounded-full bg-gold text-black font-bold text-lg flex items-center justify-center mx-auto">
                {step.num}
              </div>
              <h3 className="mt-3 font-semibold">{step.title}</h3>
              <p className="mt-1 text-sm text-gray-400">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-4xl mx-auto px-4 pb-20">
        <h2 className="text-2xl font-bold text-center mb-8">{t.landing.pricingTitle}</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col">
            <h3 className="text-xl font-bold">{t.landing.freePlan}</h3>
            <p className="text-3xl font-bold mt-2">$0</p>
            <p className="text-gray-400 mt-2">{t.landing.freeDesc}</p>
            <ul className="mt-4 space-y-2 text-sm text-gray-300 flex-1">
              <li>✓ 5 генераций</li>
              <li>✓ Все 7 инструментов</li>
              <li>✓ 4 языка</li>
            </ul>
            <div className="mt-6">
              <TelegramLogin />
            </div>
          </div>
          <div className="bg-gray-900 border border-gold rounded-xl p-6 flex flex-col">
            <h3 className="text-xl font-bold text-gold">{t.landing.premiumPlan}</h3>
            <p className="text-3xl font-bold mt-2">{t.landing.premiumPrice}</p>
            <p className="text-gray-400 mt-2">{t.landing.premiumDesc}</p>
            <ul className="mt-4 space-y-2 text-sm text-gray-300 flex-1">
              <li>✓ Безлимитные генерации</li>
              <li>✓ Все 7 инструментов</li>
              <li>✓ 4 языка</li>
              <li>✓ Приоритетная поддержка</li>
            </ul>
            <div className="mt-6">
              <Link
                href="/billing"
                className="block w-full py-2.5 rounded-lg bg-gold text-black font-semibold text-center hover:bg-gold-light transition-colors"
              >
                {t.billing.subscribe}
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
