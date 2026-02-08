# Quickstart Guide: Frontend Todo Web Application

**Date**: 2026-02-07
**Feature**: 002-frontend-todo-app
**Estimated Setup Time**: 10-15 minutes

## Prerequisites

Before starting, ensure you have:

- **Node.js**: v18.17.0 or higher (v20 recommended)
- **npm**: v9.0.0 or higher (or yarn/pnpm)
- **Git**: For cloning and branching
- **Code Editor**: VS Code recommended (with ESLint, Prettier, Tailwind CSS IntelliSense extensions)
- **Backend Running**: FastAPI backend must be running on `http://localhost:8000`

**Check Prerequisites**:
```bash
node --version    # Should be v18+
npm --version     # Should be v9+
git --version
```

---

## Setup Steps

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Initialize Next.js Project (if not already done)

If `package.json` doesn't exist:

```bash
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Prompts** (accept defaults):
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router
- ❌ src/ directory
- ✅ Import alias (@/*)

### 3. Install Dependencies

```bash
npm install react-hot-toast
```

**Dependencies Explained**:
- `react-hot-toast`: Toast notifications for user feedback

### 4. Install shadcn/ui

```bash
npx shadcn-ui@latest init
```

**Configuration**:
- Style: Default
- Base color: Slate
- CSS variables: Yes

**Add Required Components**:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add card
npx shadcn-ui@latest add checkbox
```

### 5. Configure Environment Variables

Create `.env.local`:

```bash
touch .env.local
```

Add:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Notes**:
- `NEXT_PUBLIC_*` variables are exposed to browser
- Never commit `.env.local` (already in `.gitignore`)
- For production, set in deployment platform (Vercel, etc.)

### 6. Verify Backend is Running

Before starting frontend, ensure backend is accessible:

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

**If Backend Not Running**:
```bash
cd ../backend
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
uvicorn app.main:app --reload --port 8000
```

### 7. Start Development Server

```bash
npm run dev
```

**Expected Output**:
```
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Ready in 2.5s
```

### 8. Verify Installation

Open browser to `http://localhost:3000`:
- Should see default Next.js page (will be replaced with landing page)

---

## Project Structure

After setup, your `frontend/` directory should look like:

```
frontend/
├── app/
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── ui/                 # shadcn/ui components
│       ├── button.tsx
│       ├── dialog.tsx
│       └── ...
├── lib/
│   └── utils.ts            # Utility functions (from shadcn)
├── public/
│   └── ...
├── .env.local              # Environment variables (not committed)
├── .eslintrc.json
├── .gitignore
├── components.json         # shadcn/ui config
├── next.config.js
├── package.json
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
└── CLAUDE.md               # Development guidelines
```

---

## Development Workflow

### Creating New Components

```bash
# Option 1: Manual creation
touch components/TaskCard.tsx

# Option 2: Using shadcn/ui
npx shadcn-ui@latest add [component-name]
```

### Running Commands

```bash
# Development server (with hot reload)
npm run dev

# Production build
npm run build
npm run start

# Linting
npm run lint

# Type checking
npx tsc --noEmit
```

### Environment-Specific URLs

| Environment | Frontend URL | Backend URL |
|-------------|-------------|-------------|
| Development | http://localhost:3000 | http://localhost:8000 |
| Production | https://yourdomain.com | https://api.yourdomain.com |

---

## Common Issues & Solutions

### Issue: "Module not found: @/lib/types"

**Cause**: File doesn't exist yet

**Solution**: Create the file:
```bash
touch lib/types.ts
```

### Issue: Backend API not reachable

**Symptoms**: Network errors, CORS errors

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Restart Next.js dev server: `npm run dev`
4. Check backend CORS settings allow `http://localhost:3000`

### Issue: Tailwind styles not applying

**Solutions**:
1. Check `tailwind.config.ts` has correct content paths
2. Restart dev server
3. Verify `globals.css` imports Tailwind:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

### Issue: TypeScript errors

**Solutions**:
1. Run `npm install` to ensure all types are installed
2. Check `tsconfig.json` has correct paths
3. Restart VS Code TypeScript server: Cmd+Shift+P → "Restart TS Server"

---

## Testing the Setup

### Manual Smoke Test

1. **Visit Landing Page**: http://localhost:3000
   - Should load without errors

