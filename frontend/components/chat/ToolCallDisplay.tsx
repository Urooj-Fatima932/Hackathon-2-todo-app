"use client";

/**
 * Tool Call Display Component
 * Per FR-023: Shows what actions the AI performed (real-time only)
 * Updated to match green aesthetic theme
 */

import React from "react";
import {
  Plus,
  List,
  CheckCircle,
  Edit,
  Trash2,
  Eye,
  Wrench,
} from "lucide-react";
import { ToolCall } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ToolCallDisplayProps {
  toolCalls: ToolCall[];
}

const TOOL_ICONS: Record<string, React.ElementType> = {
  add_task: Plus,
  list_tasks: List,
  complete_task: CheckCircle,
  update_task: Edit,
  delete_task: Trash2,
  get_task: Eye,
};

const TOOL_LABELS: Record<string, string> = {
  add_task: "Created task",
  list_tasks: "Listed tasks",
  complete_task: "Completed task",
  update_task: "Updated task",
  delete_task: "Deleted task",
  get_task: "Viewed task",
};

export function ToolCallDisplay({ toolCalls }: ToolCallDisplayProps) {
  if (toolCalls.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
        <Wrench className="w-3 h-3" />
        Actions performed:
      </p>
      <div className="space-y-1.5">
        {toolCalls.map((tc, index) => {
          const Icon = TOOL_ICONS[tc.tool] || Wrench;
          const label = TOOL_LABELS[tc.tool] || tc.tool;

          return (
            <div
              key={index}
              className={cn(
                "flex items-center gap-2 text-xs",
                "bg-primary/10 px-3 py-1.5 rounded-lg"
              )}
            >
              <Icon className="w-3.5 h-3.5 text-primary" />
              <span className="text-foreground font-medium">{label}</span>
              {tc.args && Object.keys(tc.args).length > 0 && (
                <span className="text-muted-foreground truncate max-w-[150px]">
                  ({formatArgs(tc.args)})
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatArgs(args: Record<string, unknown>): string {
  const entries = Object.entries(args);
  if (entries.length === 0) return "";

  // Show the most relevant arg (usually title or task_id)
  if (args.title) return `"${String(args.title).slice(0, 30)}"`;
  if (args.task_id) return `ID: ${args.task_id}`;
  if (args.status) return `${args.status}`;

  return entries
    .slice(0, 2)
    .map(([k, v]) => `${k}: ${String(v).slice(0, 20)}`)
    .join(", ");
}
