import uuid
from pydub import AudioSegment

from prompts import (
    podcast_ads,
    podcast_intro,
    podcast_outro,
    podcast_segment,
    podcast_segue,
)
from utils import date_stuff, edge_tts_stuff, string_stuff, llmOS_stuff

_SECOND = 1000


def gencast(name, desc, topics, adverts):
    current_date = date_stuff.get_tomorrows_date_for_file_names()
    unique_id = uuid.uuid4()

    # Generate scripts for the topics
    script_segments = []
    for topic in topics:
        script_segment = llmOS_stuff.generate_response(
            podcast_segment.SYSTEM_PROMPT, podcast_segment.PROMPT.format(topic=topic)
        )
        script_segments.append(script_segment)

    # Generate scripts for the advertisements
    script_ads = []
    for advert in adverts:
        script_ad = llmOS_stuff.generate_response(
            podcast_ads.SYSTEM_PROMPT, podcast_ads.PROMPT.format(product=advert)
        )
        script_ads.append(script_ad)

    # Generate an intro for the generated material
    intro = llmOS_stuff.generate_response(
        podcast_intro.SYSTEM_PROMPT,
        podcast_intro.PROMPT.format(
            segment_1=script_segments[0],
            segment_2=script_segments[1],
            segment_3=script_segments[2],
            podcast_name=name,
            podcast_desc=desc,
        ),
    )

    segue_1 = llmOS_stuff.generate_response(
        podcast_segue.SYSTEM_PROMPT,
        podcast_segue.PROMPT.format(
            count_descriptor="first",
            segment=script_segments[0],
        ),
    )

    segue_2 = llmOS_stuff.generate_response(
        podcast_segue.SYSTEM_PROMPT,
        podcast_segue.PROMPT.format(
            count_descriptor="second",
            segment=script_segments[1],
        ),
    )

    segue_3 = llmOS_stuff.generate_response(
        podcast_segue.SYSTEM_PROMPT,
        podcast_segue.PROMPT.format(
            count_descriptor="third",
            segment=script_segments[2],
        ),
    )

    outro = llmOS_stuff.generate_response(
        podcast_outro.SYSTEM_PROMPT,
        podcast_outro.PROMPT.format(
            segment_1=script_segments[0],
            segment_2=script_segments[1],
            segment_3=script_segments[2],
            ad_1=script_ads[0],
            ad_2=script_ads[1],
            podcast_name=name,
            podcast_desc=desc,
        ),
    )

    output_dir = "app/downloads/"

    # Write the script to a file
    output_file = f"{output_dir}{current_date}_{unique_id}.txt"
    with open(output_file, "w+") as script_file:
        script_file.write(
            "\n".join(
                [
                    string_stuff.script_header("Intro"),
                    intro,
                    string_stuff.script_header("Segue 1"),
                    segue_1,
                    string_stuff.script_header("Segment 1"),
                    script_segments[0],
                    string_stuff.script_header("Ad Break 1"),
                    script_ads[0],
                    string_stuff.script_header("Segue 2"),
                    segue_2,
                    string_stuff.script_header("Segment 2"),
                    script_segments[1],
                    string_stuff.script_header("Ad Break 2"),
                    script_ads[1],
                    string_stuff.script_header("Segue 3"),
                    segue_3,
                    string_stuff.script_header("Segment 3"),
                    script_segments[2],
                    string_stuff.script_header("Outro"),
                    outro,
                ]
            )
        )

    # Use elevenlabs to generate the MP3s
    cache_dir = "app/cache/"
    edge_tts_stuff.convert_text_to_mp3(text=intro, filename="intro")
    intro_audio = cache_dir + "intro.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=segue_1, filename="segue_1")
    segue_1_audio = cache_dir + "segue_1.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=segue_2, filename="segue_2")
    segue_2_audio = cache_dir + "segue_2.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=segue_3, filename="segue_3")
    segue_3_audio = cache_dir + "segue_3.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=script_segments[0], filename="segment_1")
    segment_1_audio = cache_dir + "segment_1.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=script_segments[1], filename="segment_2")
    segment_2_audio = cache_dir + "segment_2.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=script_segments[2], filename="segment_3")
    segment_3_audio = cache_dir + "segment_3.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=script_ads[0], filename="advert_1")
    ad_1_audio = cache_dir + "advert_1.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=script_ads[1], filename="advert_2")
    ad_2_audio = cache_dir + "advert_2.mp3"
    edge_tts_stuff.convert_text_to_mp3(text=outro, filename="outro")
    outro_audio = cache_dir + "outro.mp3"

    # Load music segments
    music_forest = AudioSegment.from_mp3("app/music/whistle-vibes-172471.mp3")
    music_beachside = AudioSegment.from_mp3(
        "app/music/lofi-chill-medium-version-159456.mp3"
    )
    music_feriado = AudioSegment.from_mp3("app/music/bolero-161191.mp3")
    music_typewriter = AudioSegment.from_mp3(
        "app/music/scandinavianz-thessaloniki-free-download-173689.mp3"
    )

    # Trim and apply fade outs to music segments
    music_forest = music_forest[: 6 * _SECOND].fade_out(2 * _SECOND)
    music_beachside = music_beachside[: 6 * _SECOND].fade_out(2 * _SECOND)
    music_feriado = music_feriado[: 6 * _SECOND].fade_out(2 * _SECOND)
    music_typewriter = music_typewriter[: 6 * _SECOND].fade_out(2 * _SECOND)

    # Stitch the podcast together
    podcast = music_forest.overlay(intro_audio[:_SECOND], position=5 * _SECOND)
    podcast += intro_audio[_SECOND:]  # Add remaining part of intro_audio
    podcast += AudioSegment.silent(duration=1 * _SECOND)
    podcast += segue_1_audio
    podcast += AudioSegment.silent(duration=1 * _SECOND)
    podcast += music_beachside.overlay(segment_1_audio[:_SECOND], position=5 * _SECOND)
    podcast += segment_1_audio[_SECOND:]  # Add remaining part of segment_1_audio
    podcast += AudioSegment.silent(duration=2 * _SECOND)
    podcast += ad_1_audio
    podcast += AudioSegment.silent(duration=2 * _SECOND)
    podcast += segue_2_audio
    podcast += AudioSegment.silent(duration=1 * _SECOND)
    podcast += music_feriado.overlay(segment_2_audio[:_SECOND], position=5 * _SECOND)
    podcast += segment_2_audio[_SECOND:]  # Add remaining part of segment_2_audio
    podcast += AudioSegment.silent(duration=2 * _SECOND)
    podcast += ad_2_audio
    podcast += AudioSegment.silent(duration=2 * _SECOND)
    podcast += segue_3_audio
    podcast += AudioSegment.silent(duration=1 * _SECOND)
    podcast += music_typewriter.overlay(segment_3_audio[:_SECOND], position=5 * _SECOND)
    podcast += segment_3_audio[_SECOND:]  # Add remaining part of segment_3_audio
    podcast += AudioSegment.silent(duration=2 * _SECOND)
    podcast += music_forest
    podcast += outro_audio

    # Export the final audio file
    output_file = f"{output_dir}{current_date}_{unique_id}.mp3"
    podcast.export(output_file, format="mp3")


def main():
    name = input("Enter name of podcast: ")
    desc = input("Enter description of podcast: ")
    topic1 = input("Enter first topic: ")
    topic2 = input("Enter second topic: ")
    topic3 = input("Enter third topic: ")
    advert1 = input("Enter first advert: ")
    advert2 = input("Enter second advert: ")

    topic = [topic1, topic2, topic3]
    advert = [advert1, advert2]

    gencast(name, desc, topic, advert)


if __name__ == "__main__":
    main()
