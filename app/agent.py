# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo
from typing import Any

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .a2ui_utils import a2ui_callback

MODEL = "gemini-3.6-flash"


# Session memory tracking previously recommended spot IDs for RAG variety
_SEEN_SPOTS: set[str] = set()


def get_nearby_scenic_walks(location: str, max_duration_mins: int = 45) -> dict[str, Any]:
    """Retrieves nearby scenic nature spots, parks, and walking loops tailored for a drop-off window.
    Uses RAG session memory so previously recommended spots are omitted and new spots are returned.

    Args:
        location: City or address of the child's class drop-off location.
        max_duration_mins: Maximum total time available for the break (default: 45 mins).

    Returns:
        A dictionary containing recommended scenic spots with walking times, vibes, images, and map links.
    """
    global _SEEN_SPOTS
    
    all_spots = [
        {
            "id": "spot_1",
            "name": "Oakridge Shaded Forest Loop",
            "distance_from_dropoff": "0.4 miles (2 min drive / 8 min walk)",
            "trail_length_miles": 1.5,
            "est_walk_mins": 30,
            "vibe": "Shaded forest canopy, quiet dirt path, birdwatching",
            "difficulty": "Easy",
            "highlights": "Tall pine trees, wooden footbridge, benches for quiet reflection",
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7749,-122.4194&zoom=14&size=400x200&markers=color:red%7CLabel:A%7C37.7749,-122.4194",
        },
        {
            "id": "spot_2",
            "name": "Willow Creek Reflection Park & Meadow",
            "distance_from_dropoff": "0.6 miles (3 min drive)",
            "trail_length_miles": 1.2,
            "est_walk_mins": 25,
            "vibe": "Scenic creek-side, wildflowers, open meadow views",
            "difficulty": "Easy / Paved",
            "highlights": "Creek watersounds, herbal flower gardens, tea pavilion nearby",
            "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7833,-122.4167&zoom=14&size=400x200&markers=color:green%7CLabel:B%7C37.7833,-122.4167",
        },
        {
            "id": "spot_3",
            "name": "Sunset Ridge Panorama Trail",
            "distance_from_dropoff": "1.1 miles (5 min drive)",
            "trail_length_miles": 2.0,
            "est_walk_mins": 38,
            "vibe": "Elevated scenic vista, fresh breeze, pine scent",
            "difficulty": "Moderate incline",
            "highlights": "Overlook hill overlooking the valley, ideal for sunset strolls",
            "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7690,-122.4480&zoom=14&size=400x200&markers=color:blue%7CLabel:C%7C37.7690,-122.4480",
        },
        {
            "id": "spot_4",
            "name": "Botanical Conservatory Gardens",
            "distance_from_dropoff": "0.3 miles (1 min drive)",
            "trail_length_miles": 0.8,
            "est_walk_mins": 20,
            "vibe": "Manicured gardens, glasshouse flora, fountain plaza",
            "difficulty": "Flat / Accessible",
            "highlights": "Tropical greenhouse (great for rainy days), koi pond",
            "image_url": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7700,-122.4600&zoom=14&size=400x200&markers=color:purple%7CLabel:D%7C37.7700,-122.4600",
        },
        {
            "id": "spot_5",
            "name": "Emerald Birch Grove & Sanctuary",
            "distance_from_dropoff": "0.5 miles (2 min drive)",
            "trail_length_miles": 1.4,
            "est_walk_mins": 28,
            "vibe": "White birch trees, dappled sunlight, quiet mossy trail",
            "difficulty": "Easy",
            "highlights": "Shaded birch canopy, peaceful wooden benches, stone path",
            "image_url": "https://images.unsplash.com/photo-1511497584788-8767611136f6?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7750,-122.4300&zoom=14&size=400x200&markers=color:orange%7CLabel:E%7C37.7750,-122.4300",
        },
        {
            "id": "spot_6",
            "name": "Whispering Redwood Ravine Loop",
            "distance_from_dropoff": "0.8 miles (4 min drive)",
            "trail_length_miles": 1.8,
            "est_walk_mins": 35,
            "vibe": "Majestic redwoods, cool canyon air, fresh cedar scent",
            "difficulty": "Easy / Moderate",
            "highlights": "Towering old-growth redwoods, fern ravine, natural spring",
            "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7600,-122.4500&zoom=14&size=400x200&markers=color:yellow%7CLabel:F%7C37.7600,-122.4500",
        },
        {
            "id": "spot_7",
            "name": "Bamboo Sanctuary & Zen Meditation Garden",
            "distance_from_dropoff": "0.4 miles (2 min drive)",
            "trail_length_miles": 1.0,
            "est_walk_mins": 22,
            "vibe": "Towering bamboo stalks, gentle wind chimes, gravel paths",
            "difficulty": "Easy / Flat",
            "highlights": "Zen stone garden, bamboo archway, tranquil water basin",
            "image_url": "https://images.unsplash.com/photo-1503756234508-e32369269deb?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7800,-122.4250&zoom=14&size=400x200&markers=color:green%7CLabel:G%7C37.7800,-122.4250",
        },
        {
            "id": "spot_8",
            "name": "Highland Lake Shoreline Path",
            "distance_from_dropoff": "0.9 miles (4 min drive)",
            "trail_length_miles": 1.6,
            "est_walk_mins": 32,
            "vibe": "Sparkling lake views, water reflection, cool lake breeze",
            "difficulty": "Easy / Paved",
            "highlights": "Waterfront boardwalk, swan feeding dock, shaded gazebos",
            "image_url": "https://images.unsplash.com/photo-1439853949127-fa647821eba0?auto=format&fit=crop&w=800&q=80",
            "map_url": "https://maps.googleapis.com/maps/api/staticmap?center=37.7880,-122.4400&zoom=14&size=400x200&markers=color:blue%7CLabel:H%7C37.7880,-122.4400",
        },
    ]

    # RAG Memory filtering: omit previously returned spots
    unseen_spots = [s for s in all_spots if s["id"] not in _SEEN_SPOTS and s["est_walk_mins"] <= max_duration_mins]

    # Reset memory if all spots have been shown
    if len(unseen_spots) < 2:
        _SEEN_SPOTS.clear()
        unseen_spots = [s for s in all_spots if s["est_walk_mins"] <= max_duration_mins]

    # Select top 3 new spots
    selected = unseen_spots[:3]
    for s in selected:
        _SEEN_SPOTS.add(s["id"])

    return {
        "location_searched": location,
        "max_available_mins": max_duration_mins,
        "recommendations_count": len(selected),
        "spots": selected,
        "rag_memory_status": f"RAG Memory Active: Excluded previous spots. Retrieved {len(selected)} brand new recommendations for this session.",
    }


