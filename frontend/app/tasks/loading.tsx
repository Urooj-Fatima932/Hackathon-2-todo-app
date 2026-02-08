import { Card, CardContent } from "@/components/ui/card";

export default function TasksLoading() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="h-10 w-48 bg-muted rounded-md mb-4 animate-pulse" />
        <div className="h-6 w-96 bg-muted rounded-md animate-pulse" />
      </div>

      {/* Filters Skeleton */}
      <div className="flex gap-2 mb-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-10 w-24 bg-muted rounded-md animate-pulse" />
        ))}
      </div>

      {/* Task Cards Skeleton */}
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="h-4 w-4 bg-muted rounded animate-pulse mt-1" />
                <div className="flex-1 space-y-2">
                  <div className="h-5 w-3/4 bg-muted rounded animate-pulse" />
                  <div className="h-4 w-full bg-muted rounded animate-pulse" />
                  <div className="h-4 w-2/3 bg-muted rounded animate-pulse" />
                </div>
                <div className="flex gap-2">
                  <div className="h-8 w-8 bg-muted rounded animate-pulse" />
                  <div className="h-8 w-8 bg-muted rounded animate-pulse" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
