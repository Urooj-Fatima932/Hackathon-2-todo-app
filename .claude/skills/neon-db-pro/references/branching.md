# Neon Database Branching

## Overview

Neon allows creating instant database branches - full copies of your database that are isolated and can be used for development, testing, or staging environments.

## Creating Branches

### Via Dashboard

1. Go to Neon Console → Your Project → Branches
2. Click "Create Branch"
3. Select parent branch (usually `main`)
4. Name your branch (e.g., `dev`, `staging`, `feature-x`)

### Via CLI

```bash
# Install CLI
npm install -g neonctl

# Authenticate
neonctl auth

# Create branch
neonctl branches create --project-id <project-id> --name dev

# Create branch from specific point in time
neonctl branches create --project-id <project-id> --name staging --parent main --head

# Get connection string for branch
neonctl connection-string --project-id <project-id> --branch dev
```

### Via API

```typescript
const response = await fetch(
  `https://console.neon.tech/api/v2/projects/${projectId}/branches`,
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.NEON_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      branch: {
        name: "dev",
        parent_id: "br-xxx-main",
      },
      endpoints: [{ type: "read_write" }],
    }),
  }
)
```

## Branch Connection Strings

Each branch has its own connection string:

```bash
# Main branch
DATABASE_URL="postgresql://user:pass@ep-main-xxx-pooler.region.aws.neon.tech/db"

# Dev branch
DATABASE_URL_DEV="postgresql://user:pass@ep-dev-xxx-pooler.region.aws.neon.tech/db"

# Staging branch
DATABASE_URL_STAGING="postgresql://user:pass@ep-staging-xxx-pooler.region.aws.neon.tech/db"
```

## Environment-Based Configuration

### .env.development

```bash
DATABASE_URL="postgresql://user:pass@ep-dev-xxx-pooler.region.aws.neon.tech/db?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-dev-xxx.region.aws.neon.tech/db?sslmode=require"
```

### .env.production

```bash
DATABASE_URL="postgresql://user:pass@ep-main-xxx-pooler.region.aws.neon.tech/db?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-main-xxx.region.aws.neon.tech/db?sslmode=require"
```

## CI/CD Integration

### GitHub Actions - Preview Branches

```yaml
# .github/workflows/preview.yml
name: Create Preview Branch

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  create-branch:
    runs-on: ubuntu-latest
    steps:
      - name: Create Neon Branch
        uses: neondatabase/create-branch-action@v5
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch_name: preview-pr-${{ github.event.number }}
          api_key: ${{ secrets.NEON_API_KEY }}

      - name: Run Migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: ${{ steps.create-branch.outputs.db_url }}

      - name: Deploy Preview
        # Deploy to Vercel/Netlify with branch DATABASE_URL
```

### Cleanup on PR Close

```yaml
# .github/workflows/cleanup.yml
name: Cleanup Preview Branch

on:
  pull_request:
    types: [closed]

jobs:
  delete-branch:
    runs-on: ubuntu-latest
    steps:
      - name: Delete Neon Branch
        uses: neondatabase/delete-branch-action@v3
        with:
          project_id: ${{ secrets.NEON_PROJECT_ID }}
          branch: preview-pr-${{ github.event.number }}
          api_key: ${{ secrets.NEON_API_KEY }}
```

## Vercel Integration

Neon has native Vercel integration that automatically creates preview branches:

1. Install Neon integration in Vercel
2. Link your project
3. Preview deployments get their own database branch automatically

```typescript
// Automatic environment variable
// POSTGRES_URL is set per deployment
const sql = neon(process.env.POSTGRES_URL!)
```

## Branch Management

### List Branches

```bash
neonctl branches list --project-id <project-id>
```

### Delete Branch

```bash
neonctl branches delete --project-id <project-id> --branch dev
```

### Reset Branch to Parent

```bash
neonctl branches reset --project-id <project-id> --branch dev --parent main
```

## Use Cases

### 1. Development Branch

Persistent branch for local development:

```bash
# Create once
neonctl branches create --name dev

# Use in .env.local
DATABASE_URL="postgresql://...@ep-dev-xxx-pooler..."
```

### 2. Feature Branches

Per-feature branches for isolated testing:

```bash
# Create for feature
neonctl branches create --name feature-auth --parent dev

# Delete when merged
neonctl branches delete --branch feature-auth
```

### 3. Staging Branch

Pre-production environment:

```bash
# Create staging from production
neonctl branches create --name staging --parent main

# Reset staging to match production
neonctl branches reset --branch staging --parent main
```

### 4. Testing Branch

For running automated tests:

```bash
# Create fresh branch for tests
neonctl branches create --name test-run-123

# Run tests
npm test

# Delete after tests
neonctl branches delete --branch test-run-123
```

## Best Practices

1. **Use main for production** - Keep production data on `main` branch
2. **Branch naming convention** - Use prefixes: `dev-`, `staging-`, `feature-`, `preview-`
3. **Clean up branches** - Delete branches when no longer needed
4. **Automate in CI/CD** - Create/delete branches automatically
5. **Never share credentials** - Each branch should have its own users if needed

## Costs

- Branches are instant and storage-efficient (copy-on-write)
- Only pay for data that differs from parent
- Compute charges apply when branch is active
- Delete unused branches to minimize costs
