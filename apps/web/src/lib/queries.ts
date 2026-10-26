import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ApiError,
  type ApiConversation,
  type ApiMessage,
  fetchConversations,
  fetchMessages,
  fetchOrganization,
  sendReply,
} from "./api"
import { conversationFromApi, messageFromApi } from "./from-api"

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
