import asyncio
import edge_tts

VOICE = "en-GB-SoniaNeural"


async def converter(text, filename):
    audio_segment = edge_tts.Communicate(text, VOICE)
    await audio_segment.save("app/cache/" + filename)


def convert_text_to_mp3(text, filename):
    loop = asyncio.get_event_loop_policy().get_event_loop()
    audio_segment = loop.run_until_complete(converter(text, filename))
    return audio_segment
