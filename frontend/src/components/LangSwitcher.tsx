"use client";
import { LANGUAGES, type Lang } from "@/lib/i18n";
import { setLang } from "@/lib/auth";

type Props = {
  current: Lang;
  onChange: (lang: Lang) => void;
};

export function LangSwitcher({ current, onChange }: Props) {
  const handleChange = (lang: Lang) => {
    setLang(lang);
    onChange(lang);
  };

  return (
    <div className="flex gap-1">
      {LANGUAGES.map((l) => (
        <button
          key={l.code}
          onClick={() => handleChange(l.code)}
          className={`px-2 py-1 text-xs rounded font-medium transition-colors ${
            current === l.code
              ? "bg-gold text-black"
              : "text-gray-400 hover:text-white"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}
