import asyncio
import edge_tts

VOICE = "en-GB-SoniaNeural"


async def converter(text, filename):
    """
    Asynchronously convert text to an audio segment and save it as an MP3 file.

    Args:
        text (str): The text to be converted to audio.
        filename (str): The desired filename for the resulting MP3 file.

    This function utilizes an asynchronous approach to convert the given text into an audio
    segment using the `edge_tts.Communicate` method with a specified voice. The resulting
    audio segment is then saved as an MP3 file in the 'app/cache/' directory.

    Note:
        - This function should be awaited when called.

    Example:
        await converter("Hello, world!", "output.mp3")
    """
    audio_segment = edge_tts.Communicate(text, VOICE)
    await audio_segment.save("app/cache/" + filename)


def convert_text_to_mp3(text, filename):
    """
    Convert text to an audio segment and save it as an MP3 file.

    Args:
        text (str): The text to be converted to audio.
        filename (str): The desired filename for the resulting MP3 file.

    This function is a synchronous wrapper for the asynchronous `converter` function. It
    sets up an event loop, runs the asynchronous function, and then closes the loop.

    Note:
        - This function is suitable for use in synchronous code.
        - For asynchronous contexts, it is recommended to use the `converter` function directly.

    Example:
        convert_text_to_mp3("Hello, world!", "output.mp3")
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(converter(text, filename))
    finally:
        loop.close()
