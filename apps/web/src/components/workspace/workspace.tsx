"use client"

import { useState, useSyncExternalStore } from "react"
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import { conversations as initial } from "@/lib/mock-data"
import type { Assignee, Conversation } from "@/lib/types"
import { AppRail } from "./app-rail"
import { ContextPanel } from "./context-panel"
import { ConversationView } from "./conversation-view"
import { InboxList } from "./inbox-list"

function useMedia(query: string) {
  return useSyncExternalStore(
    (cb) => {
      const mql = window.matchMedia(query)
      mql.addEventListener("change", cb)
      return () => mql.removeEventListener("change", cb)
    },
    () => window.matchMedia(query).matches,
    () => true,
  )
}

const now = () => new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })

const Handle = () => (
  <ResizableHandle className="w-2 bg-transparent after:w-2 [&>div]:opacity-0 hover:[&>div]:opacity-100" withHandle />
)

export function Workspace() {
  const [items, setItems] = useState<Conversation[]>(initial)
  const [selectedId, setSelectedId] = useState(initial[0].id)
  const [mobileView, setMobileView] = useState<"list" | "thread" | "details">("list")
  const isDesktop = useMedia("(min-width: 1024px)")
  const isWide = useMedia("(min-width: 1280px)")
  const [detailsOpen, setDetailsOpen] = useState(false)

  const selected = items.find((c) => c.id === selectedId) ?? items[0]

  const update = (patch: (c: Conversation) => Conversation) =>
    setItems((all) => all.map((c) => (c.id === selected.id ? patch(c) : c)))

  const assign = (assignee: Assignee) => {
    const label =
      assignee.type === "ai" ? "AI agent" : assignee.type === "user" ? (assignee.isMe ? "you" : assignee.name) : "nobody"
    update((c) => ({
      ...c,
      assignee,
      needsHuman: assignee.type === "user" ? false : c.needsHuman,
      messages: [...c.messages, { id: crypto.randomUUID(), kind: "event", text: `Assigned to ${label}`, at: now() }],
    }))
  }

  const send = (text: string) =>
    update((c) => ({
      ...c,
      lastAt: now(),
      messages: [...c.messages, { id: crypto.randomUUID(), kind: "text", sender: "user", text, at: now(), status: "sent" }],
    }))

  const select = (id: string) => {
    setSelectedId(id)
    setItems((all) => all.map((c) => (c.id === id ? { ...c, unread: 0 } : c)))
    setMobileView("thread")
  }

  const list = <InboxList conversations={items} selectedId={selected.id} onSelect={select} />
  const thread = (
    <ConversationView
      conversation={selected}
      onAssign={assign}
      onSend={send}
      onBack={isDesktop ? undefined : () => setMobileView("list")}
      onOpenDetails={isWide ? undefined : () => (isDesktop ? setDetailsOpen(true) : setMobileView("details"))}
    />
  )

  if (!isDesktop)
    return (
      <main className="flex h-dvh gap-3 p-3">
        <AppRail />
        <div className="min-w-0 flex-1">
          {mobileView === "list" && list}
          {mobileView === "thread" && thread}
          {mobileView === "details" && <ContextPanel conversation={selected} onClose={() => setMobileView("thread")} />}
        </div>
      </main>
    )

  return (
    <main className="flex h-dvh gap-2 p-3">
      <AppRail />
      <ResizablePanelGroup orientation="horizontal" className="min-w-0 flex-1">
        <ResizablePanel defaultSize="26" minSize="20" maxSize="36">
          {list}
        </ResizablePanel>
        <Handle />
        <ResizablePanel minSize="35">{thread}</ResizablePanel>
        {isWide && (
          <>
            <Handle />
            <ResizablePanel defaultSize="24" minSize="18" maxSize="32">
              <ContextPanel conversation={selected} />
            </ResizablePanel>
          </>
        )}
      </ResizablePanelGroup>
      {!isWide && detailsOpen && (
        <>
          <div className="fixed inset-0 z-40 bg-foreground/10 animate-in fade-in-0" onClick={() => setDetailsOpen(false)} />
          <div className="fixed inset-y-3 right-3 z-50 w-80 animate-in slide-in-from-right-4 fade-in-0">
            <ContextPanel conversation={selected} onClose={() => setDetailsOpen(false)} solid />
          </div>
        </>
      )}
    </main>
  )
}
