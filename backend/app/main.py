from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine
from app.models import SQLModel
from app.routes import tasks
from app.routes import auth
from app.utils.exceptions import http_exception_handler, general_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup: Create database tables
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown: Clean up resources
    pass


# Create FastAPI application
app = FastAPI(
    title="Backend Todo API",
    description="Secure, multi-user RESTful API for todo task management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hackathon-2-todo-app-phi.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    """Root endpoint to verify API is running."""
    return {"message": "Todo API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
