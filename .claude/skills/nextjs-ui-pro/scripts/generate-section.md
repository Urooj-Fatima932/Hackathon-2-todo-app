# Generate Landing Page Sections

Templates for common landing page sections using shadcn/ui and Tailwind CSS.

---

## Hero Section

### Simple Centered Hero

```tsx
// components/sections/hero.tsx
import Link from "next/link"
import { Button } from "@/components/ui/button"

export function Hero() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center space-y-4 text-center">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl">
              Build something amazing
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
              Create beautiful, modern web applications with our powerful platform.
              Start building today.
            </p>
          </div>
          <div className="space-x-4">
            <Button asChild size="lg">
              <Link href="/signup">Get Started</Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link href="/demo">View Demo</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
```

### Hero with Image

```tsx
// components/sections/hero-with-image.tsx
import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export function HeroWithImage() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
          <div className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl">
              Build faster with our platform
            </h1>
            <p className="max-w-[600px] text-gray-500 md:text-xl dark:text-gray-400">
              Everything you need to build modern web applications.
              Designed for developers who want to ship fast.
            </p>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Button asChild size="lg">
                <Link href="/signup">Get Started Free</Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/docs">Documentation</Link>
              </Button>
            </div>
          </div>
          <div className="relative aspect-video overflow-hidden rounded-xl">
            <Image
              src="/hero-image.png"
              alt="Hero"
              fill
              className="object-cover"
              priority
            />
          </div>
        </div>
      </div>
    </section>
  )
}
```

---

## Features Section

### Feature Grid (3 columns)

```tsx
// components/sections/features.tsx
import { Zap, Shield, Globe } from "lucide-react"

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Built for speed with optimized performance at every level.",
  },
  {
    icon: Shield,
    title: "Secure by Default",
    description: "Enterprise-grade security built into the core architecture.",
  },
  {
    icon: Globe,
    title: "Global Scale",
    description: "Deploy worldwide with our global edge network.",
  },
]

export function Features() {
  return (
    <section className="py-20 md:py-32 bg-gray-50 dark:bg-gray-900">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Features
          </h2>
          <p className="mt-4 text-gray-500 md:text-xl dark:text-gray-400">
            Everything you need to build amazing products
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="flex flex-col items-center text-center p-6"
            >
              <div className="rounded-full bg-primary/10 p-3 mb-4">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-500 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

### Feature Cards

```tsx
// components/sections/feature-cards.tsx
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Code, Palette, Rocket, Users } from "lucide-react"

const features = [
  {
    icon: Code,
    title: "Developer First",
    description: "Built by developers, for developers. Clean APIs and great DX.",
  },
  {
    icon: Palette,
    title: "Beautiful Design",
    description: "Stunning components that look great out of the box.",
  },
  {
    icon: Rocket,
    title: "Ship Faster",
    description: "Go from idea to production in record time.",
  },
  {
    icon: Users,
    title: "Team Collaboration",
    description: "Built-in tools for seamless team collaboration.",
  },
]

export function FeatureCards() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
            Why Choose Us
          </h2>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title}>
              <CardHeader>
                <feature.icon className="h-10 w-10 text-primary mb-2" />
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
```

---

## Pricing Section

```tsx
// components/sections/pricing.tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check } from "lucide-react"

const plans = [
  {
    name: "Starter",
    price: "$9",
    description: "Perfect for small projects",
    features: ["5 Projects", "10GB Storage", "Basic Support", "API Access"],
  },
  {
    name: "Pro",
    price: "$29",
    description: "For growing teams",
    features: ["Unlimited Projects", "100GB Storage", "Priority Support", "API Access", "Advanced Analytics"],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$99",
    description: "For large organizations",
    features: ["Unlimited Everything", "Dedicated Support", "Custom Integrations", "SLA", "SSO"],
  },
]

