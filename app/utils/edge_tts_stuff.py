import asyncio
import edge_tts

VOICE = "en-GB-SoniaNeural"


async def converter(text, filename):
    audio_segment = edge_tts.Communicate(text, VOICE)
    await audio_segment.save("app/cache/" + filename)


def convert_text_to_mp3(text, filename):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(converter(text, filename))
    finally:
        loop.close()
