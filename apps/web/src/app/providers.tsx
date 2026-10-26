"use client"

import type { ReactNode } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

let browserQueryClient: QueryClient | undefined

// A new client per server render; one shared client in the browser so the cache survives re-renders.
function getQueryClient() {
  if (typeof window === "undefined") return new QueryClient()
  browserQueryClient ??= new QueryClient()
  return browserQueryClient
}

export function Providers({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={getQueryClient()}>{children}</QueryClientProvider>
}
