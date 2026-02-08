# Common Errors and Fixes

Battle-tested solutions to errors encountered during JWT auth implementation.

---

## Backend Errors

### 1. "password cannot be longer than 72 bytes"

**Error:**
```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

**Cause:** bcrypt has a 72-byte limit. passlib doesn't handle this properly with newer bcrypt versions.

**Fix:** Use bcrypt directly with truncation:
```python
# ❌ WRONG
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
pwd_context.hash(password)

# ✅ CORRECT
import bcrypt
password_bytes = password.encode('utf-8')[:72]  # Truncate!
bcrypt.hashpw(password_bytes, bcrypt.gensalt())
```

---

### 2. "column users.hashed_password does not exist"

**Error:**
```
sqlalchemy.exc.ProgrammingError: column users.hashed_password does not exist
```

**Cause:** Database schema is out of sync with models.

**Fix:** Drop and recreate tables (dev only):
```python
from sqlmodel import SQLModel
from app.database import engine
from app.models import User, Task

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
```

---

### 3. "Field required: jwt_secret"

**Error:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
jwt_secret
  Field required
```

**Cause:** JWT_SECRET not in .env file.

**Fix:** Add to `backend/.env`:
```
JWT_SECRET=your-super-secret-32-char-minimum-key
```

---

### 4. Module 'bcrypt' has no attribute '__about__'

**Error:**
```
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Cause:** passlib trying to check bcrypt version but newer bcrypt changed API.

**Fix:** Don't use passlib. Use bcrypt directly (see error #1).

---

### 5. "Token has expired" / "Invalid token"

**Error:** 401 Unauthorized

**Cause:** Token expired or malformed.

**Fix:**
- Check JWT_SECRET matches between token creation and verification
- Verify token hasn't expired
- Frontend should handle 401 by redirecting to login

---

## Frontend Errors

### 6. "useAuth must be used within AuthProvider"

**Error:**
```
Error: useAuth must be used within an AuthProvider
```

**Cause:** Component using `useAuth()` is not wrapped by AuthProvider.

**Fix:** Wrap app in AuthProvider in `layout.tsx`:
```typescript
import { AuthProvider } from "@/lib/auth/context";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

---

### 7. Field name mismatch (undefined values)

**Error:** Data displays as undefined or missing.

**Cause:** Frontend using camelCase but backend returns snake_case.

**Fix:** Use snake_case in TypeScript types:
```typescript
// ❌ WRONG
interface Task {
  userId: string;
  isCompleted: boolean;
  createdAt: string;
}

// ✅ CORRECT
interface Task {
  user_id: string;
  is_completed: boolean;
  created_at: string;
}
```

---

### 8. Infinite redirect loop on protected routes

**Error:** Page keeps redirecting between login and protected route.

**Cause:** Auth state check happening before hydration completes.

**Fix:** Wait for isLoading to be false:
```typescript
const { isAuthenticated, isLoading } = useAuth();

useEffect(() => {
  // Don't redirect while still loading
  if (!isLoading && !isAuthenticated) {
    router.push("/login");
  }
}, [isAuthenticated, isLoading]);

// Don't render until loaded
if (isLoading) return <Loading />;
```

---

### 9. CORS errors

**Error:**
```
Access to fetch blocked by CORS policy
```

**Cause:** Backend not allowing frontend origin.

**Fix:** Configure CORS in FastAPI:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 10. "Cannot find module 'next-themes/dist/types'"

**Error:** TypeScript error with next-themes.

**Fix:** Update import:
```typescript
// ❌ WRONG
import { type ThemeProviderProps } from "next-themes/dist/types"

// ✅ CORRECT
import { type ThemeProviderProps } from "next-themes"
```

---

## Database Errors

### 11. Connection refused to Neon DB

**Error:**
```
psycopg2.OperationalError: connection refused
```

**Fix:**
- Check DATABASE_URL is correct
- Ensure `?sslmode=require` is in connection string
- Verify Neon project is active (not suspended)

---

### 12. Foreign key constraint failure

**Error:**
```
IntegrityError: insert or update violates foreign key constraint
```

**Cause:** Creating task for user_id that doesn't exist.

**Fix:** Ensure user exists before creating related records. With JWT auth, always use `current_user.id` from the dependency.

---

## Quick Debugging Checklist

1. **Backend not starting?**
   - Check all required env vars exist
   - Verify DATABASE_URL format
   - Check for import errors

2. **Auth not working?**
   - Verify JWT_SECRET is set
   - Check token is being sent in headers
   - Verify password hashing uses bcrypt directly

3. **Frontend errors?**
   - Check AuthProvider wraps app
   - Verify API_URL is correct
   - Check field names match backend (snake_case)

4. **Database issues?**
   - Drop and recreate tables if schema changed
   - Check connection string has sslmode=require
