
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, field_validator

from app.scraper import WebScraper
from app.models import ScraperResult

# Configuration
APP_VERSION = "1.0.0"
SCRAPE_TIMEOUT = int(os.getenv("SCRAPE_TIMEOUT", "60"))
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

# FastAPI app
app = FastAPI(
    title="Lyftr AI Web Scraper",
    description="Universal website scraper with JS rendering and JSON viewer",
    version=APP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ScrapeRequest(BaseModel):
    url: str
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


@app.get("/healthz")
async def health_check():
    """Health check endpoint - returns 200 if server is running"""
    return {
        "status": "ok",
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    """
    Scrape a URL and return structured content
    
    Returns JSON matching the Lyftr AI schema with sections, metadata, and interactions
    """
    try:
        scraper = WebScraper(timeout=SCRAPE_TIMEOUT)
        result = await scraper.scrape(request.url)
        
        return JSONResponse(
            content={"result": result.model_dump()},
            status_code=200
        )
    
    except asyncio.TimeoutError:
        return JSONResponse(
            content={
                "result": {
                    "url": request.url,
                    "scrapedAt": datetime.utcnow().isoformat() + "Z",
                    "meta": {"title": "", "description": "", "language": "en", "canonical": None},
                    "sections": [],
                    "interactions": {"clicks": [], "scrolls": 0, "pages": [request.url]},
                    "errors": [{"message": "Scraping timed out after 60 seconds", "phase": "timeout"}]
                }
            },
            status_code=408
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "result": {
                    "url": request.url,
                    "scrapedAt": datetime.utcnow().isoformat() + "Z",
                    "meta": {"title": "", "description": "", "language": "en", "canonical": None},
                    "sections": [],
                    "interactions": {"clicks": [], "scrolls": 0, "pages": [request.url]},
                    "errors": [{"message": str(e), "phase": "unknown"}]
                }
            },
            status_code=500
        )


# Serve frontend
@app.get("/")
async def serve_index():
    """Serve the frontend SPA"""
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not built. Run: cd frontend && npm install && npm run build"}


# Mount static files
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )