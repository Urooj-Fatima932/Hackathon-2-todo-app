# Generate CRUD for Resource

Complete template for generating CRUD operations for a resource.

## Usage

Replace `{resource}` with your resource name (e.g., `post`, `user`, `product`).
Replace `{Resource}` with PascalCase (e.g., `Post`, `User`, `Product`).

---

## 1. Types

### types/{resource}.ts
```typescript
export interface {Resource} {
  id: string
  // Add your fields
  createdAt: string
  updatedAt: string
}

export interface Create{Resource}Input {
  // Fields for creation (without id, timestamps)
}

export interface Update{Resource}Input {
  // Partial fields for update
}
```

---

## 2. Validation Schema

### lib/validations/{resource}.ts
```typescript
import { z } from "zod"

export const create{Resource}Schema = z.object({
  // Define validation rules
  // name: z.string().min(1, "Name is required").max(100),
})

export const update{Resource}Schema = create{Resource}Schema.partial()

export type Create{Resource}Input = z.infer<typeof create{Resource}Schema>
export type Update{Resource}Input = z.infer<typeof update{Resource}Schema>
```

---

## 3. API Functions

### lib/api/{resource}s.ts
```typescript
import { api, authApi } from "./client"
import type { {Resource}, Create{Resource}Input, Update{Resource}Input } from "@/types/{resource}"

const BASE = "/api/v1/{resource}s"

// List (public, cached)
export async function get{Resource}s() {
  return api<{Resource}[]>(BASE, {
    next: { revalidate: 60, tags: ["{resource}s"] },
  })
}

// Get one (public, cached)
export async function get{Resource}(id: string) {
  return api<{Resource}>(`${BASE}/${id}`, {
    next: { revalidate: 60, tags: ["{resource}s", `{resource}-${id}`] },
  })
}

// Create (authenticated)
export async function create{Resource}(data: Create{Resource}Input) {
  return authApi<{Resource}>(BASE, {
    method: "POST",
    body: data,
  })
}

// Update (authenticated)
export async function update{Resource}(id: string, data: Update{Resource}Input) {
  return authApi<{Resource}>(`${BASE}/${id}`, {
    method: "PATCH",
    body: data,
  })
}

// Delete (authenticated)
export async function delete{Resource}(id: string) {
  return authApi<void>(`${BASE}/${id}`, {
    method: "DELETE",
  })
}
```

---

## 4. Server Actions

### actions/{resource}s.ts
```typescript
"use server"

import { revalidateTag } from "next/cache"
import { redirect } from "next/navigation"
import { create{Resource}Schema, update{Resource}Schema } from "@/lib/validations/{resource}"
import { create{Resource}, update{Resource}, delete{Resource} } from "@/lib/api/{resource}s"
import { ApiError } from "@/lib/api/client"

export type {Resource}ActionState = {
  errors?: Record<string, string[]>
  error?: string
  success?: boolean
}

export async function create{Resource}Action(
  _prevState: {Resource}ActionState,
  formData: FormData
): Promise<{Resource}ActionState> {
  const rawData = Object.fromEntries(formData.entries())
  const validated = create{Resource}Schema.safeParse(rawData)

  if (!validated.success) {
    return { errors: validated.error.flatten().fieldErrors }
  }

  try {
    const {resource} = await create{Resource}(validated.data)
    revalidateTag("{resource}s")
    redirect(`/{resource}s/${({resource} as any).id}`)
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: error.detail }
    }
    return { error: "Failed to create {resource}" }
  }
}

export async function update{Resource}Action(
  id: string,
  _prevState: {Resource}ActionState,
  formData: FormData
): Promise<{Resource}ActionState> {
  const rawData = Object.fromEntries(formData.entries())
  const validated = update{Resource}Schema.safeParse(rawData)

  if (!validated.success) {
    return { errors: validated.error.flatten().fieldErrors }
  }

  try {
    await update{Resource}(id, validated.data)
    revalidateTag("{resource}s")
    revalidateTag(`{resource}-${id}`)
    return { success: true }
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: error.detail }
    }
    return { error: "Failed to update {resource}" }
  }
}

export async function delete{Resource}Action(id: string) {
  try {
    await delete{Resource}(id)
    revalidateTag("{resource}s")
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: error.detail }
    }
    return { error: "Failed to delete {resource}" }
  }
  redirect("/{resource}s")
}
```

---

## 5. Components

