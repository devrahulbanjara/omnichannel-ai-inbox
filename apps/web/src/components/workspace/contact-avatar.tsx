import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ChannelIcon } from "@/components/ui/channel-icon"
import { CHANNEL_LABEL, initials } from "@/lib/channels"
import type { ChannelType } from "@/lib/types"
import { cn } from "@/lib/utils"

export function ChannelBadge({ channel, className }: { channel: ChannelType; className?: string }) {
  return (
    <span
      title={CHANNEL_LABEL[channel]}
      className={cn("inline-flex size-4.5 items-center justify-center rounded-full bg-white ring-2 ring-card", className)}
    >
      <ChannelIcon channel={channel} className="size-3.5 text-black/60" />
    </span>
  )
}

export function ContactAvatar({
  name,
  channel,
  size = "default",
}: {
  name: string
  channel?: ChannelType
  size?: "default" | "lg"
}) {
  return (
    <div className="relative shrink-0">
      <Avatar className={size === "lg" ? "size-16" : "size-10"}>
        <AvatarFallback className="bg-accent text-accent-foreground font-medium">{initials(name)}</AvatarFallback>
      </Avatar>
      {channel && <ChannelBadge channel={channel} className="absolute -right-0.5 -bottom-0.5" />}
    </div>
  )
}
