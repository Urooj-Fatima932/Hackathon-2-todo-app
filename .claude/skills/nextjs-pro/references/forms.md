# Forms with react-hook-form + zod

## Installation

```bash
npm install react-hook-form @hookform/resolvers zod
npm install @radix-ui/react-slot  # For shadcn Form
npx shadcn@latest add form input button label
```

## Zod Schemas

```tsx
// lib/validations/post.ts
import { z } from "zod"

export const createPostSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(100, "Title must be less than 100 characters"),
  content: z
    .string()
    .min(10, "Content must be at least 10 characters")
    .max(10000, "Content must be less than 10000 characters"),
  published: z.boolean().default(false),
  tags: z.array(z.string()).optional(),
})

export const updatePostSchema = createPostSchema.partial()

export type CreatePostInput = z.infer<typeof createPostSchema>
export type UpdatePostInput = z.infer<typeof updatePostSchema>
```

## Basic Form with Server Action

```tsx
// components/create-post-form.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useTransition } from "react"
import { useRouter } from "next/navigation"

import { createPostSchema, CreatePostInput } from "@/lib/validations/post"
import { createPost } from "@/actions/posts"

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"

export function CreatePostForm() {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  const form = useForm<CreatePostInput>({
    resolver: zodResolver(createPostSchema),
    defaultValues: {
      title: "",
      content: "",
      published: false,
    },
  })

  function onSubmit(data: CreatePostInput) {
    startTransition(async () => {
      const formData = new FormData()
      formData.append("title", data.title)
      formData.append("content", data.content)
      formData.append("published", String(data.published))

      const result = await createPost(formData)

      if (result?.error) {
        form.setError("root", { message: result.error })
        return
      }

      router.push("/posts")
      router.refresh()
    })
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input placeholder="Post title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="content"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Content</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Write your post..."
                  rows={10}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {form.formState.errors.root && (
          <p className="text-sm text-red-500">
            {form.formState.errors.root.message}
          </p>
        )}

        <Button type="submit" disabled={isPending}>
          {isPending ? "Creating..." : "Create Post"}
        </Button>
      </form>
    </Form>
  )
}
```

## Server Action with Validation

```tsx
// actions/posts.ts
"use server"

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import { createPostSchema } from "@/lib/validations/post"

export async function createPost(formData: FormData) {
  const rawData = {
    title: formData.get("title"),
    content: formData.get("content"),
    published: formData.get("published") === "true",
  }

  const validated = createPostSchema.safeParse(rawData)

  if (!validated.success) {
    return {
      error: "Validation failed",
      fieldErrors: validated.error.flatten().fieldErrors,
    }
  }

  try {
    await db.post.create({ data: validated.data })
    revalidatePath("/posts")
  } catch (error) {
    return { error: "Failed to create post" }
  }

  redirect("/posts")
}
```

## Edit Form with Default Values

```tsx
// components/edit-post-form.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { updatePostSchema, UpdatePostInput } from "@/lib/validations/post"
import { updatePost } from "@/actions/posts"

interface EditPostFormProps {
  post: {
    id: string
    title: string
    content: string
    published: boolean
  }
}

export function EditPostForm({ post }: EditPostFormProps) {
  const form = useForm<UpdatePostInput>({
    resolver: zodResolver(updatePostSchema),
    defaultValues: {
      title: post.title,
      content: post.content,
      published: post.published,
    },
  })

  // ... rest similar to create form
}
```

## Complex Schema Examples

### User Registration

```tsx
// lib/validations/auth.ts
import { z } from "zod"

export const registerSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain an uppercase letter")
      .regex(/[0-9]/, "Password must contain a number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

export type RegisterInput = z.infer<typeof registerSchema>
```

### Profile Settings

```tsx
// lib/validations/profile.ts
import { z } from "zod"

export const profileSchema = z.object({
  name: z.string().min(2).max(50),
  bio: z.string().max(500).optional(),
  website: z.string().url("Invalid URL").optional().or(z.literal("")),
  twitter: z
    .string()
    .regex(/^@?[\w]+$/, "Invalid Twitter handle")
    .optional()
    .or(z.literal("")),
  avatar: z
    .instanceof(File)
    .refine((file) => file.size < 5 * 1024 * 1024, "Max 5MB")
    .refine(
      (file) => ["image/jpeg", "image/png"].includes(file.type),
      "Only JPG/PNG allowed"
    )
    .optional(),
})
```

## Select and Checkbox Fields

