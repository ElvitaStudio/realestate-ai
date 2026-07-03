import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8008";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? "Unknown error");
  }
  return res.json() as Promise<T>;
}

export type User = {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  photo_url: string | null;
  is_premium: boolean;
  generations_used: number;
  generations_limit: number;
  subscription_expires_at: string | null;
};

export type GenerationResult = {
  id: number;
  output_text: string;
  generations_used: number;
  generations_limit: number;
};

export type SubscriptionStatus = {
  is_premium: boolean;
  expires_at: string | null;
  days_left: number;
};

export type HistoryItem = {
  id: number;
  tool_type: string;
  language: string;
  output_preview: string;
  output_text: string;
  created_at: string;
};

export const api = {
  auth: {
    telegram: (data: Record<string, unknown>) =>
      request<{ access_token: string }>("/auth/telegram", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    me: () => request<User>("/auth/me"),
  },
  generate: {
    description: (data: unknown) =>
      request<GenerationResult>("/generate/description", { method: "POST", body: JSON.stringify(data) }),
    instagram: (data: unknown) =>
      request<GenerationResult>("/generate/instagram", { method: "POST", body: JSON.stringify(data) }),
    telegram: (data: unknown) =>
      request<GenerationResult>("/generate/telegram", { method: "POST", body: JSON.stringify(data) }),
    coldCall: (data: unknown) =>
      request<GenerationResult>("/generate/cold-call", { method: "POST", body: JSON.stringify(data) }),
    incomingCall: (data: unknown) =>
      request<GenerationResult>("/generate/incoming-call", { method: "POST", body: JSON.stringify(data) }),
    objection: (data: unknown) =>
      request<GenerationResult>("/generate/objection", { method: "POST", body: JSON.stringify(data) }),
    followup: (data: unknown) =>
      request<GenerationResult>("/generate/followup", { method: "POST", body: JSON.stringify(data) }),
  },
  history: {
    list: () => request<HistoryItem[]>("/history"),
    delete: (id: number) => request<void>(`/history/${id}`, { method: "DELETE" }),
  },
  billing: {
    createInvoice: (redirectUrl: string, webhookUrl: string) =>
      request<{ invoice_url: string; invoice_id: string }>("/billing/create-invoice", {
        method: "POST",
        body: JSON.stringify({ redirect_url: redirectUrl, webhook_url: webhookUrl }),
      }),
    status: () =>
      request<{ is_premium: boolean; subscription_expires_at: string | null }>("/billing/status"),
  },
  stars: {
    createInvoice: (userId: number) =>
      request<{ ok: boolean }>("/stars/create-invoice", {
        method: "POST",
        body: JSON.stringify({ user_id: userId }),
      }),
    subscriptionStatus: () => request<SubscriptionStatus>("/stars/subscription-status"),
  },
};

export { ApiError };