2. **Visit Tasks Page**: http://localhost:3000/tasks (after implementation)
   - Should fetch tasks from backend
   - Should display loading state → task list

3. **Create a Task**:
   - Click "New Task" button
   - Fill form, submit
   - Should see new task in list

4. **Check Network Tab**:
   - Open DevTools → Network
   - Should see API calls to `http://localhost:8000/api/tasks`
   - Status codes should be 200/201

### Automated Health Check

Create `scripts/health-check.sh`:
```bash
#!/bin/bash
echo "Checking backend..."
curl -f http://localhost:8000/health || exit 1

echo "Checking frontend..."
curl -f http://localhost:3000 || exit 1

echo "✅ All services healthy"
```

Run: `bash scripts/health-check.sh`

---

## Next Steps

After setup is complete:

1. **Implement Types**: Create `lib/types.ts` with interfaces from `data-model.md`
2. **Build API Client**: Create `lib/api.ts` with fetch wrapper
3. **Create Landing Page**: Implement `app/(marketing)/page.tsx`
4. **Build Task Components**: Create `TaskCard.tsx`, `TaskForm.tsx`, etc.
5. **Implement Task Pages**: Build `app/tasks/page.tsx`

**Refer to**:
- `research.md` for architecture decisions
- `data-model.md` for TypeScript types
- `contracts/api-endpoints.md` for API details
- `frontend/CLAUDE.md` for coding guidelines

---

## Useful Commands Reference

```bash
# Development
npm run dev                    # Start dev server
npm run build                  # Build for production
npm run start                  # Start production server
npm run lint                   # Run ESLint

# Dependencies
npm install [package]          # Add dependency
npm install -D [package]       # Add dev dependency
npm update                     # Update dependencies

# shadcn/ui
npx shadcn-ui@latest add [component]   # Add UI component
npx shadcn-ui@latest list              # List available components

# TypeScript
npx tsc --noEmit              # Type check without emitting files

# Git
git status                    # Check branch and changes
git add .                     # Stage all changes
git commit -m "message"       # Commit changes
```

---

## Configuration Files Explained

### `next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add custom config here
  images: {
    domains: ['localhost'],  // For next/image
  },
};

module.exports = nextConfig;
```

### `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Custom theme extensions
    },
  },
  plugins: [],
};

export default config;
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

---

## VS Code Recommended Extensions

Install these extensions for best development experience:

1. **ESLint** (`dbaeumer.vscode-eslint`)
2. **Prettier** (`esbenp.prettier-vscode`)
3. **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)
4. **TypeScript Vue Plugin (Volar)** (for better TS support)
5. **Error Lens** (inline error display)

**Auto-install** (from `.vscode/extensions.json`):
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss"
  ]
}
```

---

## Performance Optimization Tips

1. **Use Server Components** by default (no `'use client'`)
2. **Enable Image Optimization**: Use `next/image` for all images
3. **Code Splitting**: Use dynamic imports for heavy components
4. **Font Optimization**: Use `next/font` for Google Fonts
5. **Bundle Analysis**: Run `npm run build` and check output

---

## Security Checklist

- ✅ `.env.local` in `.gitignore`
- ✅ No hardcoded secrets in code
- ✅ HTTPS in production
- ✅ Content Security Policy headers (add in `next.config.js`)
- ✅ API client validates responses (type guards)

---

## Getting Help

**Stuck? Check these resources**:

1. **Next.js Docs**: https://nextjs.org/docs
2. **shadcn/ui Docs**: https://ui.shadcn.com
3. **Tailwind CSS Docs**: https://tailwindcss.com/docs
4. **TypeScript Handbook**: https://www.typescriptlang.org/docs
5. **Project Docs**: `specs/002-frontend-todo-app/`

**Internal Resources**:
- `frontend/CLAUDE.md`: Coding guidelines
- `backend/CLAUDE.md`: Backend API reference
- `CLAUDE.md`: Project-wide rules

---

## Summary

✅ **Setup Complete** when:
- Dev server runs at http://localhost:3000
- Backend accessible at http://localhost:8000
- No console errors
- Tailwind styles render correctly
- TypeScript compiles without errors

**Total Setup Time**: ~10-15 minutes

**Next**: Proceed to implementation (see tasks.md after `/sp.tasks` runs)
