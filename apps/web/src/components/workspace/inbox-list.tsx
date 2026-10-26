"use client"

import { useMemo, useState } from "react"
import { ChevronsUpDown, Flame, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Tag } from "@/components/ui/tag"
import { Panel } from "@/components/ui/surface"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChannelIcon } from "@/components/ui/channel-icon"
import { CHANNEL_LABEL, CHANNEL_TYPES } from "@/lib/channels"
import { STORE_NAME } from "@/lib/mock-data"
import type { ChannelType, Conversation } from "@/lib/types"
import { cn } from "@/lib/utils"
import { ContactAvatar } from "./contact-avatar"
import { AssigneeTag, preview } from "./shared"

const FILTERS = {
  all: () => true,
  mine: (c: Conversation) => c.assignee.type === "staff" && c.assignee.isMe,
  unassigned: (c: Conversation) => c.assignee.type === "none",
  ai: (c: Conversation) => c.assignee.type === "ai",
  human: (c: Conversation) => c.needsHuman,
} as const

type Filter = keyof typeof FILTERS

export function InboxList({
  conversations,
  selectedId,
  onSelect,
}: {
  conversations: Conversation[]
  selectedId: string
  onSelect: (id: string) => void
}) {
  const [filter, setFilter] = useState<Filter>("all")
  const [channel, setChannel] = useState<ChannelType | null>(null)
  const [query, setQuery] = useState("")

  const visible = useMemo(
    () =>
      conversations.filter(
        (c) =>
          FILTERS[filter](c) &&
          (!channel || c.channel === channel) &&
          c.contact.name.toLowerCase().includes(query.trim().toLowerCase()),
      ),
    [conversations, filter, channel, query],
  )
  const needsHuman = conversations.filter((c) => c.needsHuman).length

  return (
    <Panel>
      <header className="space-y-3 p-4 pb-3">
        <button className="flex w-full items-center gap-2 rounded-lg text-left">
          <div className="min-w-0 flex-1">
            <p className="text-caption">Workspace</p>
            <p className="text-title truncate">{STORE_NAME}</p>
          </div>
          <ChevronsUpDown className="size-4 text-muted-foreground" />
        </button>

        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations"
            className="glass-raised h-9 pl-8 shadow-none"
          />
        </div>

        <Tabs value={filter} onValueChange={(v) => setFilter(v as Filter)}>
          <TabsList className="glass-raised w-full">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="mine">Mine</TabsTrigger>
            <TabsTrigger value="unassigned">Open</TabsTrigger>
            <TabsTrigger value="ai">AI</TabsTrigger>
            <TabsTrigger value="human">
              Human
              {needsHuman > 0 && <span className="size-1.5 rounded-full bg-destructive" />}
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="flex flex-wrap gap-1.5">
          {CHANNEL_TYPES.map((key) => {
            const active = channel === key
            return (
              <button
                key={key}
                title={CHANNEL_LABEL[key]}
                aria-pressed={active}
                onClick={() => setChannel(active ? null : key)}
                className={cn(
                  "flex size-7 items-center justify-center rounded-lg border border-transparent text-muted-foreground transition-colors hover:bg-muted",
                  active && "border-primary/30 bg-accent text-accent-foreground",
                )}
              >
                <ChannelIcon channel={key} />
              </button>
            )
          })}
        </div>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">
        {visible.length === 0 && <p className="p-6 text-center text-sm text-muted-foreground">No conversations</p>}
        <ul className="space-y-1">
          {visible.map((c) => (
            <li key={c.id}>
              <button
                onClick={() => onSelect(c.id)}
                className={cn(
                  "flex w-full gap-3 rounded-xl border border-transparent p-2.5 text-left transition-colors hover:bg-card/60",
                  c.id === selectedId && "glass-raised border-primary/20 hover:bg-[var(--glass-raised)]",
                )}
              >
                <ContactAvatar name={c.contact.name} channel={c.channel} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline gap-2">
                    <p className={cn("flex-1 truncate text-sm", c.unread ? "font-semibold" : "font-medium")}>
                      {c.contact.name}
                    </p>
                    <span className="text-meta">{c.lastAt}</span>
                  </div>
                  <p className="mt-0.5 truncate text-sm text-muted-foreground">{preview(c)}</p>
                  <div className="mt-1.5 flex items-center gap-1.5">
                    <AssigneeTag conversation={c} />
                    {c.score >= 80 && (
                      <Tag tone="danger">
                        <Flame /> Hot
                      </Tag>
                    )}
                    {c.unread > 0 && (
                      <span className="bg-brand ml-auto flex size-4.5 items-center justify-center rounded-full text-2xs font-semibold text-white">
                        {c.unread}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </Panel>
  )
}