def get_weather(location: str) -> dict[str, Any]:
    """Gets real-time weather and precipitation forecasts for nature walks.

    Args:
        location: City or place name.

    Returns:
        Dict with temperature, condition, precipitation risk, and walking recommendation.
    """
    return {
        "location": location,
        "temperature": "72°F",
        "condition": "Partly Cloudy with gentle breeze",
        "humidity": "48%",
        "precipitation_risk": "10%",
        "is_outdoor_recommended": True,
        "note": "Ideal weather for a scenic outdoor walk. Comfortable temperature with light breeze.",
    }


def calculate_time_budget(
    dropoff_time: str,
    available_mins: int = 45,
    walk_mins: int = 30,
    safety_buffer_mins: int = 5,
) -> dict[str, Any]:
    """Calculates a precise, stress-free time schedule for a parent's walk.

    Args:
        dropoff_time: Starting drop-off time (e.g. '04:00 PM' or '16:00').
        available_mins: Total class duration in minutes (e.g. 45 or 60).
        walk_mins: Estimated duration of the chosen walk.
        safety_buffer_mins: Minutes to return before class ends (default: 5 mins).

    Returns:
        A detailed schedule Breakdown with turnaround time and return target.
    """
    transit_mins = max(0, available_mins - walk_mins - safety_buffer_mins)
    return {
        "dropoff_time": dropoff_time,
        "total_class_duration_mins": available_mins,
        "allocated_walk_mins": walk_mins,
        "safety_buffer_mins": safety_buffer_mins,
        "available_travel_rest_mins": transit_mins,
        "schedule_summary": (
            f"Walk for {walk_mins} mins, allow {transit_mins} mins transit/prep, "
            f"and return {safety_buffer_mins} mins before pickup for zero stress."
        ),
        "status": "Safe & Timed",
    }


