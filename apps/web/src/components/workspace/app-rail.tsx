"use client"

import { ChartNoAxesColumn, Inbox, Moon, Plug, Settings, ShoppingBag, Sun, Ticket, Users } from "lucide-react"
import { useTheme } from "next-themes"
import { AiMark } from "@/components/ui/ai-mark"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

const NAV = [
  { label: "Inbox", icon: Inbox, active: true },
  { label: "Contacts", icon: Users },
  { label: "Tickets", icon: Ticket },
  { label: "Orders", icon: ShoppingBag },
  { label: "AI agent", icon: AiMark },
  { label: "Analytics", icon: ChartNoAxesColumn },
  { label: "Channels", icon: Plug },
]

function RailButton({
  label,
  children,
  active,
  onClick,
}: {
  label: string
  children: React.ReactNode
  active?: boolean
  onClick?: () => void
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon-lg"
          aria-label={label}
          onClick={onClick}
          className={cn("rounded-xl text-muted-foreground", active && "bg-accent text-accent-foreground")}
        >
          {children}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="right">{label}</TooltipContent>
    </Tooltip>
  )
}

export function AppRail() {
  const { resolvedTheme, setTheme } = useTheme()

  return (
    <nav className="glass hidden w-16 shrink-0 flex-col items-center gap-1 rounded-2xl py-3 md:flex">
      <div className="bg-brand mb-3 flex size-9 items-center justify-center rounded-xl text-white shadow-sm">
        <Inbox className="size-4.5" />
      </div>
      {NAV.map(({ label, icon: Icon, active }) => (
        <RailButton key={label} label={label} active={active}>
          <Icon />
        </RailButton>
      ))}
      <div className="mt-auto flex flex-col items-center gap-1">
        <RailButton label="Toggle theme" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
          <Sun className="dark:hidden" />
          <Moon className="hidden dark:block" />
        </RailButton>
        <RailButton label="Settings">
          <Settings />
        </RailButton>
        <Avatar className="mt-2 size-8">
          <AvatarFallback className="bg-brand text-xs font-medium text-white">YO</AvatarFallback>
        </Avatar>
      </div>
    </nav>
  )
}
