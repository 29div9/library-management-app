import type { ApiError } from "./types";

const API_BASE = "/api";

export class ApiRequestError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

function formatApiError(data: ApiError): string {
  if (typeof data.detail === "string") {
    return data.detail;
  }
  return data.detail.map((e) => e.msg).join("; ");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers: HeadersInit = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = response.status === 204 ? null : await response.json();

  if (!response.ok) {
    const message =
      data && typeof data === "object" && "detail" in data
        ? formatApiError(data as ApiError)
        : `Request failed with status ${response.status}`;
    throw new ApiRequestError(message, response.status);
  }

  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  delete: (path: string) => request<void>(path, { method: "DELETE" }),
};
