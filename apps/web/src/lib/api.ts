import type { components } from "./api-types"

type Schemas = components["schemas"]
export type ApiOrganization = Schemas["OrganizationRead"]
export type ApiConversation = Schemas["ConversationRead"]
export type ApiMessage = Schemas["MessageRead"]
export type ApiErrorBody = Schemas["ErrorBody"]

// Inlined into the browser bundle at build time (NEXT_PUBLIC_ prefix).
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// Any failed API call. Carries the API's error body and the request ID for log lookups.
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly body: ApiErrorBody,
    readonly requestId: string | null,
  ) {
    super(body.message)
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init)
  if (!response.ok) {
    const fallback: ApiErrorBody = { code: "unknown_error", message: `Request failed (${response.status})` }
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body?.error ?? fallback, response.headers.get("X-Request-ID"))
  }
  return response.json()
}

export const fetchOrganization = () => request<ApiOrganization>("/organization")

export const fetchConversations = () => request<ApiConversation[]>("/conversations")

export const fetchMessages = (conversationId: string) =>
  request<ApiMessage[]>(`/conversations/${conversationId}/messages`)

// The same idempotency key on a resend makes the API return the first reply instead of a second.
export const sendReply = (conversationId: string, text: string, idempotencyKey: string) =>
  request<ApiMessage>(`/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Idempotency-Key": idempotencyKey },
    body: JSON.stringify({ text }),
  })
