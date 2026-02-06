# Landing Page Sections

## Hero Section - Centered

```tsx
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"

export function HeroCentered() {
  return (
    <section className="relative py-20 md:py-32 lg:py-40">
      <div className="container mx-auto px-4 text-center">
        {/* Badge */}
        <div className="mb-6 inline-flex items-center rounded-full border px-4 py-1.5 text-sm">
          <span className="mr-2">🎉</span>
          <span>Announcing our latest feature</span>
        </div>

        {/* Headline */}
        <h1 className="mx-auto max-w-4xl text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
          Build amazing products{" "}
          <span className="text-primary">faster than ever</span>
        </h1>

        {/* Subheadline */}
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
          The modern platform for building beautiful, responsive websites.
          Start shipping today with our powerful tools.
        </p>

        {/* CTA Buttons */}
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Button size="lg" className="w-full sm:w-auto">
            Get Started Free
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
          <Button variant="outline" size="lg" className="w-full sm:w-auto">
            Watch Demo
          </Button>
        </div>

        {/* Social Proof */}
        <p className="mt-8 text-sm text-muted-foreground">
          Trusted by 10,000+ companies worldwide
        </p>
      </div>
    </section>
  )
}
```

## Hero Section - Split with Image

```tsx
import Image from "next/image"
import { Button } from "@/components/ui/button"

export function HeroSplit() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Content */}
          <div className="max-w-xl">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              The future of
              <span className="block text-primary">web development</span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground">
              Build faster, ship sooner. Our platform gives you everything
              you need to create stunning web applications.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Button size="lg">Start Building</Button>
              <Button variant="ghost" size="lg">
                Learn More →
              </Button>
            </div>
          </div>

          {/* Image */}
          <div className="relative aspect-square lg:aspect-[4/3]">
            <Image
              src="/hero-image.png"
              alt="Product screenshot"
              fill
              className="rounded-lg object-cover shadow-2xl"
              priority
            />
          </div>
        </div>
      </div>
    </section>
  )
}
```

## Features Grid - Icons

```tsx
import { Zap, Shield, Smartphone, Globe, Layers, Clock } from "lucide-react"

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Optimized for speed with edge deployment and caching.",
  },
  {
    icon: Shield,
    title: "Secure by Default",
    description: "Enterprise-grade security with automatic updates.",
  },
  {
    icon: Smartphone,
    title: "Mobile First",
    description: "Responsive design that works on any device.",
  },
  {
    icon: Globe,
    title: "Global CDN",
    description: "Content delivered from servers closest to your users.",
  },
  {
    icon: Layers,
    title: "Modern Stack",
    description: "Built with React, Next.js, and TypeScript.",
  },
  {
    icon: Clock,
    title: "Quick Setup",
    description: "Get started in minutes with our CLI tools.",
  },
]

export function FeaturesGrid() {
  return (
    <section className="py-16 md:py-24 bg-muted/50">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Powerful features to help you build better products faster.
          </p>
        </div>

        {/* Features Grid */}
        <div className="mx-auto mt-16 grid max-w-5xl gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div key={feature.title} className="relative rounded-lg border bg-background p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mt-4 text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Features - Alternating Layout

```tsx
import Image from "next/image"
import { Check } from "lucide-react"

const features = [
  {
    title: "Powerful Analytics",
    description: "Get insights into your business with real-time dashboards.",
    image: "/feature-1.png",
    points: ["Real-time data", "Custom reports", "Export to CSV"],
  },
  {
    title: "Team Collaboration",
    description: "Work together seamlessly with built-in tools.",
    image: "/feature-2.png",
    points: ["Shared workspaces", "Comments & mentions", "Version history"],
  },
]

