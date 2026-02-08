"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import type { Task } from "@/lib/types";

interface TaskFormProps {
  task?: Task;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function TaskForm({ task, onSuccess, onCancel }: TaskFormProps) {
  const [isPending, setIsPending] = useState(false);
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsPending(true);

    try {
      if (task) {
        await api.updateTask(task.id, { title, description: description || undefined });
      } else {
        await api.createTask({ title, description: description || undefined });
      }

      setTitle("");
      setDescription("");
      onSuccess?.();
    } catch (error) {
      toast.error(task ? "Failed to update task" : "Failed to create task");
      console.error(error);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="title">
          Title <span className="text-destructive">*</span>
        </Label>
        <Input
          id="title"
          name="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title..."
          required
          maxLength={200}
          disabled={isPending}
        />
        <p className="text-xs text-muted-foreground">
          {title.length}/200 characters
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          name="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description (optional)..."
          rows={4}
          maxLength={1000}
          disabled={isPending}
        />
        <p className="text-xs text-muted-foreground">
          {description.length}/1000 characters
        </p>
      </div>

      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isPending}
          >
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isPending || !title.trim()}>
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {task ? "Update Task" : "Create Task"}
        </Button>
      </div>
    </form>
  );
}
