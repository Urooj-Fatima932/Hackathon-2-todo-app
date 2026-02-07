# API Testing Guide

## Server Status

✓ Server is running at: http://localhost:8000
✓ Database: SQLite (test_todo.db)
✓ Auto-reload: Enabled

## Quick Start Testing

### 1. View API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Test Endpoints with Swagger UI

Visit http://localhost:8000/docs and try these endpoints:

#### Health Check
```
GET /health
```
Expected: `{"status": "healthy"}`

#### Root Endpoint
```
GET /
```
Expected: Welcome message with API info

#### Create a Task
```
POST /api/test-user/tasks
Body:
{
  "title": "My first task",
  "description": "Test task from API"
}
```

#### List All Tasks
```
GET /api/test-user/tasks
```

#### Get Single Task
```
GET /api/test-user/tasks/{id}
```

#### Update a Task
```
PUT /api/test-user/tasks/{id}
Body:
{
  "title": "Updated task",
  "description": "Updated description"
}
```

#### Toggle Task Completion
```
PATCH /api/test-user/tasks/{id}/complete
```

#### Delete a Task
```
DELETE /api/test-user/tasks/{id}
```

#### Filter Tasks by Status
```
GET /api/test-user/tasks?status=completed
GET /api/test-user/tasks?status=pending
```

### 3. Test with cURL (PowerShell)

```powershell
# Health check
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/api/test-user/tasks `
  -H "Content-Type: application/json" `
  -d '{\"title\": \"Test task\", \"description\": \"Testing API\"}'

# List tasks
curl http://localhost:8000/api/test-user/tasks

# Get task by ID
curl http://localhost:8000/api/test-user/tasks/1

# Update task
curl -X PUT http://localhost:8000/api/test-user/tasks/1 `
  -H "Content-Type: application/json" `
  -d '{\"title\": \"Updated\", \"description\": \"Updated desc\"}'

# Toggle completion
curl -X PATCH http://localhost:8000/api/test-user/tasks/1/complete

# Delete task
curl -X DELETE http://localhost:8000/api/test-user/tasks/1
```

### 4. Test with Python (if requests module issues resolved)

```python
import requests

# Create task
response = requests.post(
    "http://localhost:8000/api/test-user/tasks",
    json={"title": "Test", "description": "Testing"}
)
print(response.json())
```

## Server Management

### Start Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Stop Server
Press `CTRL+C` in the terminal where the server is running

### View Logs
Server logs appear in the terminal. Look for:
- Startup messages
- Request logs
- SQL queries (SQLAlchemy logs)
- Error messages

## Database

### Location
`backend/test_todo.db`

### Tables
- `users` - User accounts
- `tasks` - Todo tasks with foreign key to users

### View Database
You can use any SQLite browser tool to inspect the database:
- DB Browser for SQLite
- SQLite CLI: `sqlite3 backend/test_todo.db`

## Environment Configuration

File: `backend/.env`

Current settings:
- Database: SQLite (local testing)
- Port: 8000
- Debug: True
- CORS: Enabled for localhost:3000, localhost:5173

## Next Steps

1. ✓ Backend API is running and ready
2. [ ] Test endpoints via Swagger UI (http://localhost:8000/docs)
3. [ ] Build the Next.js frontend
4. [ ] Implement Better Auth integration
5. [ ] Deploy to production (switch to Neon PostgreSQL)

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify Python dependencies are installed: `pip install -r requirements-local.txt`
- Check .env file exists and is configured correctly

### Database errors
- Delete test_todo.db and restart server to recreate tables
- Check SQLAlchemy logs for specific error messages

### CORS errors from frontend
- Add your frontend URL to CORS_ORIGINS in .env
- Restart the server after changing .env
