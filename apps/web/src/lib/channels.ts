import type { ChannelType } from "./types"

export const CHANNEL_LABEL: Record<ChannelType, string> = {
  rahulcoolgram: "RahulCoolGram",
  instagram: "Instagram",
  messenger: "Messenger",
  whatsapp: "WhatsApp",
  telegram: "Telegram",
  web: "Website",
  email: "Email",
}

export const CHANNEL_TYPES = Object.keys(CHANNEL_LABEL) as ChannelType[]

export const npr = (n: number) => `NPR ${n.toLocaleString("en-IN")}`

export const initials = (name: string) =>
  name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
