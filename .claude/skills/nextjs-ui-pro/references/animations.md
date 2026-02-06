# Animations

## CSS Transitions

```tsx
// Basic transition
<div className="transition-all duration-300 ease-in-out hover:scale-105">
  Smooth scale on hover
</div>

// Specific property transitions
<button className="transition-colors duration-200 hover:bg-primary/90">
  Color transition
</button>

<div className="transition-opacity duration-300 opacity-0 group-hover:opacity-100">
  Fade in on parent hover
</div>

// Transform transitions
<div className="transition-transform duration-300 hover:-translate-y-1">
  Lift up on hover
</div>
```

## Tailwind Animation Classes

```tsx
// Built-in animations
<div className="animate-spin">Spinning</div>
<div className="animate-ping">Ping effect</div>
<div className="animate-pulse">Pulsing</div>
<div className="animate-bounce">Bouncing</div>

// Loading spinner
<svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24">
  <circle
    className="opacity-25"
    cx="12"
    cy="12"
    r="10"
    stroke="currentColor"
    strokeWidth="4"
    fill="none"
  />
  <path
    className="opacity-75"
    fill="currentColor"
    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
  />
</svg>
```

## Custom CSS Animations

```css
/* globals.css */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}

.animate-scale-in {
  animation: scale-in 0.2s ease-out;
}
```

```tsx
// Usage
<div className="animate-fade-in">Fades in</div>
<div className="animate-slide-up">Slides up</div>
```

## Framer Motion

### Installation
```bash
npm install framer-motion
```

### Basic Animations

```tsx
"use client"

import { motion } from "framer-motion"

// Fade in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>
  Fade in content
</motion.div>

// Slide up
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4 }}
>
  Slide up content
</motion.div>

// Scale
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.2 }}
>
  Scale in content
</motion.div>
```

### Scroll Animations

```tsx
"use client"

import { motion } from "framer-motion"

export function ScrollFadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  )
}

// Usage
<ScrollFadeIn>
  <FeatureCard />
</ScrollFadeIn>
```

### Staggered Children

```tsx
"use client"

import { motion } from "framer-motion"

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4 },
  },
}

export function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      className="space-y-4"
    >
      {items.map((item) => (
        <motion.li key={item} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### Hover Animations

```tsx
"use client"

import { motion } from "framer-motion"

export function AnimatedCard({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className="rounded-lg border bg-card p-6"
    >
      {children}
    </motion.div>
  )
}
```

### Page Transitions

```tsx
"use client"

import { motion, AnimatePresence } from "framer-motion"
import { usePathname } from "next/navigation"

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
}

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Animated Counter

```tsx
"use client"

import { useEffect, useState } from "react"
import { motion, useSpring, useTransform } from "framer-motion"

export function AnimatedCounter({ value }: { value: number }) {
  const spring = useSpring(0, { stiffness: 100, damping: 30 })
  const display = useTransform(spring, (current) => Math.round(current))
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    spring.set(value)
  }, [spring, value])

  useEffect(() => {
    return display.on("change", (latest) => {
      setDisplayValue(latest)
    })
  }, [display])

  return <span>{displayValue.toLocaleString()}</span>
}

// Usage
<AnimatedCounter value={10000} />
```

### Animated Text

```tsx
"use client"

import { motion } from "framer-motion"

export function AnimatedText({ text }: { text: string }) {
  const words = text.split(" ")

  return (
    <motion.p
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      className="text-4xl font-bold"
    >
      {words.map((word, i) => (
        <motion.span
          key={i}
          className="inline-block mr-2"
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: {
              opacity: 1,
              y: 0,
              transition: { delay: i * 0.1 },
            },
          }}
        >
          {word}
        </motion.span>
      ))}
    </motion.p>
  )
}
```

## Intersection Observer (No Library)

```tsx
"use client"

import { useEffect, useRef, useState } from "react"

export function FadeInOnScroll({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ${
        isVisible
          ? "opacity-100 translate-y-0"
          : "opacity-0 translate-y-8"
      }`}
    >
      {children}
    </div>
  )
}
```

## Loading States

```tsx
// Skeleton loading
import { Skeleton } from "@/components/ui/skeleton"

export function CardSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
    </div>
  )
}

// Spinner button
import { Loader2 } from "lucide-react"

<Button disabled={isLoading}>
  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {isLoading ? "Loading..." : "Submit"}
</Button>
```
