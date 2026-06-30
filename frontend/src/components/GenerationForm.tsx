"use client";
import { useState, useCallback } from "react";
import type { ToolConfig } from "@/lib/toolsConfig";
import type { Translations, Lang } from "@/lib/i18n";
import type { GenerationResult } from "@/lib/api";
import { ResultBlock } from "./ResultBlock";
import { ApiError } from "@/lib/api";

type Props = {
  tool: ToolConfig;
  t: Translations;
  lang: Lang;
  onSuccess: (result: GenerationResult) => void;
  onLimitReached: () => void;
};

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  return path.split(".").reduce((acc: unknown, key) => {
    if (acc && typeof acc === "object") return (acc as Record<string, unknown>)[key];
    return path;
  }, obj) as string;
}

function buildInitialValues(tool: ToolConfig): Record<string, unknown> {
  return Object.fromEntries(
    tool.fields.map((f) => [f.name, f.defaultValue ?? ""])
  );
}

export function GenerationForm({ tool, t, lang, onSuccess, onLimitReached }: Props) {
  const [values, setValues] = useState<Record<string, unknown>>(buildInitialValues(tool));
  const [outputLang, setOutputLang] = useState<Lang>(lang);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const setValue = (name: string, value: unknown) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const toggleCheckbox = (name: string, value: string) => {
    const current = (values[name] as string[]) ?? [];
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    setValue(name, updated);
  };

  const handleSubmit = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = { ...values, language: outputLang };
      const res = await tool.apiFn(payload) as GenerationResult;
      setResult(res);
      onSuccess(res);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        onLimitReached();
      } else {
        setError(err instanceof Error ? err.message : "Error");
      }
    } finally {
      setLoading(false);
    }
  }, [values, outputLang, tool, onSuccess, onLimitReached]);

  const tObj = t as unknown as Record<string, unknown>;

  return (
    <div className="space-y-4">
      {tool.fields.map((field) => {
        const label = getNestedValue(tObj, field.labelKey);

        if (field.type === "select") {
          return (
            <div key={field.name}>
              <label className="block text-sm text-gray-400 mb-1">{label}</label>
              <select
                value={values[field.name] as string}
                onChange={(e) => setValue(field.name, e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-gold"
              >
                {field.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {getNestedValue(tObj, opt.labelKey)}
                  </option>
                ))}
              </select>
            </div>
          );
        }

        if (field.type === "textarea") {
          return (
            <div key={field.name}>
              <label className="block text-sm text-gray-400 mb-1">{label}</label>
              <textarea
                value={values[field.name] as string}
                onChange={(e) => setValue(field.name, e.target.value)}
                rows={3}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-gold resize-none"
              />
            </div>
          );
        }

        if (field.type === "text" || field.type === "number") {
          return (
            <div key={field.name}>
              <label className="block text-sm text-gray-400 mb-1">{label}</label>
              <input
                type={field.type}
                value={values[field.name] as string}
                onChange={(e) => setValue(field.name, e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-gold"
              />
            </div>
          );
        }

        if (field.type === "checkbox") {
          return (
            <label key={field.name} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={values[field.name] as boolean}
                onChange={(e) => setValue(field.name, e.target.checked)}
                className="accent-gold"
              />
              <span className="text-sm text-gray-300">{label}</span>
            </label>
          );
        }

        if (field.type === "checkboxGroup") {
          return (
            <div key={field.name}>
              <label className="block text-sm text-gray-400 mb-2">{label}</label>
              <div className="grid grid-cols-2 gap-1">
                {field.options?.map((opt) => {
                  const checked = ((values[field.name] as string[]) ?? []).includes(opt.value);
                  return (
                    <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleCheckbox(field.name, opt.value)}
                        className="accent-gold"
                      />
                      <span className="text-xs text-gray-300">
                        {getNestedValue(tObj, opt.labelKey)}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>
          );
        }

        return null;
      })}

      <div>
        <label className="block text-sm text-gray-400 mb-1">{t.form.language}</label>
        <select
          value={outputLang}
          onChange={(e) => setOutputLang(e.target.value as Lang)}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-gold"
        >
          <option value="ru">{t.form.ru}</option>
          <option value="ua">{t.form.ua}</option>
          <option value="en">{t.form.en}</option>
          <option value="bg">{t.form.bg}</option>
        </select>
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full py-3 rounded-lg bg-gold text-black font-semibold hover:bg-gold-light disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? t.form.generating : t.form.generate}
      </button>

      {result && (
        <ResultBlock
          text={result.output_text}
          t={t}
          onRegenerate={handleSubmit}
        />
      )}
    </div>
  );
}
