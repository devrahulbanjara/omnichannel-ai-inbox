import { useEffect } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ApiError,
  type ApiConversation,
  type ApiMessage,
  fetchConversations,
  fetchMessages,
  fetchOrganization,
  LIVE_URL,
  sendReply,
} from "./api"
import { conversationFromApi, messageFromApi } from "./from-api"

const RECONNECT_DELAY_MS = 2000

const toConversations = (rows: ApiConversation[]) => rows.map(conversationFromApi)
const toMessages = (rows: ApiMessage[]) => rows.map(messageFromApi)

export function useOrganization() {
  return useQuery({ queryKey: ["organization"], queryFn: fetchOrganization })
}

export function useConversations() {
  return useQuery({ queryKey: ["conversations"], queryFn: fetchConversations, select: toConversations })
}

export function useMessages(conversationId: string) {
  return useQuery({
    queryKey: ["messages", conversationId],
    queryFn: () => fetchMessages(conversationId),
    select: toMessages,
  })
}

type NewReply = { conversationId: string; text: string; idempotencyKey: string }

export function useSendReply() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ conversationId, text, idempotencyKey }: NewReply) =>
      sendReply(conversationId, text, idempotencyKey),
    // Retry only when the API was unreachable. A retry reuses the same idempotency key,
    // so the API saves the reply once even if the first attempt did reach it.
    retry: (failureCount, error) => !(error instanceof ApiError) && failureCount < 2,
    onSettled: (_reply, _error, { conversationId }) => {
      queryClient.invalidateQueries({ queryKey: ["messages", conversationId] })
      queryClient.invalidateQueries({ queryKey: ["conversations"] })
    },
  })
}

type LiveEvent = { type: "message.created" | "message.updated"; conversation_id: string }

// Keeps a WebSocket open to the API and reloads whatever an event says has changed.
// Reconnects after a drop and then reloads everything, because events sent while offline are lost.
export function useLiveUpdates() {
  const queryClient = useQueryClient()

  useEffect(() => {
    let socket: WebSocket | undefined
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined
    let stopped = false

    const connect = () => {
      socket = new WebSocket(LIVE_URL)
      socket.onopen = () => queryClient.invalidateQueries()
      socket.onmessage = (message) => {
        const event: LiveEvent = JSON.parse(message.data)
        queryClient.invalidateQueries({ queryKey: ["conversations"] })
        queryClient.invalidateQueries({ queryKey: ["messages", event.conversation_id] })
      }
      socket.onclose = () => {
        if (!stopped) reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS)
      }
    }

    connect()
    return () => {
      stopped = true
      clearTimeout(reconnectTimer)
      socket?.close()
    }
  }, [queryClient])
}
