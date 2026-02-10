"use client";

/**
 * Chat Input Component
 * Text input with send button and Enter key support
 * Updated to match green aesthetic theme
 */

import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = "Type a message...",
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;

    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  return (
    <div className="p-4 border-t border-border bg-card">
      <div className="flex items-end gap-2">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            "flex-1 px-4 py-3 bg-secondary text-secondary-foreground rounded-xl resize-none",
            "focus:outline-none focus:ring-2 focus:ring-primary/50",
            "disabled:opacity-50 placeholder:text-muted-foreground",
            "transition-all duration-200"
          )}
          style={{ minHeight: "48px", maxHeight: "120px" }}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          className={cn(
            "p-3 rounded-xl transition-all duration-200",
            "bg-primary hover:bg-primary/90 text-primary-foreground",
            "disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed",
            "focus:outline-none focus:ring-2 focus:ring-primary/50"
          )}
          aria-label="Send message"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
      <p className="text-xs text-muted-foreground mt-2 text-center">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
