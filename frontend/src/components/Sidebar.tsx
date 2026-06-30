"use client";
import type { ToolConfig } from "@/lib/toolsConfig";
import type { Translations, Lang } from "@/lib/i18n";
import type { GenerationResult } from "@/lib/api";
import { GenerationForm } from "./GenerationForm";

type Props = {
  tool: ToolConfig | null;
  t: Translations;
  lang: Lang;
  onClose: () => void;
  onSuccess: (result: GenerationResult) => void;
  onLimitReached: () => void;
};

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  return path.split(".").reduce((acc: unknown, key) => {
    if (acc && typeof acc === "object") return (acc as Record<string, unknown>)[key];
    return path;
  }, obj) as string;
}

export function Sidebar({ tool, t, lang, onClose, onSuccess, onLimitReached }: Props) {
  const tObj = t as unknown as Record<string, unknown>;

  return (
    <>
      {tool && (
        <div
          className="fixed inset-0 bg-black/50 z-30"
          onClick={onClose}
        />
      )}
      <div
        className={`fixed right-0 top-0 h-full w-full max-w-md bg-gray-900 border-l border-gray-800 z-40 transform transition-transform duration-300 flex flex-col ${
          tool ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {tool && (
          <>
            <div className="flex items-center justify-between p-5 border-b border-gray-800">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{tool.icon}</span>
                <h2 className="font-semibold text-white">
                  {getNestedValue(tObj, tool.titleKey)}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white text-xl"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-5">
              <GenerationForm
                tool={tool}
                t={t}
                lang={lang}
                onSuccess={onSuccess}
                onLimitReached={onLimitReached}
              />
            </div>
          </>
        )}
      </div>
    </>
  );
}
