# Server Actions

## Basic Server Action

```tsx
// actions/posts.ts
"use server"

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string
  const content = formData.get("content") as string

  // Create post in database or API
  await db.post.create({ data: { title, content } })

  // Revalidate the posts page
  revalidatePath("/posts")
}
```

## With Zod Validation

```tsx
// actions/posts.ts
"use server"

import { z } from "zod"
import { revalidatePath } from "next/cache"

const createPostSchema = z.object({
  title: z.string().min(1, "Title is required").max(100),
  content: z.string().min(1, "Content is required"),
})

export type CreatePostState = {
  errors?: {
    title?: string[]
    content?: string[]
    _form?: string[]
  }
  success?: boolean
}

export async function createPost(
  prevState: CreatePostState,
  formData: FormData
): Promise<CreatePostState> {
  const validated = createPostSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  })

  if (!validated.success) {
    return {
      errors: validated.error.flatten().fieldErrors,
    }
  }

  try {
    await db.post.create({ data: validated.data })
    revalidatePath("/posts")
    return { success: true }
  } catch (error) {
    return {
      errors: { _form: ["Failed to create post"] },
    }
  }
}
```

## Using Actions in Forms

### Basic Form

```tsx
// app/posts/new/page.tsx
import { createPost } from "@/actions/posts"

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  )
}
```

### With useActionState

```tsx
// components/create-post-form.tsx
"use client"

import { useActionState } from "react"
import { createPost, CreatePostState } from "@/actions/posts"

const initialState: CreatePostState = {}

export function CreatePostForm() {
  const [state, formAction, pending] = useActionState(createPost, initialState)

  return (
    <form action={formAction}>
      <div>
        <input name="title" placeholder="Title" />
        {state.errors?.title && (
          <p className="text-red-500">{state.errors.title[0]}</p>
        )}
      </div>

      <div>
        <textarea name="content" placeholder="Content" />
        {state.errors?.content && (
          <p className="text-red-500">{state.errors.content[0]}</p>
        )}
      </div>

      {state.errors?._form && (
        <p className="text-red-500">{state.errors._form[0]}</p>
      )}

      {state.success && (
        <p className="text-green-500">Post created!</p>
      )}

      <button type="submit" disabled={pending}>
        {pending ? "Creating..." : "Create Post"}
      </button>
    </form>
  )
}
```

## Revalidation

### Revalidate Path

```tsx
"use server"

import { revalidatePath } from "next/cache"

export async function createPost(formData: FormData) {
  await db.post.create({ ... })

  // Revalidate specific path
  revalidatePath("/posts")

  // Revalidate with layout
  revalidatePath("/posts", "layout")

  // Revalidate dynamic route
  revalidatePath(`/posts/${slug}`)
}
```

### Revalidate Tag

```tsx
"use server"

import { revalidateTag } from "next/cache"

export async function createPost(formData: FormData) {
  await db.post.create({ ... })

  // Revalidate all fetches with this tag
  revalidateTag("posts")
}

// In data fetching
const posts = await fetch("/api/posts", {
  next: { tags: ["posts"] }
})
```

## Redirect After Action

```tsx
"use server"

import { redirect } from "next/navigation"
import { revalidatePath } from "next/cache"

export async function createPost(formData: FormData) {
  const post = await db.post.create({ ... })

  revalidatePath("/posts")
  redirect(`/posts/${post.slug}`)
}
```

## Optimistic Updates

```tsx
"use client"

import { useOptimistic } from "react"
import { likePost } from "@/actions/posts"

export function LikeButton({ postId, likes }: { postId: string; likes: number }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (state, _) => state + 1
  )

  async function handleLike() {
    addOptimisticLike(null)
    await likePost(postId)
  }

  return (
    <form action={handleLike}>
      <button type="submit">
        ❤️ {optimisticLikes}
      </button>
    </form>
  )
}
```

### Optimistic List Updates

```tsx
"use client"

import { useOptimistic } from "react"
import { addTodo } from "@/actions/todos"

type Todo = { id: string; text: string; pending?: boolean }

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: string) => [
      ...state,
      { id: crypto.randomUUID(), text: newTodo, pending: true },
    ]
  )

  async function handleSubmit(formData: FormData) {
    const text = formData.get("text") as string
    addOptimisticTodo(text)
    await addTodo(formData)
  }

  return (
    <div>
      <ul>
        {optimisticTodos.map((todo) => (
          <li key={todo.id} className={todo.pending ? "opacity-50" : ""}>
            {todo.text}
          </li>
        ))}
      </ul>

      <form action={handleSubmit}>
        <input name="text" placeholder="New todo" />
        <button type="submit">Add</button>
      </form>
    </div>
  )
}
```

