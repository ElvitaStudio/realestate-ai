"use client";
import type { ToolConfig } from "@/lib/toolsConfig";
import type { Translations } from "@/lib/i18n";

type Props = {
  tool: ToolConfig;
  t: Translations;
  onClick: () => void;
};

type NestedKeyOf<T> = {
  [K in keyof T & string]: T[K] extends object
    ? `${K}.${NestedKeyOf<T[K]>}`
    : K;
}[keyof T & string];

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  return path.split(".").reduce((acc: unknown, key) => {
    if (acc && typeof acc === "object") return (acc as Record<string, unknown>)[key];
    return "";
  }, obj) as string;
}

export function ToolCard({ tool, t, onClick }: Props) {
  const title = getNestedValue(t as unknown as Record<string, unknown>, tool.titleKey);
  const desc = getNestedValue(t as unknown as Record<string, unknown>, tool.descKey);

  return (
    <button
      onClick={onClick}
      className="group bg-gray-900 border border-gray-800 hover:border-gold rounded-xl p-5 text-left transition-all hover:shadow-lg hover:shadow-gold/10"
    >
      <span className="text-3xl">{tool.icon}</span>
      <h3 className="mt-3 font-semibold text-white group-hover:text-gold transition-colors">
        {title}
      </h3>
      <p className="mt-1 text-sm text-gray-400">{desc}</p>
    </button>
  );
}
