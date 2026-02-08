"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { TaskCard } from "@/components/TaskCard";
import { TaskForm } from "@/components/TaskForm";
import { TaskFilters } from "@/components/TaskFilters";
import { EmptyState } from "@/components/EmptyState";
import { useAuth } from "@/lib/auth/context";
import { api } from "@/lib/api";
import type { Task, TaskFilter } from "@/lib/types";
import toast from "react-hot-toast";

export default function TasksPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const filter = (searchParams.get("filter") || "all") as TaskFilter;

  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const fetchTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await api.getTasks(filter);
      setTasks(data);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
      toast.error("Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  // Fetch tasks when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks();
    }
  }, [isAuthenticated, fetchTasks]);

  const handleTaskCreated = () => {
    setIsCreateOpen(false);
    fetchTasks();
    toast.success("Task created successfully!");
  };

  const handleTaskUpdated = () => {
    fetchTasks();
  };

  const handleTaskDeleted = () => {
    fetchTasks();
    toast.success("Task deleted successfully!");
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  // Filter tasks client-side for display
  const filteredTasks =
    filter === "all"
      ? tasks
      : filter === "pending"
      ? tasks.filter((t) => !t.is_completed)
      : tasks.filter((t) => t.is_completed);

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-primary/5 to-transparent rounded-2xl -z-10 blur-3xl"></div>
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
          My Tasks
        </h1>
        <p className="text-muted-foreground text-lg">
          Manage and organize your tasks efficiently
        </p>
      </div>

      {/* Filters and Create Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <TaskFilters />
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Task
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Task</DialogTitle>
              <DialogDescription>
                Add a new task to your list. Fill in the details below.
              </DialogDescription>
            </DialogHeader>
            <TaskForm onSuccess={handleTaskCreated} />
          </DialogContent>
        </Dialog>
      </div>

      {/* Tasks List */}
      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">
          Loading tasks...
        </div>
      ) : filteredTasks.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onUpdate={handleTaskUpdated}
              onDelete={handleTaskDeleted}
            />
          ))}
        </div>
      )}
    </div>
  );
}
