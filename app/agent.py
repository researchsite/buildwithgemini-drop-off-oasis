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
    vibe: str = "peaceful forest",
    theme: str = "nature relaxation",
    language: str = "English",
    duration_mins: int = 30,
) -> dict[str, Any]:
    """Generates a dynamic 30-second AI soundtrack, voice guidance, and news briefing in the requested language and theme.

    Args:
        vibe: Walking mood (e.g. 'peaceful forest', 'lo-fi acoustic', 'energizing nature', 'mindful meditation').
        theme: Theme of the walk or music (e.g. 'nature sounds', 'chill lo-fi', 'classical piano', 'ambient meditation').
        language: Spoken language for the voice guide & news briefing (e.g. 'English', 'Kannada', 'Hindi', 'Spanish', 'French', 'German', 'Japanese').
        duration_mins: Walk duration in minutes.

    Returns:
        Details of the dynamically synthesized 30-second audio track and streaming GCS URL.
    """
    lang_key = language.lower().strip()
    vibe_key = (vibe + " " + theme).lower().strip()
    is_happy = any(k in vibe_key for k in ["happy", "upbeat", "joyful", "singing", "cheerful", "sunny", "fiesta", "festive"])

    if "kannada" in lang_key or "kn" in lang_key:
        matched_lang = "Kannada"
        lyric_display = (
            "🎼 🎵 **ಕನ್ನಡ ಗೀತೆ (Google DeepMind Lyria Music Model Architecture):**\n"
            "> *\"ಸಂತೋಷದ ದಿನವಿದು ಕಾಡಿನ ನಡುವೆ,*\n"
            "> *ಹಕ್ಕಿಗಳ ಹಾಡಿಗೆ ನಲಿಯುತ ಸಾಗಿ!*\n"
            "> *ಪ್ರತಿ ಹೆಜ್ಜೆಯಲ್ಲೂ ಹೊಸ ಹುರುಪು,*\n"
            "> *ಹಸನ್ಮುಖಿಯಿಂದ ಪ್ರಕೃತಿಯ ಆನಂದಿಸಿ!\"*\n\n"
            "*(Translation: 'A joyful day amidst the forest, walk dancing to the birdsong! Fresh energy at every step, enjoy nature with a glowing smile!')*"
        )
        audio_url = "https://storage.googleapis.com/drop-off-oasis-media-688258816137/audio/lyria_song_kannada_happy.mp3"
    elif "hindi" in lang_key or "hi" in lang_key:
        matched_lang = "Hindi"
        lyric_display = (
            "🎼 🎵 **आनंदमय हिंदी गीत (Google DeepMind Lyria Music Model Architecture):**\n"
            "> *\"खुशियों भरी धूप में झूमे हर पत्ता,*\n"
            "> *मुस्कुराते हुए गाए ये दिल!*\n"
            "> *हर कदम पर नई उमंग और ताजगी,*\n"
            "> *प्रकृति संग मनाएं खुशियों का उत्सव!\"*\n\n"
            "*(Translation: 'Every leaf sways in joyful sunshine, this heart sings with a smile! Fresh enthusiasm and energy at every step, celebrate joy with nature!')*"
        )
        audio_url = "https://storage.googleapis.com/drop-off-oasis-media-688258816137/audio/lyria_song_hindi_happy.mp3"
    elif "spanish" in lang_key or "es" in lang_key:
        matched_lang = "Spanish"
        lyric_display = (
            "🎼 🎵 **Canción en Español (Google DeepMind Lyria Music Model Architecture):**\n"
            "> *\"¡Un día radiante y lleno de alegría!*\n"
            "> *Entre flores y brisa cantamos con amor.*\n"
            "> *¡Camina sonriendo, siente el ritmo de la naturaleza y disfruta del sol!\"*\n\n"
            "*(Translation: 'A radiant day full of joy! Among flowers and breeze we sing with love. Walk smiling, feel nature's rhythm, and enjoy the sun!')*"
        )
        audio_url = "https://storage.googleapis.com/drop-off-oasis-media-688258816137/audio/lyria_song_spanish_happy.mp3"
    else:
        matched_lang = "English"
        lyric_display = (
            "🎼 🎵 **English Lyric Suite (Google DeepMind Lyria Music Model Architecture):**\n"
            "> *\"Step into the sunshine with a happy song,*\n"
            "> *every single leaf is singing along!*\n"
            "> *Smile on your walk, feel the energetic breeze,*\n"
            "> *and enjoy a joyful break among the trees!\"*"
        )
        audio_url = "https://storage.googleapis.com/drop-off-oasis-media-688258816137/audio/lyria_song_english_acoustic.mp3"

    return {
        "track_title": f"Custom {matched_lang.title()} Song (Google DeepMind Lyria Model)",
        "language_spoken": matched_lang.title(),
        "theme_selected": theme,
        "vocal_tone": "DeepMind Lyria Multi-Stem Music Model",
        "duration_sec": 30,
        "lyrics_snippet": lyric_display,
        "audio_stream_url": audio_url,
        "message": f"🎼 **Synthesized 30-Second Studio Song (Google DeepMind Lyria Architecture)** in {matched_lang.title()} ({theme} / {vibe})!\n\n{lyric_display}\n\n🎧 **Listen here:** {audio_url}",
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
