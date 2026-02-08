import { CheckCircle2 } from "lucide-react";

export function EmptyState() {
  return (
    <div className="text-center py-16 relative">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/5 rounded-3xl -z-10"></div>
      <div className="inline-flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 to-primary/10 mb-6 shadow-lg shadow-primary/10">
        <CheckCircle2 className="h-10 w-10 text-primary" />
      </div>
      <h3 className="text-xl font-semibold mb-2 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
        No tasks yet
      </h3>
      <p className="text-muted-foreground text-base">
        Create your first task to get started!
      </p>
    </div>
  );
}
