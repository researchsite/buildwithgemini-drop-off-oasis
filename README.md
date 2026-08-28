# 🌿 Drop-Off Oasis: 45-Minute Parent Walk & Micro-Break Concierge

> **Turn child drop-off waiting windows (45–60 minutes) into refreshing, zero-stress nature walks, complete with RAG memory, Gemini 2.5 Flash singing audio soundtracks, interactive Leaflet maps, parent walk buddies, and wellness streak tracking.**

[![Google ADK](https://img.shields.io/badge/Google%20ADK-2.5.0-green.svg)](https://google.github.io/adk-docs/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Model-Gemini%202.5%20Flash-blue.svg)](https://cloud.google.com/vertex-ai/generative-ai/docs)
[![Vertex AI Agent Runtime](https://img.shields.io/badge/Deployment-Agent%20Runtime-orange.svg)](https://cloud.google.com/vertex-ai)
[![FastAPI](https://img.shields.io/badge/Proxy-FastAPI%20A2A-009688.svg)](https://fastapi.tiangolo.com)
[![Leaflet Maps](https://img.shields.io/badge/Maps-OpenStreetMap%20Leaflet-brightgreen.svg)](https://leafletjs.com/)
[![Firestore](https://img.shields.io/badge/Database-Cloud%20Firestore-ffca28.svg)](https://cloud.google.com/firestore)

---

## 💡 The Problem & The Solution

### **The Problem**
Parents dropping off their children for 45-to-60-minute extracurricular classes (music, gymnastics, sports) often face an awkward time window. It’s too short to drive home and back, yet too long to sit idly in a parked car.

### **The Solution: Drop-Off Oasis**
**Drop-Off Oasis** is a personalized AI concierge built on Google's Agent Development Kit (ADK) and Vertex AI Agent Engine. It recommends nearby shaded nature walks, calculates exact zero-stress return schedules (guaranteeing pickup 5 minutes before class ends), generates dynamic 30-second Gemini 2.5 Flash singing soundtracks over rhythmic beats, connects parent walk buddies, and logs community photo reviews!

---

## 🎬 Live Application Walkthrough

![Drop-Off Oasis Live Application Walkthrough](docs/demo_walkthrough.gif)

---

## 🌟 Key Features (7 Core Capability Tools)

1. **🧠 RAG Session Memory (Zero Duplicate Recommendations)**:
   - Maintains active memory filtering (`_SEEN_SPOTS`) across a database of distinct nature spots (*Redwood Glen*, *Whispering Pines Canyon*, *Heritage Oak Valley*, *Bamboo Sanctuary*, *Emerald Birch Grove*, *Highland Lake*, etc.).
   - Each search automatically excludes previously returned spots so parents get **brand-new, unvisited nature spots every single turn**.

2. **🎼 Gemini 2.5 Flash Native Singing & Rhythmic Beat Soundtrack Generation**:
   - Dynamically composes custom 30-second MP3 audio soundtracks in multiple languages (*Kannada*, *Hindi*, *English*, *Spanish*, *Japanese*) using `gemini-2.5-flash-preview-tts` for expressive singing vocals over dynamic FFmpeg `aevalsrc` rhythmic arpeggiated beats.
   - Uploads automatically to Google Cloud Storage (`gs://drop-off-oasis-media-688258816137/audio/`) and streams directly via an embedded HTML5 `<audio controls>` player in the chat UI.

3. **🗺️ Interactive Split-Panel Leaflet Route Mapping**:
   - Displays an interactive OpenStreetMap Leaflet map panel. Clicking "📍 Show Walking Route on Map" plots the trailhead marker and draws a walking route polyline dynamically.

4. **☀️ Live Open-Meteo Weather, AQI & UV Dashboard**:
   - Checks live weather conditions, air quality index (AQI), humidity, and UV safety warnings, providing a Walk Suitability Meter (0-10) for safe outdoor micro-breaks.

5. **👥 Walk Buddy Parent Matching**:
   - Matches nearby parent drop-off walkers based on class schedule overlap and trail preferences for community walking sessions.

6. **🔥 Wellness Streak & Badge Tracking**:
   - Logs completed parent nature walks into Cloud Firestore and awards streak badges (*First Step*, *3-Walk Streak*, *Nature Regular*).

7. **📸 Photo-First Review Workflow**:
   - Prompts parents to upload or describe a photo of their walk (e.g. redwood canopy, wooden bridge, wildflower path) before saving community reviews to Cloud Firestore.

---

## 🏗️ System Architecture

![Architecture Diagram](docs/architecture_diagram.png)

### Data Flow Overview:
1. **User Browser**: Split-panel UI (Leaflet Map + Material Design 3 Chat) sending prompts over HTTP to the FastAPI Proxy (`frontend/main.py`).
2. **FastAPI A2A Proxy (Port 8085)**: Rewrites internal container endpoints, connects over **A2A Protocol** with artifact tracking (`artifacts_latest`), and streams responses back to the browser.
3. **Vertex AI Agent Runtime**: Hosts the ADK Agent (`app/agent.py`) on Vertex AI ReasoningEngine (`projects/688258816137/locations/us-east1/reasoningEngines/651104397689880576`).
4. **Google Cloud Services**:
   - **Gemini 2.5 Flash Native Audio**: Generates expressive singing voice audio tracks.
   - **Open-Meteo Live API**: Supplies real-time weather and air quality metrics.
   - **Cloud Firestore**: Persists parent reviews, walk streaks, and community photos.
   - **Google Cloud Storage (GCS)**: Stores and serves 30-second studio MP3 audio files and user trip photos.

---

## 🧩 Component Blueprint

![Component Diagram](docs/component_diagram.png)

### Codebase File Structure:

```
drop-off-oasis/
├── app/
│   ├── agent.py               # Core ADK Agent, system instructions & 7 function tools
│   └── a2ui_utils.py          # A2UI card renderer callback helper
├── frontend/
│   ├── main.py                # FastAPI A2A Proxy server (Port 8085)
│   └── static/
│       └── index.html         # Split-Panel Web UI with Leaflet Map & Rich Card Renderer
├── docs/
│   ├── architecture_diagram.png # System Architecture Diagram
│   ├── component_diagram.png    # Codebase File Component Diagram
│   ├── USER_GUIDE_AND_DEMO_SCRIPT.md # Detailed Demo Script
│   └── LEARNINGS_AND_PROMPTS.md      # Key Engineering Learnings
├── pyproject.toml             # Project manifest & Python dependencies
└── README.md                  # Project documentation
```

---

## 🛠️ Tool Definitions in `app/agent.py`

| Tool | Functionality |
| :--- | :--- |
| `get_nearby_scenic_walks` | RAG memory-driven search retrieving 3 new unvisited nature spots with Unsplash imagery and interactive Leaflet map route triggers. |
| `generate_walk_soundtrack` | Synthesizes a 30-second dynamic MP3 audio soundtrack with Gemini 2.5 Flash singing vocals & FFmpeg rhythmic beats. |
| `calculate_time_budget` | Calculates exact walking time, transit prep, and safety buffer to return 5 minutes before pickup. |
| `get_weather` | Retrieves real-time weather, AQI, and UV index for outdoor walks via Open-Meteo. |
| `find_walk_buddy` | Matches nearby parent drop-off walkers by schedule and route preference. |
| `log_walk_streak` | Tracks parent wellness walk streaks and badges in Cloud Firestore. |
| `submit_place_review` | Logs parent community reviews and attached trip photo descriptions in Cloud Firestore. |

---

## 🚀 Quickstart & Local Execution

### 1. Install Dependencies
```bash
uv sync
```

### 2. Set GCP Project Environment
```bash
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-04-fa8e957b7026"
export GOOGLE_CLOUD_LOCATION="us-east1"
```

### 3. Run Web Application & Proxy Server
```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="projects/688258816137/locations/us-east1/reasoningEngines/651104397689880576"
export AGENT_DIRECTORY="app"
export PORT=8085
uv run python main.py
```
Open **[http://127.0.0.1:8085/](http://127.0.0.1:8085/)** in your browser!

---

## ☁️ Deployment to Agent Runtime

Deploy the agent to Google Cloud Vertex AI Agent Engine using `agents-cli`:

```bash
agents-cli deploy -d agent_runtime --project qwiklabs-gcp-04-fa8e957b7026 --no-confirm-project
```

---

## 📜 License
Copyright 2026 Google LLC. Licensed under the Apache License, Version 2.0.
