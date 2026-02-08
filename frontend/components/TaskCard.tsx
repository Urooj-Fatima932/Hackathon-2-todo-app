"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Pencil, Trash2, Loader2 } from "lucide-react";
import { TaskForm } from "./TaskForm";
import { formatRelativeTime } from "@/lib/utils";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import type { Task } from "@/lib/types";

interface TaskCardProps {
  task: Task;
  onUpdate?: () => void;
  onDelete?: () => void;
}

export function TaskCard({ task, onUpdate, onDelete }: TaskCardProps) {
  const [isPending, setIsPending] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const handleToggle = async () => {
    setIsPending(true);
    try {
      await api.toggleTask(task.id);
      toast.success(task.is_completed ? "Task marked as pending" : "Task completed!");
      onUpdate?.();
    } catch (error) {
      toast.error("Failed to update task");
      console.error(error);
    } finally {
      setIsPending(false);
    }
  };

  const handleDelete = async () => {
    setIsPending(true);
    try {
      await api.deleteTask(task.id);
      setIsDeleteOpen(false);
      onDelete?.();
    } catch (error) {
      toast.error("Failed to delete task");
      console.error(error);
    } finally {
      setIsPending(false);
    }
  };

  const handleEditSuccess = () => {
    setIsEditOpen(false);
    toast.success("Task updated successfully!");
    onUpdate?.();
  };

  return (
    <>
      <Card className="card-gradient task-card-hover border-l-4 border-l-primary/30">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            {/* Checkbox */}
            <Checkbox
              checked={task.is_completed}
              onCheckedChange={handleToggle}
              disabled={isPending}
              className="mt-1"
            />

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h3
                className={`text-lg font-semibold mb-1 ${
                  task.is_completed ? "line-through text-muted-foreground" : ""
                }`}
              >
                {task.title}
              </h3>
              {task.description && (
                <p
                  className={`text-sm mb-2 ${
                    task.is_completed ? "text-muted-foreground" : "text-muted-foreground"
                  }`}
                >
                  {task.description}
                </p>
              )}
              <p className="text-xs text-muted-foreground">
                {formatRelativeTime(task.created_at)}
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsEditOpen(true)}
                disabled={isPending}
              >
                <Pencil className="h-4 w-4" />
                <span className="sr-only">Edit task</span>
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDeleteOpen(true)}
                disabled={isPending}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
                <span className="sr-only">Delete task</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>
              Make changes to your task below.
            </DialogDescription>
          </DialogHeader>
          <TaskForm
            task={task}
            onSuccess={handleEditSuccess}
            onCancel={() => setIsEditOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Task</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this task? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button
              variant="outline"
              onClick={() => setIsDeleteOpen(false)}
              disabled={isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isPending}
            >
              {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
