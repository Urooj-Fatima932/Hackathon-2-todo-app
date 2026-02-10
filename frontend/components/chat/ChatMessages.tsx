"use client";

/**
 * Chat Messages Component
 * Per FR-021: User messages right-aligned, AI messages left-aligned
 * Updated to match green aesthetic theme
 */

import React, { useEffect, useRef } from "react";
import { Bot, User } from "lucide-react";
import { ChatMessage, ToolCall } from "@/lib/types";
import { ToolCallDisplay } from "./ToolCallDisplay";
import { cn } from "@/lib/utils";

interface ChatMessagesProps {
  messages: ChatMessage[];
  lastToolCalls?: ToolCall[];
}

export function ChatMessages({ messages, lastToolCalls }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="p-4 space-y-4">
      {messages.map((message, index) => {
        const isUser = message.role === "user";
        const isLastAssistant =
          message.role === "assistant" && index === messages.length - 1;

        return (
          <div
            key={message.id}
            className={cn(
              "flex gap-3",
              isUser ? "flex-row-reverse" : "flex-row"
            )}
          >
            {/* Avatar */}
            <div
              className={cn(
                "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                isUser
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              {isUser ? (
                <User className="w-4 h-4" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>

            {/* Message bubble */}
            <div
              className={cn(
                "max-w-[75%] rounded-2xl px-4 py-3",
                isUser
                  ? "bg-primary text-primary-foreground rounded-tr-md"
                  : "bg-secondary text-secondary-foreground rounded-tl-md"
              )}
            >
              <p className="text-sm whitespace-pre-wrap leading-relaxed">
                {message.content}
              </p>

              {/* Show tool calls for the last assistant message only (FR-023) */}
              {isLastAssistant &&
                lastToolCalls &&
                lastToolCalls.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-primary/20">
                    <ToolCallDisplay toolCalls={lastToolCalls} />
                  </div>
                )}
            </div>
          </div>
        );
      })}
      <div ref={messagesEndRef} />
    </div>
  );
}
