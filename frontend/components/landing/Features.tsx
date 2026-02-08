import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, Smile, Target, Shield } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Fast",
    description: "Lightning-fast performance with optimistic updates. Your changes appear instantly.",
  },
  {
    icon: Smile,
    title: "Simple",
    description: "Clean, intuitive interface that gets out of your way. Focus on what matters.",
  },
  {
    icon: Target,
    title: "Organized",
    description: "Smart filtering and organization to keep your tasks manageable and clear.",
  },
  {
    icon: Shield,
    title: "Reliable",
    description: "Your data is safe and always in sync. Never lose track of your tasks.",
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 md:py-28 lg:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl mb-4">
            Everything you need to stay productive
          </h2>
          <p className="text-lg text-muted-foreground">
            Built with the features that matter most to help you get things done.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title} className="border-2 transition-all hover:shadow-lg hover:border-primary/50">
              <CardHeader>
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
