"use client";

/**
 * Conversation List Component
 * Per FR-020b: Sidebar panel showing user's conversations
 * Updated to match green aesthetic theme
 */

import React, { useState } from "react";
import { Plus, Trash2, MessageSquare } from "lucide-react";
import { useChatContext } from "./ChatContext";
import { formatDistanceToNow, cn } from "@/lib/utils";

interface ConversationListProps {
  onSelectConversation: () => void;
  onNewChat: () => void;
}

export function ConversationList({
  onSelectConversation,
  onNewChat,
}: ConversationListProps) {
  const {
    conversations,
    conversationId,
    loadConversation,
    deleteConversation,
  } = useChatContext();

  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleSelect = async (id: string) => {
    await loadConversation(id);
    onSelectConversation();
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();

    // Confirm deletion (FR-025)
    if (
      !confirm("Are you sure you want to delete this conversation? This cannot be undone.")
    ) {
      return;
    }

    setDeletingId(id);
    await deleteConversation(id);
    setDeletingId(null);
  };

  return (
    <div className="flex flex-col h-full">
      {/* New Chat Button */}
      <div className="p-4 border-b border-border">
        <button
          onClick={onNewChat}
          className={cn(
            "w-full flex items-center justify-center gap-2 px-4 py-3",
            "bg-primary hover:bg-primary/90 text-primary-foreground",
            "rounded-xl transition-colors font-medium"
          )}
        >
          <Plus className="w-5 h-5" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-6 text-center">
            <div className="p-3 bg-secondary rounded-full mb-3">
              <MessageSquare className="w-6 h-6" />
            </div>
            <p className="text-sm font-medium">No conversations yet</p>
            <p className="text-xs mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleSelect(conversation.id)}
                className={cn(
                  "flex items-center justify-between px-3 py-3 rounded-xl cursor-pointer transition-all",
                  "hover:bg-secondary",
                  conversationId === conversation.id
                    ? "bg-primary/10 border border-primary/20"
                    : "border border-transparent"
                )}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className={cn(
                    "p-2 rounded-lg",
                    conversationId === conversation.id
                      ? "bg-primary/20"
                      : "bg-secondary"
                  )}>
                    <MessageSquare className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {conversation.title || "New conversation"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(conversation.updated_at)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={(e) => handleDelete(e, conversation.id)}
                  disabled={deletingId === conversation.id}
                  className={cn(
                    "p-2 rounded-lg transition-colors",
                    "text-muted-foreground hover:text-destructive hover:bg-destructive/10",
                    "disabled:opacity-50"
                  )}
                  aria-label="Delete conversation"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
