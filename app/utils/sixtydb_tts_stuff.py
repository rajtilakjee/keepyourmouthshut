"""60db TTS — peer of edge_tts_stuff.

Exposes the same `convert_text_to_mp3(text, filename)` signature
generate_podcast.py already uses, so swapping providers is a single
import-line change (handled in generate_podcast.py based on env).

Three transport surfaces, picked by SIXTYDB_TTS_TRANSPORT:
    sync   (default) — POST /tts-synthesize, one-shot mp3 in JSON
    stream            — POST /tts-stream, NDJSON of base64 mp3 chunks
    ws                — wss://api.60db.ai/ws/tts, LINEAR16 @ 24k

For this batch-podcast pipeline the sync surface is the natural fit;
the other two are exposed for completeness so users with realtime needs
have them available.

Reference: https://docs.60db.ai
"""

from __future__ import annotations

import asyncio
import base64
import io
import json
import os
from pathlib import Path

import requests

DEFAULT_API_BASE = "https://api.60db.ai"
DEFAULT_VOICE_ID = "fbb75ed2-975a-40c7-9e06-38e30524a9a1"
CACHE_DIR = "app/cache/"


def _config() -> tuple[str, str, str, str]:
    """Return (api_base, api_key, voice_id, transport). Raises on missing key."""
    api_key = os.getenv("SIXTYDB_API_KEY")
    if not api_key:
        raise RuntimeError("SIXTYDB_API_KEY environment variable not set")
    api_base = os.getenv("SIXTYDB_API_BASE", DEFAULT_API_BASE).rstrip("/")
    voice_id = os.getenv("SIXTYDB_TTS_VOICE_ID", DEFAULT_VOICE_ID)
    transport = os.getenv("SIXTYDB_TTS_TRANSPORT", "sync").strip().lower()
    return api_base, api_key, voice_id, transport


def convert_text_to_mp3(text: str, filename: str) -> None:
    """Synthesize `text` via 60db and write the mp3 to `app/cache/{filename}`.

    Same signature as edge_tts_stuff.convert_text_to_mp3 so the call sites
    in generate_podcast.py do not change.
    """
    api_base, api_key, voice_id, transport = _config()
    out_path = Path(CACHE_DIR) / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if transport == "stream":
        _synth_ndjson(text, voice_id, api_base, api_key, out_path)
    elif transport == "ws":
        _synth_ws(text, voice_id, api_base, api_key, out_path)
    else:
        _synth_sync(text, voice_id, api_base, api_key, out_path)


# ---- sync REST -------------------------------------------------------------


def _synth_sync(text: str, voice_id: str, api_base: str, api_key: str, out_path: Path) -> None:
    payload = {
        "text": text,
        "voice_id": voice_id,
        "enhance": True,
        "speed": 1,
        "stability": 50,
        "similarity": 75,
        "output_format": "mp3",
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(f"{api_base}/tts-synthesize", json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    if not data.get("success") or not data.get("audio_base64"):
        raise RuntimeError(f"60db tts-synthesize empty: {data.get('message')}")
    out_path.write_bytes(base64.b64decode(data["audio_base64"]))


# ---- NDJSON stream ---------------------------------------------------------


def _synth_ndjson(text: str, voice_id: str, api_base: str, api_key: str, out_path: Path) -> None:
    payload = {"text": text, "voice_id": voice_id, "output_format": "mp3"}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    chunks: list[bytes] = []
    with requests.post(
        f"{api_base}/tts-stream", json=payload, headers=headers, stream=True, timeout=120
    ) as r:
        r.raise_for_status()
        for raw in r.iter_lines(decode_unicode=True):
            line = (raw or "").strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("type") == "error":
                raise RuntimeError(f"60db tts-stream error: {line[:200]}")
            if msg.get("type") == "complete":
                break
            content = msg.get("audioContent")
            if content:
                chunks.append(base64.b64decode(content))
    out_path.write_bytes(b"".join(chunks))


# ---- WebSocket -------------------------------------------------------------


def _synth_ws(text: str, voice_id: str, api_base: str, api_key: str, out_path: Path) -> None:
    """LINEAR16 24 kHz PCM via WS — wrapped in a WAV header then transcoded
    to mp3 via pydub (already in the project's deps)."""
    try:
        import websockets
    except ImportError as e:
        raise RuntimeError(
            "SIXTYDB_TTS_TRANSPORT=ws requires the 'websockets' package"
        ) from e
    from pydub import AudioSegment

    pcm = asyncio.new_event_loop().run_until_complete(
        _ws_collect(text, voice_id, api_base, api_key)
    )
    if not pcm:
        raise RuntimeError("60db ws/tts returned no audio")
    wav_bytes_io = io.BytesIO(pcm)
    seg = AudioSegment(
        data=wav_bytes_io.getvalue(),
        sample_width=2,
        frame_rate=24000,
        channels=1,
    )
    seg.export(out_path, format="mp3")


async def _ws_collect(text: str, voice_id: str, api_base: str, api_key: str) -> bytes:
    import websockets

    ws_base = api_base.replace("https://", "wss://").replace("http://", "ws://")
    url = f"{ws_base}/ws/tts?apiKey={api_key}"
    context_id = f"ctx-{os.getpid()}"
    pcm_chunks: list[bytes] = []
    async with websockets.connect(url, max_size=None) as ws:
        async for raw in ws:
            msg = json.loads(raw)
            if "connection_established" in msg:
                await ws.send(json.dumps({
                    "create_context": {
                        "context_id": context_id,
                        "voice_id": voice_id,
                        "audio_config": {"audio_encoding": "LINEAR16", "sample_rate_hertz": 24000},
                    }
                }))
                continue
            if "context_created" in msg:
                await ws.send(json.dumps({"send_text": {"context_id": context_id, "text": text}}))
                await ws.send(json.dumps({"flush_context": {"context_id": context_id}}))
                continue
            chunk_b64 = msg.get("audio_chunk", {}).get("audioContent")
            if chunk_b64:
                pcm_chunks.append(base64.b64decode(chunk_b64))
                continue
            if "flush_completed" in msg:
                try:
                    await ws.send(json.dumps({"close_context": {"context_id": context_id}}))
                except Exception:
                    pass
                break
    return b"".join(pcm_chunks)