```tsx
// components/settings-form.tsx
"use client"

import { useForm } from "react-hook-form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"

const settingsSchema = z.object({
  theme: z.enum(["light", "dark", "system"]),
  language: z.string(),
  notifications: z.object({
    email: z.boolean(),
    push: z.boolean(),
    sms: z.boolean(),
  }),
})

export function SettingsForm() {
  const form = useForm<z.infer<typeof settingsSchema>>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      theme: "system",
      language: "en",
      notifications: { email: true, push: true, sms: false },
    },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {/* Select */}
        <FormField
          control={form.control}
          name="theme"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Theme</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Checkbox */}
        <FormField
          control={form.control}
          name="notifications.email"
          render={({ field }) => (
            <FormItem className="flex items-center space-x-2">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <FormLabel>Email notifications</FormLabel>
            </FormItem>
          )}
        />
      </form>
    </Form>
  )
}
```

## Dynamic Fields (Array)

```tsx
// components/tags-form.tsx
"use client"

import { useFieldArray, useForm } from "react-hook-form"
import { Plus, X } from "lucide-react"

const schema = z.object({
  tags: z.array(z.object({ value: z.string().min(1) })).min(1).max(5),
})

export function TagsForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { tags: [{ value: "" }] },
  })

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "tags",
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {fields.map((field, index) => (
          <div key={field.id} className="flex gap-2">
            <FormField
              control={form.control}
              name={`tags.${index}.value`}
              render={({ field }) => (
                <FormItem className="flex-1">
                  <FormControl>
                    <Input {...field} placeholder="Tag" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {fields.length > 1 && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => remove(index)}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        ))}

        {fields.length < 5 && (
          <Button
            type="button"
            variant="outline"
            onClick={() => append({ value: "" })}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Tag
          </Button>
        )}
      </form>
    </Form>
  )
}
```

## File Upload

```tsx
// components/avatar-form.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"]

const avatarSchema = z.object({
  avatar: z
    .instanceof(FileList)
    .refine((files) => files.length > 0, "Avatar is required")
    .refine((files) => files[0]?.size <= MAX_FILE_SIZE, "Max file size is 5MB")
    .refine(
      (files) => ACCEPTED_TYPES.includes(files[0]?.type),
      "Only JPG, PNG, WEBP allowed"
    ),
})

export function AvatarForm() {
  const form = useForm<z.infer<typeof avatarSchema>>({
    resolver: zodResolver(avatarSchema),
  })

  async function onSubmit(data: z.infer<typeof avatarSchema>) {
    const formData = new FormData()
    formData.append("avatar", data.avatar[0])

    await uploadAvatar(formData)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="avatar"
          render={({ field: { onChange, value, ...field } }) => (
            <FormItem>
              <FormLabel>Avatar</FormLabel>
              <FormControl>
                <Input
                  type="file"
                  accept={ACCEPTED_TYPES.join(",")}
                  onChange={(e) => onChange(e.target.files)}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Upload</Button>
      </form>
    </Form>
  )
}
```

## Form with API Error Handling

```tsx
"use client"

export function CreatePostForm() {
  const form = useForm<CreatePostInput>({
    resolver: zodResolver(createPostSchema),
  })

  async function onSubmit(data: CreatePostInput) {
    try {
      const result = await createPost(data)

      if (!result.success) {
        // Set field-level errors from server
        if (result.fieldErrors) {
          Object.entries(result.fieldErrors).forEach(([field, errors]) => {
            form.setError(field as any, {
              type: "server",
              message: errors[0],
            })
          })
        }

        // Set form-level error
        if (result.error) {
          form.setError("root", { message: result.error })
        }
        return
      }

      // Success
      router.push("/posts")
    } catch (error) {
      form.setError("root", { message: "Something went wrong" })
    }
  }

  return (
    <Form {...form}>
      {/* ... form fields ... */}

      {form.formState.errors.root && (
        <div className="text-sm text-red-500 bg-red-50 p-3 rounded">
          {form.formState.errors.root.message}
        </div>
      )}
    </Form>
  )
}
```

## Shared Schema Between Frontend and Backend

```tsx
// lib/validations/shared.ts
// This file can be shared with FastAPI via code generation

import { z } from "zod"

export const postSchema = z.object({
  id: z.string().optional(),
  title: z.string().min(1).max(100),
  content: z.string().min(10),
  published: z.boolean().default(false),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
})

export const createPostSchema = postSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
})

export const updatePostSchema = createPostSchema.partial()

export type Post = z.infer<typeof postSchema>
export type CreatePost = z.infer<typeof createPostSchema>
export type UpdatePost = z.infer<typeof updatePostSchema>
```
