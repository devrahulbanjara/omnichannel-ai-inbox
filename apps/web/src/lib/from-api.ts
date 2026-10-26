import type { ApiConversation, ApiMessage } from "./api"
import { CHANNEL_TYPES } from "./channels"
import type { Conversation, Message } from "./types"

// Today: "10:41". Earlier days: "26 Oct".
export function formatTime(iso: string) {
  const date = new Date(iso)
  const isToday = date.toDateString() === new Date().toDateString()
  return isToday
    ? date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })
    : date.toLocaleDateString("en-GB", { day: "numeric", month: "short" })
}

// Unknown channel names show as "web" rather than breaking the channel icon.
function channelFromApi(name: string): Conversation["channel"] {
  return CHANNEL_TYPES.find((type) => type === name) ?? "web"
}

// Maps an API conversation to the screen's Conversation.
// Fields the API does not serve yet get a neutral default; replace each one when the API adds it.
export function conversationFromApi(api: ApiConversation): Conversation {
  return {
    id: api.id,
    contact: { name: api.contact_name, handle: "" },
    channel: channelFromApi(api.channel),
    lastAt: formatTime(api.last_message_at),
    lastMessageText: api.last_message_text ?? undefined,

    // Defaults, not from the API yet:
    assignee: { type: "none" },
    needsHuman: false,
    leadStage: "new",
    score: 0,
    unread: 0,
    summary: "",
    messages: [],
    notes: [],
    tickets: [],
    orders: [],
  }
}

export function messageFromApi(api: ApiMessage): Message {
  return {
    id: api.id,
    kind: "text",
    sender: api.sender_type,
    text: api.text,
    at: formatTime(api.created_at),
    status: api.delivery_status ?? undefined,
    error: api.error ?? undefined,
  }
}
