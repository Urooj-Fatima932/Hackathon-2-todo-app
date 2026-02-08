"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import type { TaskFilter } from "@/lib/types";

const filters: { value: TaskFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
];

export function TaskFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentFilter = (searchParams.get("filter") || "all") as TaskFilter;

  const handleFilterChange = (filter: TaskFilter) => {
    const params = new URLSearchParams(searchParams.toString());

    if (filter === "all") {
      params.delete("filter");
    } else {
      params.set("filter", filter);
    }

    router.push(`/tasks?${params.toString()}`);
  };

  return (
    <div className="flex gap-2 p-1 bg-secondary/50 rounded-lg border border-border/50 backdrop-blur-sm">
      {filters.map((filter) => (
        <Button
          key={filter.value}
          variant={currentFilter === filter.value ? "default" : "ghost"}
          size="sm"
          onClick={() => handleFilterChange(filter.value)}
          className={currentFilter === filter.value ? "shadow-md" : ""}
        >
          {filter.label}
        </Button>
      ))}
    </div>
  );
}
