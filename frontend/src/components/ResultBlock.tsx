"use client";
import { useState } from "react";
import type { Translations } from "@/lib/i18n";

type Props = {
  text: string;
  t: Translations;
  onRegenerate: () => void;
};

export function ResultBlock({ text, t, onRegenerate }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-4">
      <div className="bg-gray-950 border border-gray-700 rounded-lg p-4 max-h-96 overflow-y-auto">
        <pre className="whitespace-pre-wrap text-sm text-gray-200 font-sans">{text}</pre>
      </div>
      <div className="flex gap-2 mt-3">
        <button
          onClick={handleCopy}
          className="flex-1 py-2 rounded-lg bg-gold text-black font-medium text-sm hover:bg-gold-light transition-colors"
        >
          {copied ? t.form.copied : t.form.copy}
        </button>
        <button
          onClick={onRegenerate}
          className="flex-1 py-2 rounded-lg border border-gray-600 text-gray-300 font-medium text-sm hover:border-gray-400 transition-colors"
        >
          {t.form.regenerate}
        </button>
      </div>
    </div>
  );
}
