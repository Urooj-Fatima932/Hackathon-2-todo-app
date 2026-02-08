import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function CTA() {
  return (
    <section className="py-20 md:py-28 lg:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-primary to-primary/80 px-8 py-16 text-center shadow-2xl sm:px-16 md:py-20">
          {/* Content */}
          <div className="relative z-10 mx-auto max-w-3xl">
            <h2 className="mb-4 text-3xl font-bold text-primary-foreground sm:text-4xl md:text-5xl">
              Ready to get organized?
            </h2>
            <p className="mb-8 text-lg text-primary-foreground/90 sm:text-xl">
              Start managing your tasks today. No credit card required.
            </p>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="shadow-lg hover:shadow-xl transition-shadow"
            >
              <Link href="/tasks">
                Get Started Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>

          {/* Decorative elements */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden">
            <div className="absolute -top-20 -right-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
          </div>
        </div>
      </div>
    </section>
  );
}
