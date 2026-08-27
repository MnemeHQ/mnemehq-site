from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import audit

app = FastAPI(
    title="Mneme Architecture Audit API",
    description="API for the Architecture Governability Audit Workspace",
    version="0.1.0",
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(audit.router)

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
    uvicorn.run(app, host="0.0.0.0", port=8001)