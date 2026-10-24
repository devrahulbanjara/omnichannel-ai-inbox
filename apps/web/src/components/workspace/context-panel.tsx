import { Flame, MapPin, Phone, Plus, X } from "lucide-react"
import { AiMark } from "@/components/ui/ai-mark"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Panel, Tile } from "@/components/ui/surface"
import { Tag } from "@/components/ui/tag"
import { npr } from "@/lib/channels"
import { paymentTone, priorityTone } from "@/lib/tones"
import type { Conversation } from "@/lib/types"
import { cn } from "@/lib/utils"
import { ContactAvatar } from "./contact-avatar"
import { LEAD_STAGE } from "./shared"

function Section({ title, items, children }: { title: string; items?: unknown[]; children: React.ReactNode }) {
  return (
    <section className="space-y-2.5 border-t p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-overline">
          {title}
          {items && <span className="ml-1 font-normal">({items.length})</span>}
        </h3>
        <Button variant="ghost" size="icon-xs" aria-label={`Add ${title.toLowerCase()}`}>
          <Plus />
        </Button>
      </div>
      {items?.length === 0 ? <p className="text-caption">None yet</p> : children}
    </section>
  )
}

const scoreBand = (s: number) => (s >= 80 ? "Hot" : s >= 50 ? "Warm" : "Cold")

export function ContextPanel({
  conversation: c,
  onClose,
  solid,
}: {
  conversation: Conversation
  onClose?: () => void
  solid?: boolean
}) {
  return (
    <Panel solid={solid} className="overflow-y-auto">
      <div className="relative flex flex-col items-center px-4 pt-6 pb-4 text-center">
        {onClose && (
          <Button variant="ghost" size="icon-sm" onClick={onClose} className="absolute top-3 right-3" aria-label="Close">
            <X />
          </Button>
        )}
        <ContactAvatar name={c.contact.name} channel={c.channel} size="lg" />
        <p className="text-title mt-3">{c.contact.name}</p>
        <p className="text-caption">{c.contact.handle}</p>

        <Tile className="mt-4 w-full space-y-2 p-3 text-left">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5 font-medium">
              <AiMark className="size-3.5" /> AI qualification
            </span>
            <span className="flex items-center gap-1 font-semibold tabular-nums">
              {scoreBand(c.score) === "Hot" && <Flame className="size-3.5 text-destructive" />}
              {scoreBand(c.score)} · {c.score}
            </span>
          </div>
          <Progress value={c.score} className="h-1.5 *:data-[slot=progress-indicator]:bg-ai" />
          <p className="text-meta">Stage: {LEAD_STAGE[c.leadStage]}</p>
        </Tile>
      </div>

      <Section title="Contact" items={c.contact.phone || c.contact.address ? undefined : []}>
        <div className="space-y-1.5 text-sm [&_svg]:size-3.5 [&_svg]:text-muted-foreground">
          {c.contact.phone && (
            <p className="flex items-center gap-2">
              <Phone /> {c.contact.phone}
            </p>
          )}
          {c.contact.address && (
            <p className="flex items-center gap-2">
              <MapPin /> {c.contact.address}
            </p>
          )}
        </div>
      </Section>

      <Section title="Internal notes" items={c.notes}>
        {c.notes.map((n) => (
          <Tile key={n.id}>
            <div className="text-meta flex justify-between">
              <span className={cn("font-medium text-foreground", n.isAI && "text-ai")}>{n.author}</span>
              {n.at}
            </div>
            <p className="text-sm leading-snug">{n.body}</p>
          </Tile>
        ))}
      </Section>

      <Section title="Tickets" items={c.tickets}>
        {c.tickets.map((t) => (
          <Tile key={t.id} className="space-y-1.5">
            <div className="text-meta flex items-center justify-between">
              #{t.number}
              <Tag tone={priorityTone[t.priority]} className="uppercase">
                {t.priority}
              </Tag>
            </div>
            <p className="text-sm font-medium">{t.title}</p>
            <div className="text-meta flex items-center justify-between">
              <Tag className="uppercase">{t.status.replace("_", " ")}</Tag>
              {t.at}
            </div>
          </Tile>
        ))}
      </Section>

      <Section title="Orders" items={c.orders}>
        {c.orders.map((o) => (
          <Tile key={o.id}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">#{o.number}</span>
              <Tag className="capitalize">{o.fulfillment}</Tag>
            </div>
            <div className="text-caption flex items-center justify-between">
              {o.items} item{o.items > 1 && "s"} · {o.zone}
              <Tag tone={paymentTone[o.payment]} className="capitalize">
                {o.payment}
              </Tag>
            </div>
            <div className="text-caption flex items-center justify-between">
              {o.at}
              <span className="font-semibold text-foreground tabular-nums">{npr(o.total)}</span>
            </div>
          </Tile>
        ))}
      </Section>
    </Panel>
  )
}
