"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { setToken } from "@/lib/auth";

type Props = {
  onSuccess?: () => void;
  buttonText?: string;
  compact?: boolean;
};

declare global {
  interface Window {
    onTelegramAuth: (user: Record<string, unknown>) => void;
  }
}

export function TelegramLogin({ onSuccess, compact = false }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scriptError, setScriptError] = useState(false);

  // NEXT_PUBLIC_* values are inlined into the JS bundle at `next build` time,
  // not read at runtime. If .env.local changes after the build ran, this
  // will silently be undefined until the app is rebuilt and PM2 is restarted.
  const botUsername = process.env.NEXT_PUBLIC_TG_BOT_USERNAME;

  useEffect(() => {
    // eslint-disable-next-line no-console
    console.log("[TelegramLogin] NEXT_PUBLIC_TG_BOT_USERNAME =", botUsername);

    if (!botUsername || !containerRef.current) return;

    window.onTelegramAuth = async (user) => {
      try {
        const result = await api.auth.telegram(user);
        setToken(result.access_token);
        onSuccess?.();
        window.location.href = "/dashboard";
      } catch (err) {
        console.error("Telegram auth failed", err);
      }
    };

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", compact ? "medium" : "large");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.setAttribute("data-request-access", "write");
    script.async = true;
    script.onload = () => console.log("[TelegramLogin] widget script loaded");
    script.onerror = () => {
      console.error("[TelegramLogin] failed to load telegram-widget.js (network/CSP block?)");
      setScriptError(true);
    };
    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [botUsername, onSuccess, compact]);

  if (!botUsername) {
    return (
      <span className="text-xs text-red-400">
        NEXT_PUBLIC_TG_BOT_USERNAME не задан в собранном бандле — пересоберите фронтенд
        (npm run build) после обновления .env.local
      </span>
    );
  }

  if (scriptError) {
    return (
      <span className="text-xs text-red-400">
        Не удалось загрузить telegram-widget.js — проверьте сеть/CSP
      </span>
    );
  }

  // Telegram injects an <iframe> into this div asynchronously (after the
  // script loads via postMessage), not synchronously on script.onload.
  // Without explicit sizing, an empty div inside a flex container collapses
  // to 0x0 and never grows once the iframe lands, making the button
  // invisible even though the script loaded successfully.
  return (
    <div
      ref={containerRef}
      className={`relative z-10 inline-block ${compact ? "min-h-[36px] min-w-[140px]" : "min-h-[40px] min-w-[180px]"}`}
    />
  );
}
