import io

from elevenlabs import Voice, VoiceSettings, generate
from pydub import AudioSegment

_LIMIT = 4900

HOST_VOICE = Voice(
    voice_id="r31dnNrpatHkOShYZdYQ",
    name="Mia",
    category="generated",
    settings=VoiceSettings(
        stability=0.35, similarity_boost=0.9, style=0.0, use_speaker_boost=True
    ),
)

ADS_VOICE = Voice(
    voice_id="LQITRrHstASVE8MDit6F",
    name="Johnathan",
    category="generated",
    settings=VoiceSettings(
        stability=0.35, similarity_boost=0.9, style=0.0, use_speaker_boost=True
    ),
)


def load_audio_bytes(audio_bytes):
    audio_file = io.BytesIO(audio_bytes)
    audio_segment = AudioSegment.from_file(audio_file, format="mp3")
    return audio_segment


def convert_text_to_mp3(text, voice):
    if len(text) > _LIMIT:
        # Split the text into chunks that are within the API limit
        chunks = [text[i : i + _LIMIT] for i in range(0, len(text), _LIMIT)]
    else:
        chunks = [text]

    audio_segments = []
    for chunk in chunks:
        # Generate voiceover for each chunk separately
        chunk_voice_over = load_audio_bytes(generate(text=chunk, voice=voice))
        audio_segments.append(chunk_voice_over)

    # Concatenate audio segments to form the final audio output
    audio_output = audio_segments[0]
    for segment in audio_segments[1:]:
        audio_output += segment

    return audio_output