### components/{resource}s/{resource}-form.tsx
```typescript
"use client"

import { useActionState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

import {
  create{Resource}Schema,
  Create{Resource}Input,
} from "@/lib/validations/{resource}"
import { create{Resource}Action, {Resource}ActionState } from "@/actions/{resource}s"

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function {Resource}Form() {
  const [state, formAction, isPending] = useActionState<{Resource}ActionState, FormData>(
    create{Resource}Action,
    {}
  )

  const form = useForm<Create{Resource}Input>({
    resolver: zodResolver(create{Resource}Schema),
    defaultValues: {
      // Set default values
    },
  })

  return (
    <Form {...form}>
      <form action={formAction} className="space-y-6">
        {/* Add form fields */}
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {state.error && (
          <p className="text-sm text-red-500">{state.error}</p>
        )}

        <Button type="submit" disabled={isPending}>
          {isPending ? "Creating..." : "Create"}
        </Button>
      </form>
    </Form>
  )
}
```

### components/{resource}s/{resource}-card.tsx
```typescript
import Link from "next/link"
import type { {Resource} } from "@/types/{resource}"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

interface {Resource}CardProps {
  {resource}: {Resource}
}

export function {Resource}Card({ {resource} }: {Resource}CardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <Link href={`/{resource}s/${({resource} as any).id}`}>
            {{resource}.name}
          </Link>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Content */}
      </CardContent>
    </Card>
  )
}
```

### components/{resource}s/{resource}-list.tsx
```typescript
import type { {Resource} } from "@/types/{resource}"
import { {Resource}Card } from "./{resource}-card"

interface {Resource}ListProps {
  {resource}s: {Resource}[]
}

export function {Resource}List({ {resource}s }: {Resource}ListProps) {
  if ({resource}s.length === 0) {
    return (
      <p className="text-muted-foreground text-center py-8">
        No {resource}s found.
      </p>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {{resource}s.map(({resource}) => (
        <{Resource}Card key={({resource} as any).id} {resource}={{resource}} />
      ))}
    </div>
  )
}
```

### components/{resource}s/delete-{resource}-button.tsx
```typescript
"use client"

import { useTransition } from "react"
import { Trash2 } from "lucide-react"
import { delete{Resource}Action } from "@/actions/{resource}s"
import { Button } from "@/components/ui/button"
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

interface Delete{Resource}ButtonProps {
  id: string
}

export function Delete{Resource}Button({ id }: Delete{Resource}ButtonProps) {
  const [isPending, startTransition] = useTransition()

  const handleDelete = () => {
    startTransition(() => {
      delete{Resource}Action(id)
    })
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive" size="icon">
          <Trash2 className="h-4 w-4" />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete {Resource}?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete} disabled={isPending}>
            {isPending ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

---

## 6. Pages

### app/{resource}s/page.tsx
```typescript
import { Metadata } from "next"
import Link from "next/link"
import { get{Resource}s } from "@/lib/api/{resource}s"
import { {Resource}List } from "@/components/{resource}s/{resource}-list"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export const metadata: Metadata = {
  title: "{Resource}s",
}

export default async function {Resource}sPage() {
  const {resource}s = await get{Resource}s()

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">{Resource}s</h1>
        <Button asChild>
          <Link href="/{resource}s/new">
            <Plus className="h-4 w-4 mr-2" />
            New {Resource}
          </Link>
        </Button>
      </div>
      <{Resource}List {resource}s={{resource}s} />
    </div>
  )
}
```

### app/{resource}s/new/page.tsx
```typescript
import { Metadata } from "next"
import { {Resource}Form } from "@/components/{resource}s/{resource}-form"

export const metadata: Metadata = {
  title: "New {Resource}",
}

export default function New{Resource}Page() {
  return (
    <div className="container py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Create {Resource}</h1>
      <{Resource}Form />
    </div>
  )
}
```

### app/{resource}s/[id]/page.tsx
```typescript
import { Metadata } from "next"
import { notFound } from "next/navigation"
import { get{Resource} } from "@/lib/api/{resource}s"

interface PageProps {
  params: Promise<{ id: string }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params
  const {resource} = await get{Resource}(id).catch(() => null)
  return { title: {resource}?.name || "{Resource}" }
}

export default async function {Resource}Page({ params }: PageProps) {
  const { id } = await params
  const {resource} = await get{Resource}(id).catch(() => null)

  if (!{resource}) notFound()

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-6">{{resource}.name}</h1>
      {/* Content */}
    </div>
  )
}
```
