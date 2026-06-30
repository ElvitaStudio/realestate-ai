"use client";
import type { Translations } from "@/lib/i18n";

type Props = {
  used: number;
  limit: number;
  isPremium: boolean;
  t: Translations;
};

export function UsageCounter({ used, limit, isPremium, t }: Props) {
  if (isPremium) {
    return (
      <span className="text-sm text-gold font-medium">
        ♾ {t.dashboard.unlimited}
      </span>
    );
  }

  const remaining = Math.max(0, limit - used);
  const pct = Math.min(100, (used / limit) * 100);

  return (
    <div className="flex items-center gap-2 min-w-0">
      <span className="text-sm text-gray-300 whitespace-nowrap shrink-0">
        {t.dashboard.generationsLeft}:{" "}
        <span className={remaining === 0 ? "text-red-400 font-bold" : "text-gold font-bold"}>
          {remaining}
        </span>
        /{limit}
      </span>
      <div className="w-12 sm:w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden shrink-0">
        <div
          className="h-full bg-gold transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
