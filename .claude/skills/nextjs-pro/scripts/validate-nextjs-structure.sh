#!/bin/bash

# =================================================================
# Next.js App Router Structure Validator
# =================================================================
# Validates Next.js projects for common App Router pitfalls:
# 1. Route group conflicts with root page.tsx
# 2. Missing 'use client' directives on interactive components

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Next.js App Router Structure Validator${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# =================================================================
# Check 1: Route Group Conflicts
# =================================================================

echo -e "${BLUE}🔍 Check 1: Route Group Conflicts${NC}"
echo "Checking for conflicting page.tsx files..."
echo ""

if [ -f "app/page.tsx" ] || [ -f "src/app/page.tsx" ]; then
  APP_DIR="app"
  [ -d "src/app" ] && APP_DIR="src/app"

  # Find route groups with page.tsx
  ROUTE_GROUPS=$(find "$APP_DIR" -maxdepth 1 -type d -name '(*)')

  if [ -n "$ROUTE_GROUPS" ]; then
    echo -e "${RED}❌ CONFLICT DETECTED!${NC}"
    echo -e "${RED}   Root page.tsx exists with route groups${NC}"
    echo ""
    echo "   Root page found: ${APP_DIR}/page.tsx"
    echo "   Route groups found:"
    for group in $ROUTE_GROUPS; do
      if [ -f "$group/page.tsx" ]; then
        echo "   - $group/page.tsx"
      fi
    done
    echo ""
    echo -e "${YELLOW}   📝 FIX:${NC} Remove ${APP_DIR}/page.tsx"
    echo "   The route group pages will handle the routes"
    echo ""
    ((ERRORS++))
  else
    echo -e "${GREEN}✅ No route group conflicts${NC}"
    echo ""
  fi
else
  echo -e "${GREEN}✅ No root page.tsx (OK if using route groups)${NC}"
  echo ""
fi

# =================================================================
# Check 2: Missing 'use client' Directives
# =================================================================

echo -e "${BLUE}🔍 Check 2: Missing 'use client' Directives${NC}"
echo "Checking for components with interactive features..."
echo ""

# Patterns that indicate need for 'use client'
INTERACTIVE_PATTERNS=(
  "onClick"
  "onChange"
  "onSubmit"
  "onFocus"
  "onBlur"
  "onKeyDown"
  "onKeyUp"
  "useState"
  "useEffect"
  "useContext"
  "useRef"
  "useReducer"
  "window\."
  "document\."
  "localStorage"
  "sessionStorage"
  "framer-motion"
  "react-hook-form"
  "@radix-ui"
)

# Find all TSX/JSX files
FILES=$(find . -type f \( -name "*.tsx" -o -name "*.jsx" \) \
  ! -path "*/node_modules/*" \
  ! -path "*/.next/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*")

MISSING_DIRECTIVE_COUNT=0

for file in $FILES; do
  # Skip server action files
  if grep -q "'use server'" "$file" 2>/dev/null; then
    continue
  fi

  # Check if file has 'use client'
  HAS_CLIENT_DIRECTIVE=false
  if head -n 5 "$file" | grep -q "'use client'" 2>/dev/null; then
    HAS_CLIENT_DIRECTIVE=true
  fi

  # Check for interactive patterns
  if [ "$HAS_CLIENT_DIRECTIVE" = false ]; then
    FOUND_INTERACTIVE=false

    for pattern in "${INTERACTIVE_PATTERNS[@]}"; do
      if grep -q "$pattern" "$file" 2>/dev/null; then
        FOUND_INTERACTIVE=true
        MATCHED_PATTERN="$pattern"
        break
      fi
    done

    if [ "$FOUND_INTERACTIVE" = true ]; then
      if [ $MISSING_DIRECTIVE_COUNT -eq 0 ]; then
        echo -e "${YELLOW}⚠️  Components missing 'use client' directive:${NC}"
        echo ""
      fi

      echo "   ${file}"
      echo "      → Contains: ${MATCHED_PATTERN}"
      ((MISSING_DIRECTIVE_COUNT++))
      ((WARNINGS++))
    fi
  fi
done

if [ $MISSING_DIRECTIVE_COUNT -eq 0 ]; then
  echo -e "${GREEN}✅ All interactive components have 'use client'${NC}"
else
  echo ""
  echo -e "${YELLOW}   📝 FIX:${NC} Add 'use client' as the first line of these files"
  echo "   Example:"
  echo "   'use client'"
  echo ""
  echo "   import { useState } from 'react'"
  echo "   ..."
fi

echo ""

# =================================================================
# Check 3: shadcn/ui Components (if present)
# =================================================================

if [ -d "components/ui" ] || [ -d "src/components/ui" ]; then
  echo -e "${BLUE}🔍 Check 3: shadcn/ui Component Directives${NC}"
  echo "Checking shadcn/ui components..."
  echo ""

  UI_DIR="components/ui"
  [ -d "src/components/ui" ] && UI_DIR="src/components/ui"

  # Components that should have 'use client'
  INTERACTIVE_UI_COMPONENTS=(
    "button"
    "input"
    "textarea"
    "checkbox"
    "switch"
    "select"
    "dialog"
    "sheet"
    "popover"
    "dropdown-menu"
    "tabs"
    "accordion"
    "toast"
    "toaster"
    "form"
    "combobox"
    "command"
    "slider"
  )

  MISSING_UI_DIRECTIVE=0

  for component in "${INTERACTIVE_UI_COMPONENTS[@]}"; do
    if [ -f "${UI_DIR}/${component}.tsx" ]; then
      if ! head -n 5 "${UI_DIR}/${component}.tsx" | grep -q "'use client'" 2>/dev/null; then
        if [ $MISSING_UI_DIRECTIVE -eq 0 ]; then
          echo -e "${YELLOW}⚠️  shadcn/ui components missing 'use client':${NC}"
          echo ""
        fi
        echo "   ${UI_DIR}/${component}.tsx"
        ((MISSING_UI_DIRECTIVE++))
        ((WARNINGS++))
      fi
    fi
  done

  if [ $MISSING_UI_DIRECTIVE -eq 0 ]; then
    echo -e "${GREEN}✅ All shadcn/ui components have correct directives${NC}"
  else
    echo ""
    echo -e "${YELLOW}   📝 FIX:${NC} Add 'use client' to these shadcn/ui components"
  fi

  echo ""
fi

# =================================================================
# Summary
# =================================================================

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ All checks passed!${NC}"
  echo "Your Next.js App Router structure looks good."
  exit 0
else
  if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ ${ERRORS} error(s) found${NC}"
  fi
  if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) found${NC}"
  fi
  echo ""
  echo "Please review and fix the issues above."

  if [ $ERRORS -gt 0 ]; then
    exit 1
  else
    exit 0
  fi
fi
