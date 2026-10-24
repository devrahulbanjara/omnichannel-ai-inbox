import type { Tone } from "@/components/ui/tag"
import type { Order, Tags, Ticket } from "./types"

export const urgencyTone: Record<Tags["urgency"], Tone> = { low: "success", medium: "warning", high: "danger" }
export const priorityTone: Record<Ticket["priority"], Tone> = {
  low: "neutral",
  medium: "warning",
  high: "danger",
  urgent: "danger",
}
export const paymentTone: Record<Order["payment"], Tone> = { unpaid: "danger", paid: "success" }
