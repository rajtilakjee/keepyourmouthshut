import asyncio
import edge_tts

VOICE = "en-GB-SoniaNeural"


def convert_text_to_mp3(text):
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        audio_segment = loop.run_until_complete(edge_tts.Communicate(text, VOICE))
    finally:
        return audio_segment
