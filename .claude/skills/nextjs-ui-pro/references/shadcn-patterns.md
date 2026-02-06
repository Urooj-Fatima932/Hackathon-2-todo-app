# shadcn/ui Patterns

## Installation & Setup

### Initialize shadcn/ui
```bash
npx shadcn@latest init
```

### Add Components
```bash
# Single component
npx shadcn@latest add button

# Multiple components
npx shadcn@latest add button card dialog

# All components
npx shadcn@latest add --all
```

### components.json Configuration
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

## The cn() Utility

Essential for conditional classes:

```tsx
// lib/utils.ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Usage Patterns

```tsx
import { cn } from "@/lib/utils"

// Basic conditional
<div className={cn("base-class", isActive && "active-class")} />

// With variants
<button className={cn(
  "rounded-md px-4 py-2",
  variant === "primary" && "bg-primary text-primary-foreground",
  variant === "secondary" && "bg-secondary text-secondary-foreground",
  disabled && "opacity-50 cursor-not-allowed"
)} />

// Merging with incoming className
function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("rounded-lg border p-4", className)} {...props} />
  )
}
```

## Button Component

```tsx
import { Button } from "@/components/ui/button"

// Variants
<Button variant="default">Default</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="default">Default</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Icon /></Button>

// With Icon
import { ArrowRight, Loader2 } from "lucide-react"

<Button>
  Continue <ArrowRight className="ml-2 h-4 w-4" />
</Button>

// Loading State
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Please wait
</Button>

// As Link
import Link from "next/link"

<Button asChild>
  <Link href="/dashboard">Dashboard</Link>
</Button>
```

## Card Component

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here.</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

// Horizontal Card
<Card className="flex">
  <div className="flex-shrink-0">
    <Image src="/image.jpg" width={200} height={200} alt="" />
  </div>
  <div>
    <CardHeader>
      <CardTitle>Title</CardTitle>
    </CardHeader>
    <CardContent>Content</CardContent>
  </div>
</Card>
```

## Dialog (Modal)

```tsx
"use client"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function ConfirmDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Open Dialog</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogDescription>
            This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button variant="destructive">Delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

## Sheet (Slide-over)

```tsx
"use client"

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"

export function MobileMenu() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left">
        <SheetHeader>
          <SheetTitle>Menu</SheetTitle>
        </SheetHeader>
        <nav className="mt-6 flex flex-col gap-4">
          <Link href="/">Home</Link>
          <Link href="/about">About</Link>
          <Link href="/contact">Contact</Link>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
```

## Dropdown Menu

```tsx
"use client"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function UserMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Settings</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="text-destructive">
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

## Tabs

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function FeatureTabs() {
  return (
    <Tabs defaultValue="features" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="features">Features</TabsTrigger>
        <TabsTrigger value="pricing">Pricing</TabsTrigger>
        <TabsTrigger value="faq">FAQ</TabsTrigger>
      </TabsList>
      <TabsContent value="features">
        <Card>
          <CardContent className="pt-6">Features content</CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="pricing">
        <Card>
          <CardContent className="pt-6">Pricing content</CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="faq">
        <Card>
          <CardContent className="pt-6">FAQ content</CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  )
}
```

## Avatar

```tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

<Avatar>
  <AvatarImage src="/avatar.jpg" alt="User" />
  <AvatarFallback>JD</AvatarFallback>
</Avatar>

// Avatar Group
<div className="flex -space-x-2">
  {users.map((user) => (
    <Avatar key={user.id} className="border-2 border-background">
      <AvatarImage src={user.avatar} alt={user.name} />
      <AvatarFallback>{user.initials}</AvatarFallback>
    </Avatar>
  ))}
</div>
```

## Badge

```tsx
import { Badge } from "@/components/ui/badge"

<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="outline">Outline</Badge>
<Badge variant="destructive">Destructive</Badge>

// Custom colors
<Badge className="bg-green-500 hover:bg-green-600">Success</Badge>
```

## Input with Label

```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    placeholder="name@example.com"
  />
</div>

// With error state
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    className="border-destructive"
    aria-invalid="true"
  />
  <p className="text-sm text-destructive">Please enter a valid email</p>
</div>
```

## Toast Notifications

```tsx
"use client"

import { useToast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"

export function ToastDemo() {
  const { toast } = useToast()

  return (
    <Button
      onClick={() => {
        toast({
          title: "Success!",
          description: "Your changes have been saved.",
        })
      }}
    >
      Show Toast
    </Button>
  )
}

// Destructive toast
toast({
  variant: "destructive",
  title: "Error",
  description: "Something went wrong.",
})

// With action
toast({
  title: "File deleted",
  description: "The file has been moved to trash.",
  action: (
    <ToastAction altText="Undo">Undo</ToastAction>
  ),
})
```

## Skeleton Loading

```tsx
import { Skeleton } from "@/components/ui/skeleton"

// Card skeleton
export function CardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-4 w-3/4" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-32 w-full" />
      </CardContent>
    </Card>
  )
}

// List skeleton
export function ListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-48" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
      ))}
    </div>
  )
}
```

## Separator

```tsx
import { Separator } from "@/components/ui/separator"

<div>
  <h4>Section 1</h4>
  <p>Content</p>
</div>
<Separator className="my-4" />
<div>
  <h4>Section 2</h4>
  <p>Content</p>
</div>

// Vertical separator
<div className="flex h-5 items-center gap-4">
  <span>Item 1</span>
  <Separator orientation="vertical" />
  <span>Item 2</span>
</div>
```

## Common Required Components

For landing pages, install these commonly used components:

```bash
npx shadcn@latest add button card badge avatar accordion separator tabs dialog sheet dropdown-menu input label textarea
```
