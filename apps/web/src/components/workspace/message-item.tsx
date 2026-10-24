import { Check, CheckCheck, Info, Luggage, ShoppingCart } from "lucide-react"
import { AiMark } from "@/components/ui/ai-mark"
import { Bubble, BubbleContent } from "@/components/ui/bubble"
import { Button } from "@/components/ui/button"
import { Marker, MarkerContent, MarkerIcon } from "@/components/ui/marker"
import { Message, MessageAvatar, MessageContent, MessageFooter } from "@/components/ui/message"
import { Tag } from "@/components/ui/tag"
import { npr } from "@/lib/channels"
import { urgencyTone } from "@/lib/tones"
import type { Message as MessageT, Product } from "@/lib/types"
import { cn } from "@/lib/utils"

function ProductCard({ product }: { product: Product }) {
  return (
    <div className="w-52 shrink-0 overflow-hidden rounded-xl border bg-card shadow-sm">
      <div className="relative flex h-28 items-center justify-center bg-gradient-to-br from-accent to-muted">
        <Luggage className="size-12 text-primary/70" strokeWidth={1.25} />
        <span className="glass-raised absolute bottom-2 left-2 rounded-md px-1.5 py-0.5 text-xs font-semibold tabular-nums">
          {npr(product.price)}
        </span>
      </div>
      <div className="space-y-2.5 p-3">
        <div>
          <p className="text-sm font-medium leading-tight">{product.name}</p>
          <p className="text-caption">{product.variant}</p>
        </div>
        <div className="grid grid-cols-2 gap-1.5">
          <Button variant="outline" size="sm">
            <Info /> Details
          </Button>
          <Button variant="brand" size="sm">
            <ShoppingCart /> Buy now
          </Button>
        </div>
      </div>
    </div>
  )
}

function Status({ status }: { status?: "sent" | "delivered" | "read" }) {
  if (!status) return null
  if (status === "sent") return <Check className="size-3.5" />
  return <CheckCheck className={cn("size-3.5", status === "read" && "text-primary")} />
}

export function MessageItem({ message: m }: { message: MessageT }) {
  if (m.kind === "event")
    return (
      <Marker variant="separator" className="text-xs">
        <MarkerIcon>
          <Info />
        </MarkerIcon>
        <MarkerContent>
          {m.text} · {m.at}
        </MarkerContent>
      </Marker>
    )

  const outgoing = m.sender !== "contact"
  const fromAI = m.sender === "ai"

  return (
    <Message align={outgoing ? "end" : "start"}>
      {fromAI && (
        <MessageAvatar className="glass-raised size-7 min-w-7">
          <AiMark />
        </MessageAvatar>
      )}
      <MessageContent>
        {m.kind === "products" ? (
          <div data-slot="product-carousel" className="flex max-w-[80%] gap-2 overflow-x-auto pb-1">
            {m.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        ) : (
          <Bubble
            align={outgoing ? "end" : "start"}
            variant={fromAI ? "ai" : outgoing ? "brand" : "incoming"}
            className="max-w-[min(80%,34rem)]"
          >
            <BubbleContent className="rounded-2xl px-3.5 py-2.5">{m.text}</BubbleContent>
          </Bubble>
        )}
        <MessageFooter className="gap-1.5 px-1">
          {m.kind === "text" && m.tags && (
            <>
              <Tag tone="brand">{m.tags.intent}</Tag>
              <Tag tone={urgencyTone[m.tags.urgency]}>{m.tags.urgency}</Tag>
            </>
          )}
          <span className="tabular-nums">{m.at}</span>
          {m.kind === "text" && <Status status={m.status} />}
        </MessageFooter>
      </MessageContent>
    </Message>
  )
}