export function FeaturesAlternating() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="space-y-24">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className={`grid items-center gap-12 lg:grid-cols-2 ${
                index % 2 === 1 ? "lg:flex-row-reverse" : ""
              }`}
            >
              {/* Content */}
              <div className={index % 2 === 1 ? "lg:order-2" : ""}>
                <h3 className="text-3xl font-bold">{feature.title}</h3>
                <p className="mt-4 text-lg text-muted-foreground">
                  {feature.description}
                </p>
                <ul className="mt-6 space-y-3">
                  {feature.points.map((point) => (
                    <li key={point} className="flex items-center gap-3">
                      <Check className="h-5 w-5 text-primary" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Image */}
              <div className={`relative aspect-video ${index % 2 === 1 ? "lg:order-1" : ""}`}>
                <Image
                  src={feature.image}
                  alt={feature.title}
                  fill
                  className="rounded-lg object-cover shadow-lg"
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Testimonials - Cards

```tsx
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const testimonials = [
  {
    quote: "This product has completely transformed how we work. Highly recommended!",
    author: "Sarah Johnson",
    role: "CEO at TechCorp",
    avatar: "/avatars/sarah.jpg",
  },
  {
    quote: "The best investment we've made this year. Our team productivity doubled.",
    author: "Michael Chen",
    role: "CTO at StartupXYZ",
    avatar: "/avatars/michael.jpg",
  },
  {
    quote: "Incredible support team and amazing features. We switched from competitors.",
    author: "Emily Davis",
    role: "Product Lead at Design Co",
    avatar: "/avatars/emily.jpg",
  },
]

export function Testimonials() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Loved by thousands
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            See what our customers are saying about us.
          </p>
        </div>

        <div className="mx-auto mt-16 grid max-w-6xl gap-8 md:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((testimonial) => (
            <Card key={testimonial.author}>
              <CardContent className="p-6">
                <p className="text-muted-foreground">"{testimonial.quote}"</p>
                <div className="mt-6 flex items-center gap-4">
                  <Avatar>
                    <AvatarImage src={testimonial.avatar} alt={testimonial.author} />
                    <AvatarFallback>
                      {testimonial.author.split(" ").map((n) => n[0]).join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold">{testimonial.author}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Pricing Section

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

const plans = [
  {
    name: "Starter",
    price: "$9",
    description: "Perfect for small projects",
    features: ["5 projects", "10GB storage", "Basic analytics", "Email support"],
    popular: false,
  },
  {
    name: "Pro",
    price: "$29",
    description: "For growing businesses",
    features: ["Unlimited projects", "100GB storage", "Advanced analytics", "Priority support", "Custom domain"],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For large organizations",
    features: ["Everything in Pro", "Unlimited storage", "Dedicated support", "SLA guarantee", "Custom integrations"],
    popular: false,
  },
]

export function Pricing() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Choose the plan that's right for you.
          </p>
        </div>

        <div className="mx-auto mt-16 grid max-w-5xl gap-8 lg:grid-cols-3">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={cn(
                "relative",
                plan.popular && "border-primary shadow-lg"
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-primary px-3 py-1 text-xs font-medium text-primary-foreground">
                    Most Popular
                  </span>
                </div>
              )}
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  {plan.price !== "Custom" && (
                    <span className="text-muted-foreground">/month</span>
                  )}
                </div>
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-3">
                      <Check className="h-4 w-4 text-primary" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  variant={plan.popular ? "default" : "outline"}
                >
                  Get Started
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

## CTA Section

```tsx
import { Button } from "@/components/ui/button"

export function CTASection() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="rounded-2xl bg-primary px-6 py-16 text-center text-primary-foreground md:px-12">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Ready to get started?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-primary-foreground/80">
            Join thousands of satisfied customers and start building today.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" variant="secondary">
              Start Free Trial
            </Button>
            <Button size="lg" variant="outline" className="border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10">
              Contact Sales
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
```

## FAQ Section

```tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const faqs = [
  {
    question: "How does the free trial work?",
    answer: "You get 14 days of full access to all features. No credit card required.",
  },
  {
    question: "Can I cancel anytime?",
    answer: "Yes, you can cancel your subscription at any time with no penalties.",
  },
  {
    question: "Do you offer refunds?",
    answer: "We offer a 30-day money-back guarantee for all paid plans.",
  },
  {
    question: "Is my data secure?",
    answer: "We use enterprise-grade encryption and follow industry best practices.",
  },
]

export function FAQ() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Frequently asked questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to know about our product.
          </p>
        </div>

        <div className="mx-auto mt-16 max-w-3xl">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent>{faq.answer}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  )
}
```

## Logo Cloud

```tsx
import Image from "next/image"

const logos = [
  { name: "Company 1", src: "/logos/company1.svg" },
  { name: "Company 2", src: "/logos/company2.svg" },
  { name: "Company 3", src: "/logos/company3.svg" },
  { name: "Company 4", src: "/logos/company4.svg" },
  { name: "Company 5", src: "/logos/company5.svg" },
]

export function LogoCloud() {
  return (
    <section className="py-12 md:py-16">
      <div className="container mx-auto px-4">
        <p className="text-center text-sm text-muted-foreground">
          Trusted by industry leaders
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-8 md:gap-12">
          {logos.map((logo) => (
            <Image
              key={logo.name}
              src={logo.src}
              alt={logo.name}
              width={120}
              height={40}
              className="h-8 w-auto opacity-60 grayscale transition-all hover:opacity-100 hover:grayscale-0"
            />
          ))}
        </div>
      </div>
    </section>
  )
}
```

## Stats Section

```tsx
const stats = [
  { value: "10K+", label: "Active Users" },
  { value: "99.9%", label: "Uptime" },
  { value: "24/7", label: "Support" },
  { value: "150+", label: "Countries" },
]

export function Stats() {
  return (
    <section className="border-y bg-muted/50 py-12 md:py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-3xl font-bold md:text-4xl">{stat.value}</p>
              <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```
