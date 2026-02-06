# Form Components

## Basic Contact Form

```tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export function ContactForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsSubmitting(true)

    const formData = new FormData(e.currentTarget)
    // Handle submission
    console.log(Object.fromEntries(formData))

    setIsSubmitting(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="firstName">First Name</Label>
          <Input
            id="firstName"
            name="firstName"
            placeholder="John"
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="lastName">Last Name</Label>
          <Input
            id="lastName"
            name="lastName"
            placeholder="Doe"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="john@example.com"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="message">Message</Label>
        <Textarea
          id="message"
          name="message"
          placeholder="How can we help you?"
          rows={5}
          required
        />
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Sending..." : "Send Message"}
      </Button>
    </form>
  )
}
```

## Newsletter Form

```tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { CheckCircle } from "lucide-react"

export function NewsletterForm() {
  const [email, setEmail] = useState("")
  const [isSubmitted, setIsSubmitted] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    // Handle subscription
    setIsSubmitted(true)
  }

  if (isSubmitted) {
    return (
      <div className="flex items-center gap-2 text-green-600">
        <CheckCircle className="h-5 w-5" />
        <span>Thanks for subscribing!</span>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="max-w-xs"
        required
      />
      <Button type="submit">Subscribe</Button>
    </form>
  )
}
```

## Form with React Hook Form + Zod

```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  company: z.string().optional(),
  plan: z.enum(["starter", "pro", "enterprise"]),
})

type FormData = z.infer<typeof formSchema>

export function SignupForm() {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      plan: "starter",
    },
  })

  async function onSubmit(data: FormData) {
    console.log(data)
    // Handle submission
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input
          id="name"
          {...register("name")}
          className={errors.name ? "border-destructive" : ""}
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          {...register("email")}
          className={errors.email ? "border-destructive" : ""}
        />
        {errors.email && (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="company">Company (Optional)</Label>
        <Input id="company" {...register("company")} />
      </div>

      <div className="space-y-2">
        <Label htmlFor="plan">Plan</Label>
        <Select
          onValueChange={(value) => setValue("plan", value as FormData["plan"])}
          defaultValue="starter"
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a plan" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="starter">Starter - $9/mo</SelectItem>
            <SelectItem value="pro">Pro - $29/mo</SelectItem>
            <SelectItem value="enterprise">Enterprise - Custom</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Creating account..." : "Create Account"}
      </Button>
    </form>
  )
}
```

## Checkbox & Radio Groups

```tsx
"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"

export function PreferencesForm() {
  return (
    <div className="space-y-8">
      {/* Checkbox */}
      <div className="flex items-center space-x-2">
        <Checkbox id="terms" />
        <Label htmlFor="terms" className="text-sm">
          I agree to the terms and conditions
        </Label>
      </div>

      {/* Multiple Checkboxes */}
      <div className="space-y-4">
        <Label>Notifications</Label>
        <div className="space-y-2">
          {["Email", "SMS", "Push"].map((type) => (
            <div key={type} className="flex items-center space-x-2">
              <Checkbox id={type.toLowerCase()} />
              <Label htmlFor={type.toLowerCase()}>{type} notifications</Label>
            </div>
          ))}
        </div>
      </div>

      {/* Radio Group */}
      <div className="space-y-4">
        <Label>Billing Cycle</Label>
        <RadioGroup defaultValue="monthly">
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="monthly" id="monthly" />
            <Label htmlFor="monthly">Monthly</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="yearly" id="yearly" />
            <Label htmlFor="yearly">Yearly (Save 20%)</Label>
          </div>
        </RadioGroup>
      </div>
    </div>
  )
}
```

## Form Field Component

```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface FormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  description?: string
}

export function FormField({
  label,
  error,
  description,
  className,
  id,
  ...props
}: FormFieldProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        className={cn(error && "border-destructive", className)}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        {...props}
      />
      {description && !error && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
      {error && (
        <p id={`${id}-error`} className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}

// Usage
<FormField
  id="email"
  label="Email Address"
  type="email"
  placeholder="you@example.com"
  description="We'll never share your email."
  error={errors.email?.message}
/>
```

## Search Form

```tsx
"use client"

import { useState } from "react"
import { Search, X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function SearchForm({ onSearch }: { onSearch: (query: string) => void }) {
  const [query, setQuery] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onSearch(query)
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        type="search"
        placeholder="Search..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="pl-10 pr-10"
      />
      {query && (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2"
          onClick={() => setQuery("")}
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </form>
  )
}
```

## File Upload

```tsx
"use client"

import { useState, useRef } from "react"
import { Upload, X } from "lucide-react"
import { Button } from "@/components/ui/button"

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  return (
    <div className="space-y-4">
      <div
        className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors hover:border-primary"
        onClick={() => inputRef.current?.click()}
      >
        <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          Click to upload or drag and drop
        </p>
        <p className="text-xs text-muted-foreground">PNG, JPG up to 10MB</p>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileChange}
        />
      </div>

      {file && (
        <div className="flex items-center justify-between rounded-lg border p-3">
          <span className="text-sm truncate">{file.name}</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setFile(null)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
```

## Server Actions Form (Next.js 14+)

```tsx
// app/actions.ts
"use server"

import { z } from "zod"

const schema = z.object({
  email: z.string().email(),
  message: z.string().min(10),
})

export async function submitForm(formData: FormData) {
  const validatedFields = schema.safeParse({
    email: formData.get("email"),
    message: formData.get("message"),
  })

  if (!validatedFields.success) {
    return { error: "Invalid form data" }
  }

  // Process form
  return { success: true }
}

// Component
"use client"

import { useFormStatus } from "react-dom"
import { submitForm } from "./actions"

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <Button type="submit" disabled={pending}>
      {pending ? "Submitting..." : "Submit"}
    </Button>
  )
}

export function ServerActionForm() {
  return (
    <form action={submitForm} className="space-y-4">
      <Input name="email" type="email" placeholder="Email" required />
      <Textarea name="message" placeholder="Message" required />
      <SubmitButton />
    </form>
  )
}
```
