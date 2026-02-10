"use client";

/**
 * Floating Chat Widget Component
 * Per FR-020: Floating widget in bottom-right corner, accessible from all pages
 */

import React, { useState } from "react";
import { MessageSquare, X, ChevronLeft, Lock } from "lucide-react";
import { useChatContext } from "./ChatContext";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { ConversationList } from "./ConversationList";
import { TypingIndicator } from "./TypingIndicator";
import { RetryButton } from "./RetryButton";
import Link from "next/link";

export function ChatWidget() {
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

  // Floating button when closed
  if (!isOpen) {
    return (
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-200 hover:scale-105 z-50"
        aria-label="Open chat"
      >
        <MessageSquare className="w-6 h-6" />
      </button>
    );
  }

  // Expanded widget
  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-blue-600 text-white rounded-t-2xl">
        <div className="flex items-center gap-2">
          {(conversationId || messages.length > 0) && !showConversations && (
            <button
              onClick={handleBack}
              className="p-1 hover:bg-blue-700 rounded"
              aria-label="Back to conversations"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <MessageSquare className="w-5 h-5" />
          <span className="font-semibold">TaskBot</span>
        </div>
        <button
          onClick={toggleChat}
          className="p-1 hover:bg-blue-700 rounded"
          aria-label="Close chat"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
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
                <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400 p-6 text-center">
                  <Lock className="w-12 h-12 mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">
                    Sign in to use TaskBot
                  </p>
                  <p className="text-sm mb-4">
                    Please sign in to start managing your tasks with our AI assistant.
                  </p>
                  <Link href="/login" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors inline-block">
                      Sign In
                    </Link>
                </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400 p-6 text-center">
                  <MessageSquare className="w-12 h-12 mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">
                    Hi! I&apos;m TaskBot
                  </p>
                  <p className="text-sm">
                    I can help you manage your tasks. Try saying:
                  </p>
                  <ul className="text-sm mt-2 space-y-1">
                    <li>&quot;Add a task to buy groceries&quot;</li>
                    <li>&quot;Show me my tasks&quot;</li>
                    <li>&quot;Mark task as done&quot;</li>
                  </ul>
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
              <div className="p-4 text-center text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800">
                <p>Please sign in to send messages</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
