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
  if (c.assignee.type === "user")
    return (
      <Tag className={className}>
        <UserRound /> {c.assignee.name}
      </Tag>
    )
  return <Tag tone="warning" className={className}>
      Unassigned
    </Tag>
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
  if (!last) return ""
  if (last.kind === "products") return `Shared ${last.items.length} products`
  if (last.kind === "event") return last.text
  const prefix = { contact: "", ai: "AI: ", user: "Team: " }[last.sender]
  return prefix + last.text
}
