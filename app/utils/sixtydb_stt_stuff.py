"""60db STT — standalone utility.

KYMS's podcast pipeline is text-in / audio-out so there is no built-in
STT consumer. This module exists so callers (admin scripts, future
"upload a voice memo and turn it into a podcast topic" flows) can
transcribe wav/mp3/m4a files without re-deriving the API contract.

    from utils.sixtydb_stt_stuff import transcribe
    text = transcribe("path/to/audio.mp3")

Reference: https://docs.60db.ai/api-reference/stt/speech-to-text
"""

import mimetypes
import os
from pathlib import Path
from typing import Optional

import requests

DEFAULT_API_BASE = "https://api.60db.ai"


def transcribe(
    audio_path: str,
    language: Optional[str] = None,
    diarize: bool = False,
    keywords: Optional[str] = None,
) -> Optional[str]:
    """Upload `audio_path` to 60db /stt and return the transcript string."""
    api_key = os.getenv("SIXTYDB_API_KEY")
    if not api_key:
        raise RuntimeError("SIXTYDB_API_KEY environment variable not set")
    api_base = os.getenv("SIXTYDB_API_BASE", DEFAULT_API_BASE).rstrip("/")

    path = Path(audio_path)
    if not path.is_file():
        print(f"60db STT: file not found: {audio_path}")
        return None

    content_type, _ = mimetypes.guess_type(path.name)
    headers = {"Authorization": f"Bearer {api_key}"}
    data: dict[str, str] = {}
    lang = language or os.getenv("SIXTYDB_STT_LANGUAGE", "auto")
    if lang and lang.lower() != "auto":
        data["language"] = lang
    if diarize:
        data["diarize"] = "true"
    if keywords:
        data["keywords"] = keywords

    try:
        with path.open("rb") as f:
            files = {"file": (path.name, f, content_type or "application/octet-stream")}
            response = requests.post(
                f"{api_base}/stt",
                headers=headers,
                files=files,
                data=data,
                timeout=120,
            )
        response.raise_for_status()
        payload = response.json()
        return (payload.get("text") or "").strip() or None
    except requests.exceptions.RequestException as e:
        print(f"60db STT: error transcribing {audio_path}: {e}")
        return None
