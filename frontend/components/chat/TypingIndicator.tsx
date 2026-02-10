"use client";

/**
 * Typing Indicator Component
 * Per FR-022: Loading indicator while waiting for AI response
 * Updated to match green aesthetic theme
 */

import React from "react";
import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 p-4">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
        <Bot className="w-4 h-4 text-secondary-foreground" />
      </div>

      {/* Typing bubble */}
      <div className="bg-secondary rounded-2xl rounded-tl-md px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            TaskBot is thinking
          </span>
          <div className="flex gap-1">
            <div
              className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
              style={{ animationDelay: "0ms" }}
            />
            <div
              className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
              style={{ animationDelay: "150ms" }}
            />
            <div
              className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"
              style={{ animationDelay: "300ms" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
