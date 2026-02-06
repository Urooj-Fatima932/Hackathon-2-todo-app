# Tailwind CSS Patterns

## Responsive Design

Mobile-first breakpoints:

| Prefix | Min Width | Usage |
|--------|-----------|-------|
| (none) | 0px | Mobile default |
| `sm:` | 640px | Large phones |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops |
| `xl:` | 1280px | Desktops |
| `2xl:` | 1536px | Large screens |

```tsx
// Mobile first approach
<div className="
  text-sm           // Mobile: small text
  md:text-base      // Tablet+: normal text
  lg:text-lg        // Desktop+: large text
">

// Responsive grid
<div className="
  grid
  grid-cols-1       // Mobile: 1 column
  sm:grid-cols-2    // Small: 2 columns
  lg:grid-cols-3    // Large: 3 columns
  xl:grid-cols-4    // XL: 4 columns
  gap-4
  md:gap-6
  lg:gap-8
">

// Hide/show at breakpoints
<div className="hidden md:block">Desktop only</div>
<div className="block md:hidden">Mobile only</div>
```

## Spacing System

```tsx
// Padding
<div className="p-4">All sides</div>
<div className="px-4 py-2">Horizontal/Vertical</div>
<div className="pt-4 pb-2 pl-6 pr-8">Individual</div>

// Margin
<div className="m-4">All sides</div>
<div className="mx-auto">Center horizontally</div>
<div className="mt-8 mb-4">Top/bottom</div>

// Gap (for flex/grid)
<div className="flex gap-4">Gap between items</div>
<div className="grid gap-x-4 gap-y-8">Different X/Y gaps</div>

// Space between children
<div className="space-y-4">Vertical space between</div>
<div className="space-x-4">Horizontal space between</div>
```

## Typography

```tsx
// Font sizes
<p className="text-xs">Extra small (12px)</p>
<p className="text-sm">Small (14px)</p>
<p className="text-base">Base (16px)</p>
<p className="text-lg">Large (18px)</p>
<p className="text-xl">XL (20px)</p>
<p className="text-2xl">2XL (24px)</p>
<p className="text-3xl">3XL (30px)</p>
<p className="text-4xl">4XL (36px)</p>
<p className="text-5xl">5XL (48px)</p>

// Font weight
<p className="font-normal">Normal (400)</p>
<p className="font-medium">Medium (500)</p>
<p className="font-semibold">Semibold (600)</p>
<p className="font-bold">Bold (700)</p>

// Line height
<p className="leading-tight">Tight</p>
<p className="leading-normal">Normal</p>
<p className="leading-relaxed">Relaxed</p>

// Letter spacing
<h1 className="tracking-tight">Tight tracking</h1>
<p className="tracking-wide">Wide tracking</p>

// Text color with opacity
<p className="text-foreground">Default text</p>
<p className="text-muted-foreground">Muted text</p>
<p className="text-primary">Primary color</p>
```

## Flexbox Patterns

```tsx
// Center everything
<div className="flex items-center justify-center">
  Centered content
</div>

// Space between
<div className="flex items-center justify-between">
  <span>Left</span>
  <span>Right</span>
</div>

// Vertical stack
<div className="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

// Responsive direction
<div className="flex flex-col md:flex-row gap-4">
  <div>Column on mobile, row on desktop</div>
</div>

// Wrap items
<div className="flex flex-wrap gap-4">
  {items.map(item => <div key={item}>{item}</div>)}
</div>

// Grow/shrink
<div className="flex">
  <div className="flex-shrink-0 w-20">Fixed width</div>
  <div className="flex-grow">Takes remaining space</div>
</div>
```

## Grid Patterns

```tsx
// Basic grid
<div className="grid grid-cols-3 gap-4">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>

// Auto-fit (responsive without breakpoints)
<div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  {items.map(item => <Card key={item} />)}
</div>

// Span columns
<div className="grid grid-cols-4 gap-4">
  <div className="col-span-2">Spans 2 columns</div>
  <div>1 column</div>
  <div>1 column</div>
</div>

// Named grid areas
<div className="grid grid-cols-[1fr_3fr] grid-rows-[auto_1fr_auto] gap-4">
  <header className="col-span-2">Header</header>
  <aside>Sidebar</aside>
  <main>Content</main>
  <footer className="col-span-2">Footer</footer>
</div>
```

