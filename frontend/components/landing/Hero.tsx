"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Check, Sparkles, Zap, Shield, Users, CheckCircle, Clock } from "lucide-react";
import { useAuth } from "@/lib/auth/context";

export function Hero() {
  const { isAuthenticated } = useAuth();

  return (
    <section className="relative min-h-[calc(100vh-4rem)] flex flex-col mt-[10px] overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]" />
        <div className="absolute left-1/2 -translate-x-1/2 top-0 -z-10 h-[400px] w-[600px] rounded-full bg-gradient-to-r from-violet-500/30 via-fuchsia-500/20 to-pink-500/30 opacity-40 blur-[100px] animate-pulse" />
        <div className="absolute right-0 top-1/3 -z-10 h-[300px] w-[300px] rounded-full bg-gradient-to-br from-blue-500/25 to-cyan-500/20 opacity-50 blur-[80px]" />
        <div className="absolute left-0 bottom-1/4 -z-10 h-[250px] w-[350px] rounded-full bg-gradient-to-tr from-rose-500/20 to-orange-500/15 opacity-40 blur-[80px]" />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-6">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-2 text-sm font-medium text-primary backdrop-blur-sm">
                <Sparkles className="h-4 w-4" />
                <span>Productivity Reimagined</span>
              </div>

              {/* Headline */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1]">
                <span className="bg-gradient-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
                  Focus on what
                </span>
                <br />
                <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500 bg-clip-text text-transparent">
                  matters most
                </span>
              </h1>

              {/* Subheadline */}
              <p className="text-lg text-muted-foreground max-w-lg leading-relaxed">
                A beautifully crafted task management app that helps you stay organized,
                focused, and productive. No clutter, just clarity.
              </p>

              {/* Feature pills */}
              <div className="flex flex-wrap gap-3">
                {[
                  { icon: Zap, text: "Lightning fast" },
                  { icon: Shield, text: "Secure by design" },
                  { icon: Check, text: "Free to use" },
                ].map(({ icon: Icon, text }) => (
                  <div
                    key={text}
                    className="flex items-center gap-2 rounded-full bg-muted/50 px-4 py-2 text-sm"
                  >
                    <Icon className="h-4 w-4 text-primary" />
                    <span>{text}</span>
                  </div>
                ))}
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-2">
                <Button asChild size="lg" className="text-base px-8 h-12 rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 transition-all duration-300 border-0">
                  <Link href={isAuthenticated ? "/tasks" : "/register"}>
                    {isAuthenticated ? "Go to Tasks" : "Start for Free"}
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                {!isAuthenticated && (
                  <Button asChild variant="outline" size="lg" className="text-base px-8 h-12 rounded-full">
                    <Link href="/login">
                      Sign In
                    </Link>
                  </Button>
                )}
              </div>
            </div>

            {/* Right Content - App Preview */}
            <div className="relative hidden lg:block">
              <div className="relative">
                {/* Glow effect */}
                <div className="absolute -inset-4 bg-gradient-to-r from-violet-500/25 via-fuchsia-500/20 to-pink-500/25 rounded-2xl blur-2xl opacity-60" />

                {/* Mock App Window */}
                <div className="relative rounded-2xl border bg-card/80 backdrop-blur-xl shadow-2xl overflow-hidden">
                  {/* Window header */}
                  <div className="flex items-center gap-2 px-4 py-3 border-b bg-muted/30">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-500/80" />
                      <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                      <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    </div>
                    <div className="flex-1 text-center text-sm text-muted-foreground">My Tasks</div>
                  </div>

                  {/* Mock tasks */}
                  <div className="p-4 space-y-2.5">
                    {[
                      { title: "Review project proposal", done: true },
                      { title: "Schedule team meeting", done: true },
                      { title: "Update documentation", done: false },
                      { title: "Deploy to production", done: false },
                    ].map((task, i) => (
                      <div
                        key={i}
                        className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                          task.done
                            ? "bg-muted/30 opacity-60"
                            : "bg-muted/50"
                        }`}
                      >
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                          task.done
                            ? "border-primary bg-primary"
                            : "border-muted-foreground/30"
                        }`}>
                          {task.done && <Check className="w-3 h-3 text-primary-foreground" />}
                        </div>
                        <span className={task.done ? "line-through text-muted-foreground" : ""}>
                          {task.title}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Add task input */}
                  <div className="p-4 border-t">
                    <div className="flex items-center gap-2 p-3 rounded-xl bg-muted/30 text-muted-foreground">
                      <span className="text-lg">+</span>
                      <span className="text-sm">Add a new task...</span>
                    </div>
                  </div>
                </div>

                {/* Floating elements */}
                <div className="absolute -top-3 -right-3 bg-primary text-primary-foreground rounded-full p-2.5 shadow-lg animate-bounce">
                  <Check className="w-5 h-5" />
                </div>
                <div className="absolute -bottom-2 -left-2 bg-card border rounded-xl px-4 py-2 shadow-lg">
                  <div className="text-xs text-muted-foreground">Completed today</div>
                  <div className="text-lg font-bold text-primary">12 tasks</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section - Full Width */}
      <div className="border-t bg-muted/30 backdrop-blur-sm mt-[100px]">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 py-8">
            {[
              { icon: Users, value: "10K+", label: "Active Users" },
              { icon: CheckCircle, value: "50K+", label: "Tasks Completed" },
              { icon: Clock, value: "99.9%", label: "Uptime" },
              { icon: Zap, value: "<100ms", label: "Response Time" },
            ].map(({ icon: Icon, value, label }) => (
              <div key={label} className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-primary/10">
                  <Icon className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{value}</div>
                  <div className="text-sm text-muted-foreground">{label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
