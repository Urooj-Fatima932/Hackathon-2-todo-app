"use client";

/**
 * Chat Sidebar Component
 * Collapsible right sidebar for TaskBot chat
 * Matches the green aesthetic theme of the application
 */

import React, { useState } from "react";
import { MessageSquare, X, ChevronLeft, ChevronRight, Plus, History, Lock } from "lucide-react";
import { useChatContext } from "./ChatContext";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { ConversationList } from "./ConversationList";
import { TypingIndicator } from "./TypingIndicator";
import { RetryButton } from "./RetryButton";
import { cn } from "@/lib/utils";
import Link from "next/link";

export function ChatSidebar() {
  const {
    isOpen,
    toggleChat,
    conversationId,
    messages,
    isLoading,
    error,
    sendMessage,
    startNewConversation,
    lastToolCalls,
    isAuthenticated,
  } = useChatContext();

  const [showConversations, setShowConversations] = useState(false);

  const handleSendMessage = async (message: string) => {
    if (!isAuthenticated) {
      // If not authenticated, prevent sending messages
      return;
    }
    await sendMessage(message);
  };

  const handleBack = () => {
    setShowConversations(true);
  };

  const handleSelectConversation = () => {
    setShowConversations(false);
  };

  const handleNewChat = () => {
    startNewConversation();
    setShowConversations(false);
  };

  return (
    <>
      {/* Toggle Button - Fixed on right edge */}
      <button
        onClick={toggleChat}
        className={cn(
          "fixed top-1/2 -translate-y-1/2 z-40 flex items-center justify-center",
          "w-10 h-24 bg-primary hover:bg-primary/90 text-primary-foreground",
          "rounded-l-xl shadow-lg transition-all duration-300",
          isOpen ? "right-[400px]" : "right-0"
        )}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        <div className="flex flex-col items-center gap-1">
          {isOpen ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <MessageSquare className="w-5 h-5" />
              <ChevronLeft className="w-4 h-4" />
            </>
          )}
        </div>
      </button>

      {/* Sidebar Panel */}
      <div
        className={cn(
          "fixed top-0 right-0 h-full w-[400px] z-30",
          "bg-card border-l border-border shadow-2xl",
          "transform transition-transform duration-300 ease-in-out",
          "flex flex-col",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 bg-primary text-primary-foreground">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-foreground/20 rounded-lg">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-semibold text-lg">TaskBot</h2>
              <p className="text-xs text-primary-foreground/70">AI Task Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleNewChat}
              className="p-2 hover:bg-primary-foreground/20 rounded-lg transition-colors"
              aria-label="New conversation"
              title="New conversation"
            >
              <Plus className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowConversations(!showConversations)}
              className={cn(
                "p-2 rounded-lg transition-colors",
                showConversations ? "bg-primary-foreground/20" : "hover:bg-primary-foreground/20"
              )}
              aria-label="Conversation history"
              title="Conversation history"
            >
              <History className="w-5 h-5" />
            </button>
            <button
              onClick={toggleChat}
              className="p-2 hover:bg-primary-foreground/20 rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col overflow-hidden bg-background">
          {showConversations ? (
            <ConversationList
              onSelectConversation={handleSelectConversation}
              onNewChat={handleNewChat}
            />
          ) : (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto">
                {!isAuthenticated ? (
                  <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-6 text-center">
                    <div className="p-4 bg-primary/10 rounded-full mb-4">
                      <Lock className="w-10 h-10 text-primary" />
                    </div>
                    <p className="text-lg font-medium mb-2 text-foreground">
                      Sign in to use TaskBot
                    </p>
                    <p className="text-sm mb-4">
                      Please sign in to start managing your tasks with our AI assistant.
                    </p>
                    <Link href="/login" className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-md transition-colors inline-block">
                      Sign In
                    </Link>
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-6 text-center">
                    <div className="p-4 bg-primary/10 rounded-full mb-4">
                      <MessageSquare className="w-10 h-10 text-primary" />
                    </div>
                    <p className="text-lg font-medium mb-2 text-foreground">
                      Hi! I&apos;m TaskBot
                    </p>
                    <p className="text-sm mb-4">
                      I can help you manage your tasks. Try saying:
                    </p>
                    <div className="space-y-2 w-full max-w-xs">
                      {[
                        "Add a task to buy groceries",
                        "Show me my tasks",
                        "Mark the first task as done",
                      ].map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSendMessage(suggestion)}
                          className="w-full px-4 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded-lg transition-colors text-left text-secondary-foreground"
                        >
                          &quot;{suggestion}&quot;
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <ChatMessages
                    messages={messages}
                    lastToolCalls={lastToolCalls}
                  />
                )}

                {/* Loading indicator */}
                {isLoading && isAuthenticated && <TypingIndicator />}

                {/* Error with retry */}
                {error && isAuthenticated && <RetryButton error={error} />}
              </div>

              {/* Input */}
              {isAuthenticated ? (
                <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
              ) : (
                <div className="p-4 text-center text-muted-foreground bg-secondary">
                  <p>Please sign in to send messages</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Backdrop overlay when sidebar is open on mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-20 lg:hidden"
          onClick={toggleChat}
          aria-label="Close chat"
        />
      )}
    </>
  );
}
