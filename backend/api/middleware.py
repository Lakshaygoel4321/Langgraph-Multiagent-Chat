from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import logging


logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    """Setup custom middleware for the application"""
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests with timing"""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        return response
    
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add security headers to responses"""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
