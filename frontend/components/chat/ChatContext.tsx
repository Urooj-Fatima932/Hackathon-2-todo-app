"use client";

/**
 * Chat Context and Provider for floating chat widget.
 * Following chatkit-pro skill pattern with React Context + Portal.
 *
 * Manages:
 * - Widget open/closed state
 * - Current conversation ID
 * - Messages for current conversation
 * - Loading and error states
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
  ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { api } from "@/lib/api";
import { ChatMessage, Conversation, ToolCall } from "@/lib/types";
import { ChatSidebar } from "./ChatSidebar";
import { useAuth } from "@/lib/auth/context";

// Event listener type for task changes
type TaskChangeListener = () => void;

interface ChatContextType {
  // Widget state
  isOpen: boolean;
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;

  // Conversation state
  conversationId: string | null;
  setConversationId: (id: string | null) => void;
  conversations: Conversation[];

  // Message state
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;

  // UI state
  isLoading: boolean;
  error: string | null;
  lastToolCalls: ToolCall[];

  // Actions
  sendMessage: (message: string) => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  startNewConversation: () => void;
  clearError: () => void;
  retryLastMessage: () => Promise<void>;

  // Task change subscription (for real-time UI updates)
  onTaskChange: (listener: TaskChangeListener) => () => void;
  
  // Auth state
  isAuthenticated: boolean;
}

const ChatContext = createContext<ChatContextType | null>(null);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within ChatProvider");
  }
  return context;
}

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  // Widget state
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Task change listeners (for real-time UI updates)
  const taskChangeListeners = useRef<Set<TaskChangeListener>>(new Set());

  // Conversation state
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  // Message state
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastToolCalls, setLastToolCalls] = useState<ToolCall[]>([]);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(
    null
  );
  
  // Get auth context
  const { isAuthenticated } = useAuth();

  // Handle client-side mounting for portal
  useEffect(() => {
    setMounted(true);
  }, []);

  // Toggle functions
  const toggleChat = useCallback(() => setIsOpen((prev) => !prev), []);
  const openChat = useCallback(() => setIsOpen(true), []);
  const closeChat = useCallback(() => setIsOpen(false), []);

  // Clear error
  const clearError = useCallback(() => setError(null), []);

  // Load conversations list
  const loadConversations = useCallback(async () => {
    try {
      const response = await api.getConversations();
      setConversations(response.conversations);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }, []);

  // Load specific conversation
  const loadConversation = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getConversation(id);
      setMessages(response.messages);
      setConversationId(id);
    } catch (err) {
      setError("Failed to load conversation");
      console.error("Failed to load conversation:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Start new conversation
  const startNewConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setLastToolCalls([]);
    setError(null);
  }, []);

  // Delete conversation
  const deleteConversation = useCallback(
    async (id: string) => {
      try {
        await api.deleteConversation(id);
        setConversations((prev) => prev.filter((c) => c.id !== id));
        if (conversationId === id) {
          startNewConversation();
        }
      } catch (err) {
        setError("Failed to delete conversation");
        console.error("Failed to delete conversation:", err);
      }
    },
    [conversationId, startNewConversation]
  );

  // Subscribe to task changes (returns unsubscribe function)
  const onTaskChange = useCallback((listener: TaskChangeListener) => {
    taskChangeListeners.current.add(listener);
    // Return unsubscribe function
    return () => {
      taskChangeListeners.current.delete(listener);
    };
  }, []);

  // Notify all task change listeners
  const notifyTaskChange = useCallback(() => {
    taskChangeListeners.current.forEach((listener) => {
      try {
        listener();
      } catch (err) {
        console.error("Task change listener error:", err);
      }
    });
  }, []);

  // Send message
  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim()) return;

      setIsLoading(true);
      setError(null);
      setLastFailedMessage(message);

      // Optimistically add user message
      const tempUserMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        role: "user",
        content: message,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMessage]);

      try {
        const response = await api.sendMessage(
          message,
          conversationId || undefined
        );

        // Update conversation ID if new
        if (!conversationId) {
          setConversationId(response.conversation_id);
          // Refresh conversations list
          loadConversations();
        }

        // Add assistant message
        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.response,
          created_at: new Date().toISOString(),
          tool_calls: response.tool_calls,
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setLastToolCalls(response.tool_calls);
        setLastFailedMessage(null);

        // Notify task list to refresh if backend reports any task changes
        if (response.tasks_changed) {
          notifyTaskChange();
        }
      } catch (err: unknown) {
        // Remove optimistic user message on error
        setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));

        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);
        console.error("Failed to send message:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, loadConversations, notifyTaskChange]
  );

  // Retry last failed message
  const retryLastMessage = useCallback(async () => {
    if (lastFailedMessage) {
      await sendMessage(lastFailedMessage);
    }
  }, [lastFailedMessage, sendMessage]);

  // Load conversations when widget opens
  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen, loadConversations]);

  const value: ChatContextType = {
    isOpen,
    toggleChat,
    openChat,
    closeChat,
    conversationId,
    setConversationId,
    conversations,
    messages,
    setMessages,
    isLoading,
    error,
    lastToolCalls,
    sendMessage,
    loadConversation,
    loadConversations,
    deleteConversation,
    startNewConversation,
    clearError,
    retryLastMessage,
    onTaskChange,
    isAuthenticated, // Pass authentication status to context
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
      {mounted &&
        typeof window !== "undefined" &&
        createPortal(<ChatSidebar />, document.body)}
    </ChatContext.Provider>
  );
}
