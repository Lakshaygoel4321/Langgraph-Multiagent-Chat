from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from config.settings import settings
from api.routes.agent import router as agent_router
from api.middleware import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    print("🚀 Starting FastAPI LangGraph Agent System...")
    settings.validate()
    print("✅ Settings validated")
    yield
    # Shutdown
    print("👋 Shutting down FastAPI LangGraph Agent System...")


# Initialize FastAPI app
app = FastAPI(
    title="LangGraph Multi-Agent API",
    description="AI-powered multi-agent system with business, research, and technical expertise",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup additional middleware
setup_middleware(app)

# Include routers
app.include_router(agent_router, prefix="/api/v1", tags=["agent"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LangGraph Multi-Agent API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "model": settings.MODEL_NAME
    }


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