export function Pricing() {
  return (
    <section className="py-20 md:py-32">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Simple Pricing
          </h2>
          <p className="mt-4 text-gray-500 md:text-xl dark:text-gray-400">
            Choose the plan that works for you
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <Card key={plan.name} className={plan.popular ? "border-primary shadow-lg" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{plan.name}</CardTitle>
                  {plan.popular && <Badge>Popular</Badge>}
                </div>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold mb-4">
                  {plan.price}
                  <span className="text-lg font-normal text-gray-500">/mo</span>
                </div>
                <ul className="space-y-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center">
                      <Check className="h-4 w-4 text-primary mr-2" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
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

---

## Testimonials Section

```tsx
// components/sections/testimonials.tsx
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const testimonials = [
  {
    quote: "This platform has transformed how we build products. Highly recommended!",
    author: "Sarah Johnson",
    role: "CTO at TechCorp",
    avatar: "/avatars/sarah.jpg",
  },
  {
    quote: "The best developer experience I've ever had. Our team ships 2x faster now.",
    author: "Michael Chen",
    role: "Lead Developer at StartupX",
    avatar: "/avatars/michael.jpg",
  },
  {
    quote: "Finally, a tool that just works. No more fighting with configurations.",
    author: "Emily Davis",
    role: "Founder at DevStudio",
    avatar: "/avatars/emily.jpg",
  },
]

export function Testimonials() {
  return (
    <section className="py-20 md:py-32 bg-gray-50 dark:bg-gray-900">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
            Loved by Developers
          </h2>
        </div>
        <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
          {testimonials.map((testimonial) => (
            <Card key={testimonial.author}>
              <CardContent className="pt-6">
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center">
                  <Avatar className="h-10 w-10 mr-3">
                    <AvatarImage src={testimonial.avatar} />
                    <AvatarFallback>{testimonial.author[0]}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold">{testimonial.author}</p>
                    <p className="text-sm text-gray-500">{testimonial.role}</p>
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

---

## CTA Section

```tsx
// components/sections/cta.tsx
import Link from "next/link"
import { Button } from "@/components/ui/button"

export function CTA() {
  return (
    <section className="py-20 md:py-32 bg-primary text-primary-foreground">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center text-center space-y-4">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Ready to get started?
          </h2>
          <p className="max-w-[600px] text-primary-foreground/80 md:text-xl">
            Join thousands of developers building amazing products.
          </p>
          <div className="flex flex-col gap-2 min-[400px]:flex-row">
            <Button size="lg" variant="secondary" asChild>
              <Link href="/signup">Start Free Trial</Link>
            </Button>
            <Button size="lg" variant="outline" className="bg-transparent" asChild>
              <Link href="/contact">Contact Sales</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
```

---

## Footer

```tsx
// components/sections/footer.tsx
import Link from "next/link"

const footerLinks = {
  Product: ["Features", "Pricing", "Changelog", "Docs"],
  Company: ["About", "Blog", "Careers", "Press"],
  Legal: ["Privacy", "Terms", "Security"],
  Social: ["Twitter", "GitHub", "Discord"],
}

export function Footer() {
  return (
    <footer className="border-t py-12">
      <div className="container px-4 md:px-6">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link href="/" className="text-xl font-bold">
              YourBrand
            </Link>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Building the future of web development.
            </p>
          </div>
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-semibold mb-3">{category}</h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link}>
                    <Link
                      href={`/${link.toLowerCase()}`}
                      className="text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                    >
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 pt-8 border-t text-center text-sm text-gray-500">
          © {new Date().getFullYear()} YourBrand. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
```

---

## Navbar

```tsx
// components/sections/navbar.tsx
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="text-xl font-bold">
          YourBrand
        </Link>
        <nav className="hidden md:flex items-center gap-6">
          <Link href="/features" className="text-sm font-medium hover:underline">
            Features
          </Link>
          <Link href="/pricing" className="text-sm font-medium hover:underline">
            Pricing
          </Link>
          <Link href="/docs" className="text-sm font-medium hover:underline">
            Docs
          </Link>
        </nav>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button variant="ghost" asChild>
            <Link href="/login">Login</Link>
          </Button>
          <Button asChild>
            <Link href="/signup">Sign Up</Link>
          </Button>
        </div>
      </div>
    </header>
  )
}
```
