"use client"

import { useState } from "react"
import { ArrowLeft, ArrowUp, CircleCheck, PanelRightOpen, Paperclip, ShoppingBag } from "lucide-react"
import { AiMark } from "@/components/ui/ai-mark"
import { Button } from "@/components/ui/button"
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "@/components/ui/message-scroller"
import { Panel } from "@/components/ui/surface"
import { Textarea } from "@/components/ui/textarea"
import { CHANNEL_LABEL } from "@/lib/channels"
import type { Assignee, Conversation } from "@/lib/types"
import { CustomerAvatar } from "./customer-avatar"
import { MessageItem } from "./message-item"
import { AssigneeTag } from "./shared"


export function ConversationView({
  conversation: c,
  onAssign,
  onSend,
  sendError,
  onBack,
  onOpenDetails,
}: {
  conversation: Conversation
  onAssign: (owner: Assignee["type"]) => void
  onSend: (text: string) => void
  sendError?: string
  onBack?: () => void
  onOpenDetails?: () => void
}) {
  const canReply = c.assignee.type === "staff"

  return (
    <Panel>
      <header className="flex items-center gap-3 border-b px-4 py-3">
        {onBack && (
          <Button variant="ghost" size="icon" onClick={onBack} aria-label="Back to inbox">
            <ArrowLeft />
          </Button>
        )}
        <CustomerAvatar name={c.customer.name} channel={c.channel} />
        <div className="min-w-0 flex-1">
          <p className="text-title truncate">{c.customer.name}</p>
          <p className="text-caption truncate">
            {c.customer.handle} · {CHANNEL_LABEL[c.channel]}
          </p>
        </div>
        <AssigneeTag conversation={c} className="hidden sm:inline-flex" />
        <Button variant="ghost" size="icon" aria-label="Resolve conversation">
          <CircleCheck />
        </Button>
        {onOpenDetails && (
          <Button variant="ghost" size="icon" onClick={onOpenDetails} aria-label="Open details">
            <PanelRightOpen />
          </Button>
        )}
      </header>

      {c.summary && (
        <div className="glass-raised mx-4 mt-3 flex gap-2.5 rounded-xl px-3.5 py-2.5 text-sm leading-relaxed">
          <AiMark className="mt-0.5" />
          <p>
            <span className="text-ai font-medium">Summary · </span>
            <span className="text-muted-foreground">{c.summary}</span>
          </p>
        </div>
      )}

      <MessageScrollerProvider key={c.id} defaultScrollPosition="end" autoScroll>
        <MessageScroller className="min-h-0 flex-1">
          <MessageScrollerViewport>
            <MessageScrollerContent className="gap-4 px-4 py-5">
              {c.messages.map((m) => (
                <MessageScrollerItem key={m.id} messageId={m.id}>
                  <MessageItem message={m} />
                </MessageScrollerItem>
              ))}
            </MessageScrollerContent>
          </MessageScrollerViewport>
          <MessageScrollerButton />
        </MessageScroller>
      </MessageScrollerProvider>

      <footer className="p-3 pt-0">
        {sendError && <p className="px-1 pb-2 text-sm text-destructive">Reply not saved: {sendError}</p>}
        {canReply ? (
          <Composer onSend={onSend} onHandToAI={() => onAssign("ai")} />
        ) : (
          <div className="ai-working flex flex-wrap items-center gap-3 rounded-xl bg-card px-4 py-3">
            <AiMark active />
            <p className="min-w-48 flex-1 text-sm text-muted-foreground">
              The AI agent is handling this conversation. Take it over to reply yourself.
            </p>
            <Button variant="brand" size="sm" onClick={() => onAssign("staff")}>
              Assign yourself
            </Button>
          </div>
        )}
      </footer>
    </Panel>
  )
}

function Composer({ onSend, onHandToAI }: { onSend: (text: string) => void; onHandToAI: () => void }) {
  const [text, setText] = useState("")
  const send = () => {
    if (!text.trim()) return
    onSend(text.trim())
    setText("")
  }

  return (
    <div className="glass-raised rounded-xl p-2 focus-within:border-primary/30">
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            send()
          }
        }}
        placeholder="Type a reply…  ( / for quick replies )"
        className="min-h-12 resize-none border-0 bg-transparent shadow-none focus-visible:ring-0 dark:bg-transparent"
      />
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" aria-label="Attach file">
          <Paperclip />
        </Button>
        <Button variant="ghost" size="icon-sm" aria-label="Share products">
          <ShoppingBag />
        </Button>
        <Button variant="ghost" size="sm" onClick={onHandToAI} className="text-muted-foreground">
          <AiMark /> Hand to AI
        </Button>
        <Button variant="brand" size="icon-sm" className="ml-auto" onClick={send} aria-label="Send" disabled={!text.trim()}>
          <ArrowUp />
        </Button>
      </div>
    </div>
  )
}