## Container Patterns

```tsx
// Centered container with padding
<div className="container mx-auto px-4 sm:px-6 lg:px-8">
  Content with responsive padding
</div>

// Max-width container
<div className="mx-auto max-w-7xl px-4">
  Max 1280px width
</div>

// Prose container for text
<div className="mx-auto max-w-prose">
  Long-form text content
</div>
```

## Background & Colors

```tsx
// Background colors
<div className="bg-background">Default background</div>
<div className="bg-muted">Muted background</div>
<div className="bg-primary">Primary color</div>
<div className="bg-secondary">Secondary color</div>

// Opacity
<div className="bg-primary/50">50% opacity</div>
<div className="bg-black/10">10% black overlay</div>

// Gradients
<div className="bg-gradient-to-r from-primary to-secondary">
  Horizontal gradient
</div>
<div className="bg-gradient-to-b from-background to-muted">
  Vertical gradient
</div>
```

## Borders & Shadows

```tsx
// Borders
<div className="border">Default border</div>
<div className="border-2">2px border</div>
<div className="border-t">Top border only</div>
<div className="border-primary">Colored border</div>
<div className="rounded-lg">Rounded corners</div>
<div className="rounded-full">Fully rounded</div>

// Shadows
<div className="shadow-sm">Small shadow</div>
<div className="shadow">Default shadow</div>
<div className="shadow-lg">Large shadow</div>
<div className="shadow-xl">Extra large</div>
<div className="shadow-2xl">2XL shadow</div>

// Ring (for focus states)
<button className="focus:ring-2 focus:ring-primary focus:ring-offset-2">
  Focus ring
</button>
```

## Interactive States

```tsx
// Hover
<button className="bg-primary hover:bg-primary/90">
  Hover to darken
</button>

// Focus
<input className="focus:outline-none focus:ring-2 focus:ring-primary" />

// Active
<button className="active:scale-95">
  Press to shrink
</button>

// Disabled
<button className="disabled:opacity-50 disabled:cursor-not-allowed" disabled>
  Disabled
</button>

// Group hover
<div className="group">
  <div className="group-hover:text-primary">
    Changes when parent is hovered
  </div>
</div>
```

## Transitions & Animations

```tsx
// Basic transition
<div className="transition-colors duration-200">
  Color transition
</div>

// All properties
<div className="transition-all duration-300 ease-in-out">
  All properties animate
</div>

// Transform on hover
<div className="transition-transform hover:scale-105">
  Scale on hover
</div>

// Built-in animations
<div className="animate-spin">Spinning</div>
<div className="animate-pulse">Pulsing</div>
<div className="animate-bounce">Bouncing</div>
```

## Position & Z-Index

```tsx
// Positioning
<div className="relative">
  <div className="absolute top-0 right-0">
    Top right corner
  </div>
</div>

// Fixed header
<header className="fixed top-0 left-0 right-0 z-50">
  Sticky header
</header>

// Sticky element
<aside className="sticky top-20">
  Sticks when scrolling
</aside>

// Z-index layers
<div className="z-0">Base</div>
<div className="z-10">Above</div>
<div className="z-50">Modal level</div>
```

## Aspect Ratios

```tsx
// Common ratios
<div className="aspect-square">1:1</div>
<div className="aspect-video">16:9</div>
<div className="aspect-[4/3]">4:3</div>

// With image
<div className="relative aspect-video">
  <Image src="/image.jpg" alt="" fill className="object-cover" />
</div>
```

## Overflow & Scrolling

```tsx
// Hide overflow
<div className="overflow-hidden">Clips content</div>

// Scroll
<div className="overflow-y-auto max-h-96">
  Scrollable container
</div>

// Scroll snap
<div className="overflow-x-auto snap-x snap-mandatory flex gap-4">
  {items.map(item => (
    <div key={item} className="snap-start flex-shrink-0 w-80">
      {item}
    </div>
  ))}
</div>
```

## Dark Mode

```tsx
// Dark mode variants
<div className="bg-white dark:bg-gray-900">
  White in light, dark in dark mode
</div>

<p className="text-gray-900 dark:text-gray-100">
  Dark text in light, light text in dark
</p>

// Using CSS variables (shadcn approach)
<div className="bg-background text-foreground">
  Automatically adapts to theme
</div>
```
