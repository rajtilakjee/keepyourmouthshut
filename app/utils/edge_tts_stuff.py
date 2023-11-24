import asyncio
import edge_tts as et

VOICE = "en-GB-SoniaNeural"


def convert_text_to_mp3(text, filename):
    async def wrapper():
        c = et.Communicate(text, VOICE)
        await c.save("app/cache/" + filename + ".mp3")

    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(wrapper())
    finally:
        loop.close()