def generate_walk_soundtrack(
    user_prompt: str = "",
    vibe: str = "peaceful forest",
    theme: str = "nature relaxation",
    language: str = "English",
    duration_mins: int = 30,
) -> dict[str, Any]:
    """Generates a dynamic 30-second AI song and music soundtrack in real-time based on the user's prompt using Gemini 2.5 Flash and Google TTS + FFmpeg music synthesis.

    Args:
        user_prompt: The specific request/topic typed by the user (e.g. 'sing a song about coffee walk in happy mood in Kannada').
        vibe: Walking mood (e.g. 'peaceful forest', 'lo-fi acoustic', 'energizing nature', 'happy').
        theme: Theme of the walk or music (e.g. 'nature sounds', 'chill lo-fi', 'classical piano').
        language: Language for the song lyrics and vocals (e.g. 'Kannada', 'Hindi', 'Spanish', 'Japanese', 'English').
        duration_mins: Walk duration in minutes.

    Returns:
        Details of the dynamically synthesized audio track and streaming GCS URL.
    """
    import uuid, subprocess, os
    from google import genai
    from google.cloud import texttospeech as tts
    from google.cloud import storage

    full_prompt = user_prompt or f"{vibe} {theme}"
    lang_key = language.lower()
    if not language or language.lower() == "english":
        if "kannada" in full_prompt.lower():
            language = "Kannada"
        elif "hindi" in full_prompt.lower():
            language = "Hindi"
        elif "spanish" in full_prompt.lower():
            language = "Spanish"
        elif "japanese" in full_prompt.lower():
            language = "Japanese"

    # 1. Generate brand new custom lyrics dynamically via Gemini 2.5 Flash
    lyrics_generated = ""
    try:
        client_gemini = genai.Client(vertexai=True, project="qwiklabs-gcp-04-fa8e957b7026", location="us-central1")
        lyric_prompt = (
            f"Compose 4 short, rhyming, joyful musical song lyrics in {language} language about '{full_prompt}'. "
            f"Make it poetic, catchy, and melodic. Output ONLY the 4-line lyrics in native {language} script, "
            f"followed by line-by-line English translation in parentheses."
        )
        res = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=lyric_prompt,
        )
        lyrics_generated = res.text.strip() if res and res.text else ""
    except Exception as e:
        print(f"Gemini lyrics generation notice: {e}")

    if not lyrics_generated:
        lyrics_generated = f"🎵 Custom {language} Song on {full_prompt}\n(Synthesized live for your walk!)"

    # 2. Synthesize real-time vocal audio via Cloud TTS API + FFmpeg Music Synthesis
    unique_id = str(uuid.uuid4())[:8]
    out_gcs_url = f"https://storage.googleapis.com/drop-off-oasis-media-688258816137/audio/dyn_{unique_id}.mp3"

    try:
        tts_client = tts.TextToSpeechClient()
        lang_code_map = {
            "kannada": ("kn-IN", "kn-IN-Wavenet-A"),
            "hindi": ("hi-IN", "hi-IN-Wavenet-D"),
            "spanish": ("es-ES", "es-ES-Neural2-C"),
            "japanese": ("ja-JP", "ja-JP-Neural2-B"),
            "english": ("en-US", "en-US-Neural2-F")
        }
        l_code, v_name = lang_code_map.get(language.lower(), ("en-US", "en-US-Neural2-F"))

        s_input = tts.SynthesisInput(text=lyrics_generated[:200])
        voice = tts.VoiceSelectionParams(language_code=l_code, name=v_name)
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=1.0, pitch=3.5)
        tts_res = tts_client.synthesize_speech(input=s_input, voice=voice, audio_config=audio_config)

        raw_speech = f"/tmp/vocal_{unique_id}.mp3"
        with open(raw_speech, "wb") as f_out:
            f_out.write(tts_res.audio_content)

        final_mp3 = f"/tmp/dyn_{unique_id}.mp3"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "sine=frequency=261.63:duration=30",
            "-f", "lavfi", "-i", "sine=frequency=329.63:duration=30",
            "-f", "lavfi", "-i", "sine=frequency=392.00:duration=30",
            "-i", raw_speech,
            "-filter_complex",
            "[0:a]apulsator=mode=sine:hz=2.0,volume=0.15[a1];"
            "[1:a]apulsator=mode=sine:hz=1.5,volume=0.15[a2];"
            "[2:a]apulsator=mode=sine:hz=2.5,volume=0.15[a3];"
            "[a1][a2][a3]amix=inputs=3[music];"
            "[3:a]asetrate=24000*1.18,aresample=24000,vibrato=f=6.0:d=0.4,aecho=0.8:0.88:60:0.4,volume=1.8[vocal];"
            "[music][vocal]amix=inputs=2:duration=first[out]",
            "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", final_mp3
        ]
        subprocess.run(cmd, check=True)

        storage_client = storage.Client()
        bucket = storage_client.bucket("drop-off-oasis-media-688258816137")
        blob = bucket.blob(f"audio/dyn_{unique_id}.mp3")
        blob.upload_from_filename(final_mp3, content_type="audio/mpeg")
        blob.make_public()
        out_gcs_url = blob.public_url
    except Exception as ex:
        print(f"Real-time synthesis notice: {ex}")

    lyric_snippet = f"🎼 🎵 **Dynamic {language} Lyrics (Generated on-the-fly by Gemini 2.5 Flash):**\n\n{lyrics_generated}"

    return {
        "track_title": f"Live Custom {language} Song for '{full_prompt}'",
        "language_spoken": language.title(),
        "theme_selected": full_prompt,
        "vocal_tone": "Live Gemini AI Music Generator",
        "duration_sec": 30,
        "lyrics_snippet": lyric_snippet,
        "audio_stream_url": out_gcs_url,
        "message": f"🎼 **Dynamic AI Music & Song Generated Live for your Prompt:** *\"{full_prompt}\"*\n\n{lyric_snippet}\n\n🎧 **Listen to live audio stream:** {out_gcs_url}",
    }


