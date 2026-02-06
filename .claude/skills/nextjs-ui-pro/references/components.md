# Reusable Component Patterns

## Component Structure

```tsx
// components/ui/feature-card.tsx
import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  className?: string
}

export function FeatureCard({
  icon: Icon,
  title,
  description,
  className,
}: FeatureCardProps) {
  return (
    <div className={cn("rounded-lg border bg-card p-6", className)}>
      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
        <Icon className="h-6 w-6 text-primary" />
      </div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-muted-foreground">{description}</p>
    </div>
  )
}
```

## Section Header

```tsx
import { cn } from "@/lib/utils"

interface SectionHeaderProps {
  title: string
  description?: string
  align?: "left" | "center"
  className?: string
}

export function SectionHeader({
  title,
  description,
  align = "center",
  className,
}: SectionHeaderProps) {
  return (
    <div
      className={cn(
        "max-w-2xl",
        align === "center" && "mx-auto text-center",
        className
      )}
    >
      <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">{title}</h2>
      {description && (
        <p className="mt-4 text-lg text-muted-foreground">{description}</p>
      )}
    </div>
  )
}

// Usage
<SectionHeader
  title="Our Features"
  description="Everything you need to build amazing products."
  align="center"
/>
```

## Icon Button

```tsx
import { Button, ButtonProps } from "@/components/ui/button"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface IconButtonProps extends ButtonProps {
  icon: LucideIcon
  label: string
}

export function IconButton({
  icon: Icon,
  label,
  className,
  ...props
}: IconButtonProps) {
  return (
    <Button
      size="icon"
      className={cn("", className)}
      aria-label={label}
      {...props}
    >
      <Icon className="h-4 w-4" />
      <span className="sr-only">{label}</span>
    </Button>
  )
}

// Usage
import { Menu } from "lucide-react"
<IconButton icon={Menu} label="Open menu" variant="ghost" />
```

## Empty State

```tsx
import { LucideIcon } from "lucide-react"
import { Button } from "@/components/ui/button"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
        <Icon className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="mt-2 max-w-sm text-muted-foreground">{description}</p>
      {action && (
        <Button onClick={action.onClick} className="mt-6">
          {action.label}
        </Button>
      )}
    </div>
  )
}

// Usage
import { FileText } from "lucide-react"
<EmptyState
  icon={FileText}
  title="No documents"
  description="Get started by creating a new document."
  action={{ label: "Create Document", onClick: () => {} }}
/>
```

## Status Badge

```tsx
import { cn } from "@/lib/utils"

type Status = "success" | "warning" | "error" | "info" | "default"

interface StatusBadgeProps {
  status: Status
  label: string
}

const statusStyles: Record<Status, string> = {
  success: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  info: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  default: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        statusStyles[status]
      )}
    >
      {label}
    </span>
  )
}

// Usage
<StatusBadge status="success" label="Active" />
<StatusBadge status="error" label="Failed" />
```

## Avatar with Status

```tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface AvatarWithStatusProps {
  src?: string
  name: string
  status?: "online" | "offline" | "busy"
  size?: "sm" | "md" | "lg"
}

const sizeClasses = {
  sm: "h-8 w-8",
  md: "h-10 w-10",
  lg: "h-12 w-12",
}

const statusColors = {
  online: "bg-green-500",
  offline: "bg-gray-400",
  busy: "bg-red-500",
}

export function AvatarWithStatus({
  src,
  name,
  status,
  size = "md",
}: AvatarWithStatusProps) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()

  return (
    <div className="relative">
      <Avatar className={sizeClasses[size]}>
        <AvatarImage src={src} alt={name} />
        <AvatarFallback>{initials}</AvatarFallback>
      </Avatar>
      {status && (
        <span
          className={cn(
            "absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-background",
            statusColors[status]
          )}
        />
      )}
    </div>
  )
}
```

## Link Card

```tsx
import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"

interface LinkCardProps {
  href: string
  title: string
  description: string
  className?: string
}

export function LinkCard({ href, title, description, className }: LinkCardProps) {
  return (
    <Link
      href={href}
      className={cn(
        "group block rounded-lg border p-6 transition-colors hover:border-primary hover:bg-muted/50",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{title}</h3>
        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
      </div>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </Link>
  )
}
```

## Metric Card

```tsx
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  label: string
  value: string | number
  change?: {
    value: number
    trend: "up" | "down"
  }
  icon?: LucideIcon
}

export function MetricCard({ label, value, change, icon: Icon }: MetricCardProps) {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold">{value}</span>
        {change && (
          <span
            className={cn(
              "text-sm",
              change.trend === "up" ? "text-green-600" : "text-red-600"
            )}
          >
            {change.trend === "up" ? "+" : "-"}{Math.abs(change.value)}%
          </span>
        )}
      </div>
    </div>
  )
}
```

## Image with Fallback

```tsx
"use client"

import { useState } from "react"
import Image, { ImageProps } from "next/image"
import { cn } from "@/lib/utils"

interface ImageWithFallbackProps extends Omit<ImageProps, "onError"> {
  fallbackSrc?: string
}

export function ImageWithFallback({
  src,
  fallbackSrc = "/placeholder.png",
  alt,
  className,
  ...props
}: ImageWithFallbackProps) {
  const [error, setError] = useState(false)

  return (
    <Image
      src={error ? fallbackSrc : src}
      alt={alt}
      className={cn("", className)}
      onError={() => setError(true)}
      {...props}
    />
  )
}
```

## Tooltip Wrapper

```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface TooltipWrapperProps {
  children: React.ReactNode
  content: string
  side?: "top" | "right" | "bottom" | "left"
}

export function TooltipWrapper({
  children,
  content,
  side = "top",
}: TooltipWrapperProps) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent side={side}>
          <p>{content}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// Usage
<TooltipWrapper content="Edit this item">
  <Button variant="ghost" size="icon">
    <Pencil className="h-4 w-4" />
  </Button>
</TooltipWrapper>
```

## Confirm Dialog

```tsx
"use client"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

interface ConfirmDialogProps {
  trigger: React.ReactNode
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  variant?: "default" | "destructive"
}

export function ConfirmDialog({
  trigger,
  title,
  description,
  confirmLabel = "Continue",
  cancelLabel = "Cancel",
  onConfirm,
  variant = "default",
}: ConfirmDialogProps) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{trigger}</AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className={variant === "destructive" ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" : ""}
          >
            {confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

// Usage
<ConfirmDialog
  trigger={<Button variant="destructive">Delete</Button>}
  title="Are you sure?"
  description="This action cannot be undone."
  confirmLabel="Delete"
  onConfirm={() => handleDelete()}
  variant="destructive"
/>
```
