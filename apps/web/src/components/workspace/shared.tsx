import { Hand, UserRound } from "lucide-react"
import { AiMark } from "@/components/ui/ai-mark"
import { Tag } from "@/components/ui/tag"
import type { Conversation } from "@/lib/types"

export function AssigneeTag({ conversation: c, className }: { conversation: Conversation; className?: string }) {
  if (c.needsHuman)
    return (
      <Tag tone="danger" className={className}>
        <Hand /> Needs human
      </Tag>
    )
  if (c.assignee.type === "ai")
    return (
      <Tag tone="brand" className={className}>
        <AiMark /> AI agent
      </Tag>
    )
  return (
    <Tag className={className}>
      <UserRound /> Staff
    </Tag>
  )
}

export const LEAD_STAGE: Record<Conversation["leadStage"], string> = {
  new: "New",
  interested: "Interested",
  ordering: "Ordering",
  won: "Won",
  lost: "Lost",
}

export function preview(c: Conversation) {
  const last = c.messages.at(-1)
  if (!last) return c.lastMessageText ?? ""
  if (last.kind === "products") return `Shared ${last.items.length} products`
  if (last.kind === "event") return last.text
  const prefix = { customer: "", ai: "AI: ", staff: "Team: " }[last.sender]
  return prefix + last.text
}
