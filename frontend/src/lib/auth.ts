const TOKEN_KEY = "realestate_token";
const LANG_KEY = "realestate_lang";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function getLang(): string {
  if (typeof window === "undefined") return "ru";
  return localStorage.getItem(LANG_KEY) ?? "ru";
}

export function setLang(lang: string): void {
  localStorage.setItem(LANG_KEY, lang);
}
