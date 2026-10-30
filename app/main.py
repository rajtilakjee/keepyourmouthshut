import logging
import os
import zipfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Podcast generation writes to app/downloads and app/cache relative to the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)

from generate_podcast import generate_podcast  # noqa: E402

logger = logging.getLogger(__name__)

APP_DIR = REPO_ROOT / "app"
DOWNLOADS = APP_DIR / "downloads"

app = FastAPI(title="KeepYourMouthShut", version="0.0.1")

_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    name: str = Field(min_length=1)
    desc: str = Field(min_length=1)
    topic1: str = Field(min_length=1)
    topic2: str = Field(min_length=1)
    topic3: str = Field(min_length=1)
    advert1: str = Field(min_length=1)
    advert2: str = Field(min_length=1)


def _safe_stem(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in (" ", "-", "_") else "_" for ch in name)
    cleaned = " ".join(cleaned.split()).strip(" .")
    return cleaned or "podcast"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate")
def generate(body: GenerateRequest):
    """Generate a podcast script and voice-over, returned as a zip archive."""
    topics = [body.topic1, body.topic2, body.topic3]
    adverts = [body.advert1, body.advert2]

    try:
        mp3_name, txt_name = generate_podcast(body.name, body.desc, topics, adverts)
    except Exception as exc:
        logger.exception("Podcast generation failed")
        raise HTTPException(status_code=500, detail="Podcast generation failed.") from exc

    mp3_file = DOWNLOADS / mp3_name
    txt_file = DOWNLOADS / txt_name
    if not mp3_file.is_file() or not txt_file.is_file():
        raise HTTPException(status_code=500, detail="Podcast generation failed.")

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    zip_path = DOWNLOADS / f"{_safe_stem(body.name)}_podcast.zip"
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        zip_file.write(mp3_file, arcname=mp3_file.name)
        zip_file.write(txt_file, arcname=txt_file.name)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_path.name,
    )