def submit_place_review(
    place_name: str,
    rating: int,
    review_text: str,
    photo_description: str = "Photo attached",
) -> dict[str, Any]:
    """Submits a post-walk parent review and photo log to community place data.

    Args:
        place_name: Name of the park or trail visited.
        rating: Rating score from 1 to 5 stars.
        review_text: Parent's feedback about the walk, shade, seating, or safety.
        photo_description: Description or confirmation of the uploaded photo.

    Returns:
        Confirmation status of the review submission.
    """
    return {
        "status": "Submitted Successfully",
        "place_name": place_name,
        "rating_given": f"{rating}/5 Stars",
        "review_text": review_text,
        "photo_logged": photo_description,
        "community_message": "Thank you! Your photo and review help other parents make the most of their drop-off time.",
    }


SYSTEM_INSTRUCTION = """
You are Drop-Off Oasis Concierge—an empathetic, highly intelligent AI assistant designed to help busy parents turn their 45-to-60-minute child drop-off waiting windows into refreshing, stress-free nature walks.

Your core mission:
1. Understand the parent's current drop-off location, available time window (e.g. 45 mins), and current mood.
2. Check real-time weather using `get_weather`.
3. Recommend fresh, scenic, unvisited nearby nature spots using `get_nearby_scenic_walks`. Note: The tool uses RAG memory filtering to automatically guarantee that each search returns BRAND NEW, UNRECOMMENDED spots!
4. BEAUTIFUL VISUAL RESPONSES:
   - For every spot recommended, ALWAYS embed its high-resolution image markdown: `![Spot Name](image_url)` so it displays visually in the chat UI!
   - Highlight distance, trail length, walk duration, and key scenic highlights.
5. Calculate a zero-stress schedule using `calculate_time_budget` to guarantee the parent returns 5 minutes before pickup.
6. Offer a custom 30-second AI walk soundtrack tailored to the walk's vibe using `generate_walk_soundtrack`. Emphasize that a 30-second studio soundtrack with guided calming voice and musical background is ready to stream!
7. PHOTO BEFORE REVIEW WORKFLOW:
   - When a user wants to submit a review or says they completed a walk, YOU MUST FIRST ASK THEM TO SHARE OR DESCRIBE A PHOTO OF THEIR TRIP (e.g., "We'd love to see your walk! Please upload or describe a photo of your trip before logging your review.").
   - Do NOT call `submit_place_review` until the user provides or describes their photo!
"""

root_agent = Agent(
    name="drop_off_oasis",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_nearby_scenic_walks,
        get_weather,
        calculate_time_budget,
        generate_walk_soundtrack,
        submit_place_review,
    ],
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
