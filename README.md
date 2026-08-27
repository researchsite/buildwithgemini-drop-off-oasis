# 🌿 Drop-Off Oasis: 45-Minute Parent Walk & Micro-Break Concierge

> **Turn child drop-off waiting windows (45–60 minutes) into refreshing, zero-stress nature walks, complete with RAG memory, dynamic 30-second studio audio soundtracks with news briefings, visual map previews, and post-walk photo reviews.**

[![Google ADK](https://img.shields.io/badge/Google%20ADK-2.5.0-green.svg)](https://google.github.io/adk-docs/)
[![Gemini 3.6 Flash](https://img.shields.io/badge/Model-Gemini%203.6%20Flash-blue.svg)](https://cloud.google.com/vertex-ai/generative-ai/docs)
[![Vertex AI Agent Runtime](https://img.shields.io/badge/Deployment-Agent%20Runtime-orange.svg)](https://cloud.google.com/vertex-ai)
[![FastAPI](https://img.shields.io/badge/Proxy-FastAPI%20A2A-009688.svg)](https://fastapi.tiangolo.com)

---

## 💡 The Problem & The Solution

### **The Problem**
Parents dropping off their children for 45-to-60-minute extracurricular classes (music, gymnastics, sports) often face an awkward time window. It’s too short to drive home and back, yet too long to sit idly in a parked car.

### **The Solution: Drop-Off Oasis**
**Drop-Off Oasis** is a personalized AI concierge built on Google's Agent Development Kit (ADK) and Vertex AI Agent Engine. It recommends nearby shaded nature walks, calculates exact zero-stress return schedules (guaranteeing pickup 5 minutes before class ends), generates dynamic 30-second audio soundtracks with daily nature news briefings, and logs community photo reviews!

---

## 🎬 Live Application Walkthrough

![Drop-Off Oasis Live Application Walkthrough](docs/demo_walkthrough.gif)

---

## 🌟 Key Features

1. **🧠 RAG Session Memory (Zero Duplicate Recommendations)**:
   - Maintains active memory filtering (`_SEEN_SPOTS`) across a database of 10+ distinct nature spots (*Redwood Glen*, *Whispering Pines Canyon*, *Heritage Oak Valley*, *Bamboo Sanctuary*, *Emerald Birch Grove*, *Highland Lake*, etc.).
   - Each search automatically excludes previously returned spots so parents get **brand-new, unvisited nature spots every single turn**.

2. **🎧 Dynamic Multi-Language & Multi-Theme 30-Second Audio Generation**:
   - Dynamically synthesizes a 30-second studio audio track per request taking **Language** (*Kannada*, *Hindi*, *English*, *Spanish*, *French*, *German*, *Japanese*) and **Theme** (*lo-fi beats*, *nature relaxation*, *ambient meditation*, *upbeat acoustic*).
   - Combines **Google Cloud Text-to-Speech (Neural2 / Standard voice guidance)** with custom harmonic music scores.
   - Uploads automatically to Google Cloud Storage (`gs://drop-off-oasis-media-688258816137/audio/`) and streams directly via an embedded HTML5 `<audio controls>` player in the chat UI.

3. **📸 Photo-First Review Workflow**:
   - Prompts parents to upload or describe a photo of their walk (e.g. redwood canopy, wooden bridge, wildflower path) *before* saving community reviews.

4. **🖼️ Rich Visual UI (Embedded Images, Maps & A2UI Cards)**:
   - Parses markdown images `![alt](url)` and renders high-res responsive nature photography cards.
   - Includes Google Static Maps location previews and native A2UI rich cards.

---

## 🏗️ System Architecture

![Architecture Diagram](docs/architecture_diagram.png)

### Data Flow Overview:
1. **User Browser**: Sends chat prompts over HTTP to the FastAPI Proxy (`frontend/main.py`).
2. **FastAPI A2A Proxy (Port 8085)**: Rewrites internal container endpoints, connects over **A2A Protocol**, and streams responses back to the browser.
3. **Vertex AI Agent Runtime**: Hosts the ADK Agent (`app/agent.py`) on Vertex AI ReasoningEngine (`projects/688258816137/locations/us-east1/reasoningEngines/651104397689880576`).
4. **Google Cloud Services**:
   - **Google Cloud Text-to-Speech API**: Synthesizes Neural2 voice narration for walk briefings and nature news.
   - **Google Cloud Storage (GCS)**: Stores and serves 30-second studio MP3 audio files.
   - **Gemini 3.6 Flash**: Generative AI reasoning model.

---

## 🧩 Component Blueprint

![Component Diagram](docs/component_diagram.png)

### Codebase File Structure:

```
drop-off-oasis/
├── app/
│   ├── agent.py               # Core ADK Agent, system instructions & 5 function tools
│   └── a2ui_utils.py          # A2UI card renderer callback helper
├── frontend/
│   ├── main.py                # FastAPI A2A Proxy server (Port 8085)
│   └── static/
│       └── index.html         # Web Chat UI with A2UI card & HTML5 audio streamer
├── docs/
│   ├── architecture_diagram.svg # Visual System Architecture Diagram
│   └── component_diagram.svg    # Detailed Codebase File Component Diagram
├── pyproject.toml             # Project manifest & Python dependencies
└── README.md                  # Project documentation
```

---

## 🛠️ Tool Definitions in `app/agent.py`

| Tool | Functionality |
| :--- | :--- |
| `get_nearby_scenic_walks` | RAG memory-driven search retrieving 3 new unvisited nature spots with Unsplash imagery and map markers. |
| `generate_walk_soundtrack` | Synthesizes a 30-second dynamic MP3 audio soundtrack with Google TTS nature news & 432Hz ambient music score. |
| `calculate_time_budget` | Calculates exact walking time, transit prep, and safety buffer to return 5 minutes before pickup. |
| `submit_place_review` | Logs parent community reviews and attached trip photo descriptions. |
| `get_weather` | Retrieves real-time weather and precipitation risks for outdoor walks. |

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
