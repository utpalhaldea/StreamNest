import os
import logging
from urllib.parse import urlparse

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("streamnest")

app = FastAPI(title="StreamNest", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ResolveRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

def valid_diskwala_url(value: str) -> bool:
    try:
        p = urlparse(value.strip())
        host = (p.hostname or "").lower()
        return p.scheme in {"http", "https"} and (
            host == "diskwala.com" or host.endswith(".diskwala.com")
        )
    except Exception:
        return False

async def resolve_media(url: str) -> dict:
    endpoint = os.getenv("DISKWALA_PROXY_URL", "").strip()
    api_key = os.getenv("DISKWALA_API_KEY", "").strip()
    if not endpoint or not api_key:
        raise RuntimeError("DISKWALA_PROXY_URL/DISKWALA_API_KEY are not configured.")

    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        r = await client.post(
            endpoint,
            json={"url": url},
            headers={"x-api-key": api_key},
        )
    if r.status_code != 200:
        raise RuntimeError(f"Resolver returned HTTP {r.status_code}")
    data = r.json()
    info = data.get("fileInfo") or {}
    media_url = info.get("url")
    if not media_url:
        raise RuntimeError("Resolver returned no media URL.")
    return {
        "title": info.get("name") or "DiskWala video",
        "mime_type": info.get("type") or "video/mp4",
        "size": int(info.get("size") or 0),
        "media_url": media_url,
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/resolve")
async def resolve(payload: ResolveRequest):
    url = payload.url.strip()
    if not valid_diskwala_url(url):
        raise HTTPException(400, "Please enter a valid DiskWala share URL.")
    try:
        return {"ok": True, **await resolve_media(url)}
    except Exception as exc:
        log.exception("Resolve failed")
        raise HTTPException(502, "The configured resolver could not resolve this link.") from exc

@app.get("/health")
async def health():
    return {"ok": True, "service": "StreamNest"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
