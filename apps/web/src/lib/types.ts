export type ChannelType = "instagram" | "messenger" | "whatsapp" | "telegram" | "web" | "email"

export type Assignee = { type: "none" } | { type: "ai" } | { type: "user"; name: string; isMe: boolean }

export type LeadStage = "new" | "interested" | "ordering" | "won" | "lost"

export type Tags = { intent: string; urgency: "low" | "medium" | "high" }

export type Product = { id: string; name: string; variant: string; price: number }

export type Message =
  | {
      id: string
      kind: "text"
      sender: "contact" | "ai" | "user"
      text: string
      at: string
      status?: "sent" | "delivered" | "read"
      tags?: Tags
    }
  | { id: string; kind: "products"; sender: "ai" | "user"; items: Product[]; at: string }
  | { id: string; kind: "event"; text: string; at: string }

export type Note = { id: string; author: string; isAI: boolean; body: string; at: string }

export type Ticket = {
  id: string
  number: number
  title: string
  priority: "low" | "medium" | "high" | "urgent"
  status: "open" | "in_progress" | "closed"
  at: string
}

export type Order = {
  id: string
  number: number
  items: number
  zone: string
  total: number
  fulfillment: "pending" | "confirmed" | "dispatched" | "delivered"
  payment: "unpaid" | "paid"
  at: string
}

export type Conversation = {
  id: string
  contact: { name: string; handle: string; phone?: string; address?: string }
  channel: ChannelType
  assignee: Assignee
  needsHuman: boolean
  leadStage: LeadStage
  score: number
  unread: number
  lastAt: string
  summary: string
  messages: Message[]
  notes: Note[]
  tickets: Ticket[]
  orders: Order[]
}
