"use client";
import { useEffect, useRef } from "react";
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

  useEffect(() => {
    const botUsername = process.env.NEXT_PUBLIC_TG_BOT_USERNAME;
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
    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [onSuccess, compact]);

  return <div ref={containerRef} />;
}
