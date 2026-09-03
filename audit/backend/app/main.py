from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
import os

from app.api import audit
from app.api import v1 as api_v1

app = FastAPI(
    title="Mneme Architecture Audit API",
    description="API for the Architecture Governability Audit Workspace",
    version="0.1.0",
)

# Custom exception handler to format errors for frontend
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

# CORS for frontend development and production
# Allow origins from environment variable (comma-separated) or defaults
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "https://mnemehq.com,https://www.mnemehq.com,http://localhost:3001,http://127.0.0.1:3001")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*mnemehq\.com.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(audit.router, prefix="/api")
app.include_router(api_v1.router, prefix="")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "mneme-audit-api"}

# Serve frontend build in production
frontend_build = os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "public")
if os.path.exists(frontend_build):
    app.mount("/", StaticFiles(directory=frontend_build, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)