## Delete Action

```tsx
// actions/posts.ts
"use server"

import { revalidatePath } from "next/cache"

export async function deletePost(postId: string) {
  await db.post.delete({ where: { id: postId } })
  revalidatePath("/posts")
}
```

```tsx
// components/delete-button.tsx
"use client"

import { deletePost } from "@/actions/posts"
import { useTransition } from "react"

export function DeleteButton({ postId }: { postId: string }) {
  const [isPending, startTransition] = useTransition()

  const handleDelete = () => {
    startTransition(async () => {
      await deletePost(postId)
    })
  }

  return (
    <button onClick={handleDelete} disabled={isPending}>
      {isPending ? "Deleting..." : "Delete"}
    </button>
  )
}
```

## Action with Authentication

```tsx
// actions/posts.ts
"use server"

import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

export async function createPost(formData: FormData) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/login")
  }

  await db.post.create({
    data: {
      title: formData.get("title") as string,
      authorId: session.user.id,
    },
  })

  revalidatePath("/posts")
}
```

## Calling Actions from Client Components

### Using bind

```tsx
// Pass additional data with bind
"use client"

import { updatePost } from "@/actions/posts"

export function EditButton({ postId }: { postId: string }) {
  const updatePostWithId = updatePost.bind(null, postId)

  return (
    <form action={updatePostWithId}>
      <input name="title" />
      <button type="submit">Update</button>
    </form>
  )
}
```

### Using hidden fields

```tsx
<form action={updatePost}>
  <input type="hidden" name="postId" value={postId} />
  <input name="title" />
  <button type="submit">Update</button>
</form>
```

## Error Handling

```tsx
"use server"

export async function createPost(formData: FormData) {
  try {
    await db.post.create({ ... })
    revalidatePath("/posts")
    return { success: true }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { error: "Validation failed", details: error.flatten() }
    }
    // Log error for debugging
    console.error("Failed to create post:", error)
    return { error: "Something went wrong" }
  }
}
```

## Action Patterns

### Return Type Pattern

```tsx
// types/action.ts
export type ActionResult<T = void> =
  | { success: true; data: T }
  | { success: false; error: string; fieldErrors?: Record<string, string[]> }

// actions/posts.ts
"use server"

import { ActionResult } from "@/types/action"

export async function createPost(formData: FormData): Promise<ActionResult<{ id: string }>> {
  const validated = schema.safeParse(...)

  if (!validated.success) {
    return {
      success: false,
      error: "Validation failed",
      fieldErrors: validated.error.flatten().fieldErrors,
    }
  }

  try {
    const post = await db.post.create({ data: validated.data })
    revalidatePath("/posts")
    return { success: true, data: { id: post.id } }
  } catch {
    return { success: false, error: "Failed to create post" }
  }
}
```

### Safe Action Wrapper

```tsx
// lib/safe-action.ts
import { z } from "zod"

export function createSafeAction<TInput, TOutput>(
  schema: z.Schema<TInput>,
  handler: (data: TInput) => Promise<TOutput>
) {
  return async (formData: FormData) => {
    const rawData = Object.fromEntries(formData.entries())
    const validated = schema.safeParse(rawData)

    if (!validated.success) {
      return {
        success: false as const,
        fieldErrors: validated.error.flatten().fieldErrors,
      }
    }

    try {
      const data = await handler(validated.data)
      return { success: true as const, data }
    } catch (error) {
      return {
        success: false as const,
        error: error instanceof Error ? error.message : "Unknown error",
      }
    }
  }
}

// Usage
export const createPost = createSafeAction(
  createPostSchema,
  async (data) => {
    const post = await db.post.create({ data })
    revalidatePath("/posts")
    return post
  }
)
```

## Progressive Enhancement

Server actions work without JavaScript:

```tsx
// Works without JS (form submits normally)
// With JS, gets enhanced with pending states
<form action={createPost}>
  <input name="title" />
  <SubmitButton />
</form>
```

```tsx
// components/submit-button.tsx
"use client"

import { useFormStatus } from "react-dom"

export function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? "Submitting..." : "Submit"}
    </button>
  )
}
```
