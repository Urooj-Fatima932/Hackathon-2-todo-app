"use client";

/**
 * Retry Button Component
 * Per FR-022a: Retry button shown when AI request fails or times out
 * Updated to match green aesthetic theme
 */

import React from "react";
import { RefreshCw, AlertCircle } from "lucide-react";
import { useChatContext } from "./ChatContext";
import { cn } from "@/lib/utils";

interface RetryButtonProps {
  error: string;
}

export function RetryButton({ error }: RetryButtonProps) {
  const { retryLastMessage, clearError, isLoading } = useChatContext();

  const handleRetry = async () => {
    await retryLastMessage();
  };

  return (
    <div className="p-4">
      <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-destructive/20 rounded-lg">
            <AlertCircle className="w-4 h-4 text-destructive" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-destructive font-medium mb-1">Something went wrong</p>
            <p className="text-xs text-muted-foreground">{error}</p>
            <div className="flex gap-2 mt-3">
              <button
                onClick={handleRetry}
                disabled={isLoading}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 text-sm font-medium",
                  "bg-primary hover:bg-primary/90 text-primary-foreground",
                  "rounded-lg transition-colors disabled:opacity-50"
                )}
              >
                <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
                Retry
              </button>
              <button
                onClick={clearError}
                className={cn(
                  "px-4 py-2 text-sm font-medium",
                  "text-muted-foreground hover:text-foreground",
                  "transition-colors"
                )}
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
