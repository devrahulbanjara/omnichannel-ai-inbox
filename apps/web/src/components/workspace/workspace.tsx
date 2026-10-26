"use client"

import { useState, useSyncExternalStore } from "react"
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import { ApiError } from "@/lib/api"
import { useConversations, useLiveUpdates, useMessages, useSendReply } from "@/lib/queries"
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

const Handle = () => (
  <ResizableHandle className="w-2 bg-transparent after:w-2 [&>div]:opacity-0 hover:[&>div]:opacity-100" withHandle />
)

function StatusMessage({ title, detail }: { title: string; detail?: string }) {
  return (
    <main className="flex h-dvh items-center justify-center p-6 text-center">
      <div className="space-y-1">
        <p className="text-sm font-medium">{title}</p>
        {detail && <p className="text-sm text-muted-foreground">{detail}</p>}
      </div>
    </main>
  )
}

export function Workspace() {
  useLiveUpdates()
  const { data: conversations, error, isPending } = useConversations()

  if (isPending) return <StatusMessage title="Loading conversations…" />
  if (error) {
    const requestId = error instanceof ApiError && error.requestId ? ` · Request ID ${error.requestId}` : ""
    return <StatusMessage title="Could not load conversations" detail={error.message + requestId} />
  }
  if (conversations.length === 0) return <StatusMessage title="No conversations yet" />

  return <WorkspaceScreen conversations={conversations} />
}

function WorkspaceScreen({ conversations }: { conversations: Conversation[] }) {
  const [selectedId, setSelectedId] = useState(conversations[0].id)
  // Assignment has no API yet, so it is kept in this browser only.
  const [assignees, setAssignees] = useState<Record<string, Assignee>>({})
  const [mobileView, setMobileView] = useState<"list" | "thread" | "details">("list")
  const isDesktop = useMedia("(min-width: 1024px)")
  const isWide = useMedia("(min-width: 1280px)")
  const [detailsOpen, setDetailsOpen] = useState(false)

  const items = conversations.map((c) => (assignees[c.id] ? { ...c, assignee: assignees[c.id] } : c))
  const current = items.find((c) => c.id === selectedId) ?? items[0]
  const { data: messages = [] } = useMessages(current.id)
  const selected = { ...current, messages }
  const sendReply = useSendReply()

  const assign = (assignee: Assignee) => setAssignees((all) => ({ ...all, [selected.id]: assignee }))

  const send = (text: string) =>
    sendReply.mutate({ conversationId: selected.id, text, idempotencyKey: crypto.randomUUID() })

  const select = (id: string) => {
    setSelectedId(id)
    sendReply.reset()
    setMobileView("thread")
  }

  const list = <InboxList conversations={items} selectedId={selected.id} onSelect={select} />
  const thread = (
    <ConversationView
      conversation={selected}
      onAssign={assign}
      onSend={send}
      sendError={sendReply.error?.message}
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
