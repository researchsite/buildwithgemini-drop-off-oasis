# 📚 Drop-Off Oasis: Learnings, Prompts & Troubleshooting Guide

> **A complete record of all user prompts, reported runtime errors, root causes, and technical solutions applied during the development of the Drop-Off Oasis agentic application.**

---

## 📑 Table of Contents
1. [Chronological User Prompts](#1-chronological-user-prompts)
2. [Reported Errors & Technical Solutions](#2-reported-errors--technical-solutions)
   - [Error 1: Protobuf Mismatch (AgentCard supportedInterfaces)](#error-1-protobuf-mismatch-agentcard-supportedinterfaces)
   - [Error 2: Internal Container Host Connection Errors (0.0.0.0:8000)](#error-2-internal-container-host-connection-errors-00008000)
   - [Error 3: Missing Audio Storage & Mock Soundtrack URLs](#error-3-missing-audio-storage--mock-soundtrack-urls)
   - [Error 4: RAG Recommending Duplicate Nature Spots](#error-4-rag-recommending-duplicate-nature-spots)
   - [Error 5: Plain Text Links Instead of In-App Images & Maps](#error-5-plain-text-links-instead-of-in-app-images--maps)
   - [Error 6: Skipping Photo Attachment Before Review Submission](#error-6-skipping-photo-attachment-before-review-submission)
   - [Error 7: Agent Engine Cloud Build Deployment Failure (Code 3)](#error-7-agent-engine-cloud-build-deployment-failure-code-3)
3. [Key Architecture Patterns & Lessons Learned](#3-key-architecture-patterns--lessons-learned)

---

## 1. Chronological User Prompts

Below is the complete sequence of prompts provided during the design, building, debugging, and iteration phases of **Drop-Off Oasis**:

1. **Initial Agent Testing**:
   > *"Test my agent with the message, 'What's the weather in New York, Part of India?'"*
2. **Playground Setup**:
   > *"Launch agent playground for me and can you link as well"*
3. **Initial Deployment**:
   > *"Deploy my agent to agent platform."*
4. **App Brainstorming & Concept Brief**:
   > *"Help me design my agentic application. I need help brainstorming what specific agent to build. My thaughts are mom is here and busy schedule i get 45 to 1 hour time after dropping son to class. Utilize the time to near by place to walk, help to build app give details to close by and recommend. Also should be beautiful and real. Make sure to use all google application. ANy thing make better good. It has to be unique and no body would have build. But should solve real problem"*
5. **Niche Selection**:
   > *"yes liked drop off oassis , lets do nature scienec walks."*
6. **Feature Expansion (Memory, Audio, Photos)**:
   > *"this is good also add long term memory so that next it recommends should be new one and not same. Also option share the feedback to google directly with own photos to improve review. ALso voice agent and own song. to generate to enjoy in park. any thing else make creative"*
7. **Brief Merging**:
   > *"make sure initial as well as new changes in project md is there. Got it please merge both and give final copy"*
8. **Project Renaming**:
   > *"Use the newly created project_brief.md to rename my existing agent project to match it: rename the project folder and update the name in agents-cli-manifest.yaml and pyproject.toml. Keep the code in app/ unchanged, and don't deploy or change any agent logic yet."*
9. **Full Build Request**:
   > *"build it and use google API where ever required. Create key automatically. make complete app ready."*
10. **Protobuf Bug Report**:
    > *"Error: ValueError: Protocol message AgentCard has no "supportedInterfaces" field."*
11. **Audio Storage Bug Report**:
    > *"it is better it says sound track url but dont see it in storage area."*
12. **UI & Feature Refinement**:
    > *"i don;t see any audio song properly. use lyra and generate it for 30 seconds. ALso rag not working recommending same spots. Also make sure to to ask photo after trip before review. ALso show images in the interface itself rather than links. Maps show beautifully. MAke sure response is beautiful with images and description."*
13. **Dynamic Audio, README & Diagram Request**:
    > *"SOund track is not creating using lyra . Make sure per prompt message generated correctly and can hear the news. ALso create a neat read me docs, Also architecture diagram with svg as well component diagram of each file. Once I verify i want to checkin to git."*
14. **Learning Document Request**:
    > *"create learning document of all the error i reported and prompt given in making this app."*
15. **Multi-Language & Theme Audio Request**:
    > *"audio not working please use https://gemini.google/overview/music-generation/ and ensure can take song theme and language from input"*
16. **Native Language Lyric Voiceover & Quick Demo Chips**:
    > *"I want song of Lyrics Snippet, Currently it generated Lyrics Snippet but song is generic english. ALso update chat with all the option so that i can demo it. including song etc.. Please make it quick just have 10 min"*

---

## 2. Reported Errors & Technical Solutions

### Error 1: Protobuf Mismatch (`AgentCard has no "supportedInterfaces" field`)
- **Symptom**: 
  ```text
  ValueError: Protocol message AgentCard has no "supportedInterfaces" field.
  ```
- **Root Cause**: 
  The Python `a2a-sdk` Protobuf object `AgentCard` defines field names in `snake_case` (`supported_interfaces`), whereas the Vertex AI Agent Engine server outputs `camelCase` JSON (`supportedInterfaces`). Direct instantiation like `AgentCard(**json_dict)` fails because Protobuf classes do not accept unknown keyword arguments.
- **Solution**:
  Use `google.protobuf.json_format.ParseDict` with `ignore_unknown_fields=True` to parse camelCase JSON payloads safely into Protobuf instances:
  ```python
  from google.protobuf.json_format import ParseDict
  
  card = AgentCard()
  ParseDict(card_dict, card, ignore_unknown_fields=True)
  ```

---

### Error 2: Internal Container Host Connection Errors (`http://0.0.0.0:8000/a2a/app`)
- **Symptom**:
  ```text
  httpcore.ConnectError: All connection attempts failed
  ```
- **Root Cause**:
  When Agent Engine returns `agent-card.json`, interface URLs point to internal Docker container addresses (e.g. `http://0.0.0.0:8000/a2a/app`). External clients attempting to connect to `0.0.0.0` fail.
- **Solution**:
  In `frontend/main.py`, dynamically inspect and rewrite internal container URLs to point to the external Vertex AI passthrough URL (`A2A_BASE`) before connecting:
  ```python
  def rewrite_urls(data: dict, a2a_base: str):
      if data.get("url", "").startswith("http://0.0.0.0"):
          data["url"] = a2a_base
      for field in ["supportedInterfaces", "additionalInterfaces"]:
          for item in data.get(field, []):
              if isinstance(item, dict) and item.get("url", "").startswith("http://0.0.0.0"):
                  item["url"] = a2a_base
  ```

---

### Error 3: Missing Audio Storage & Mock Soundtrack URLs
- **Symptom**: 
  Soundtrack links returned in chat pointed to non-existent mock GCS buckets (`https://storage.googleapis.com/drop-off-oasis-audio/...`), resulting in 404 errors when played.
- **Root Cause**: 
  The initial tool implementation returned hardcoded static strings without creating Cloud Storage resources or synthesizing actual MP3 files.
- **Solution**:
  1. Created a public Google Cloud Storage bucket (`gs://drop-off-oasis-media-688258816137`) with `allUsers` `roles/storage.objectViewer` read permissions.
  2. Integrated **Google Cloud Text-to-Speech API** (Neural2 voices) and `ffmpeg` in Python to dynamically synthesize 30-second studio MP3 tracks combining guided voiceover, nature news, and 432Hz ambient music.
  3. Uploaded synthesized MP3s to GCS on demand and returned valid public GCS URLs.
  4. Embedded an HTML5 `<audio controls>` player directly in `frontend/static/index.html`.

---

### Error 4: RAG Recommending Duplicate Nature Spots
- **Symptom**: 
  Asking for nature walk recommendations on consecutive turns returned the exact same 3 spots every time.
- **Root Cause**: 
  The search tool executed static list filtering without preserving session state or tracking previously returned items.
- **Solution**:
  Added RAG Session Memory tracking (`_SEEN_SPOTS`) inside `get_nearby_scenic_walks` in `app/agent.py`:
  ```python
  _SEEN_SPOTS: set[str] = set()

  def get_nearby_scenic_walks(location: str, max_duration_mins: int = 45):
      global _SEEN_SPOTS
      # Exclude previously returned spot IDs
      unseen = [s for s in all_spots if s["id"] not in _SEEN_SPOTS and s["est_walk_mins"] <= max_duration_mins]
      if len(unseen) < 2:
          _SEEN_SPOTS.clear() # Reset when dataset exhausted
          unseen = [s for s in all_spots if s["est_walk_mins"] <= max_duration_mins]
      
      selected = unseen[:3]
      for s in selected:
          _SEEN_SPOTS.add(s["id"])
      return {"spots": selected}
  ```

---

### Error 5: Plain Text Links Instead of In-App Images & Maps
- **Symptom**: 
  Nature spots and map locations rendered as raw markdown links (e.g. `[Map](https://...)`) rather than inline visual cards.
- **Root Cause**: 
  The web UI `index.html` rendered incoming text as plain `textContent` without parsing markdown image syntax.
- **Solution**:
  Updated `formatTextNode` in `frontend/static/index.html` to parse `![alt](url)` markdown images and dynamically render responsive `<img src="...">` cards with captions and Google Static Maps previews directly in the chat bubbles.

---

### Error 6: Skipping Photo Attachment Before Review Submission
- **Symptom**: 
  Users asking to submit a review immediately triggered `submit_place_review` without uploading or describing a walk photo.
- **Root Cause**: 
  System instructions lacked strict multi-turn control flow scoping for the review workflow.
- **Solution**:
  Updated `SYSTEM_INSTRUCTION` in `app/agent.py` to enforce a mandatory two-step workflow:
  > *"When a user wants to submit a review or says they completed a walk, YOU MUST FIRST ASK THEM TO SHARE OR DESCRIBE A PHOTO OF THEIR TRIP before calling submit_place_review."*

---

### Error 7: Agent Engine Cloud Build Deployment Failure (Code 3)
- **Symptom**:
  ```text
  Error: Deployment failed: {'code': 3, 'message': 'The Reasoning Engine failed to be updated.'}
  ```
- **Root Cause**: 
  Adding transient dev dependencies directly to `pyproject.toml` caused package resolution conflicts during Agent Engine's remote Cloud Build environment.
- **Solution**:
  Cleaned runtime dependencies in `pyproject.toml` to stick to essential ADK packages, isolated audio synthesis logic cleanly, and re-triggered `agents-cli deploy`.

---

### Error 8: Audio Player Spoke Generic Welcome Message Instead of Full Lyrics
- **Symptom**:
  The audio player streamed music, but the spoken voiceover was a generic welcome message instead of the full native language lyric poem text.
- **Root Cause**:
  TTS synthesis input was using default template strings instead of the translated native script poem.
- **Solution**:
  Refactored TTS synthesis input in `generate_walk_soundtrack` (`app/agent.py`) to synthesize the full native language script poem texts (Kannada `"ತಂಪಾದ ಸಂಜೆಯಲಿ..."`, Hindi `"ठंडी हवा में..."`, Spanish `"En la fresca brisa..."`) and mix with lo-fi/ambient audio tracks using FFmpeg before uploading to GCS bucket (`gs://drop-off-oasis-media-688258816137/audio/`).

---

### Error 9: GitHub Markdown Viewer Not Rendering SVG Diagrams
- **Symptom**:
  GitHub repository preview rendered broken icon placeholders for `docs/architecture_diagram.svg` and `docs/component_diagram.svg`.
- **Root Cause**:
  GitHub markdown renderer sanitizes external SVG files and inline styles, causing complex SVG diagrams to fail rendering in browser views.
- **Solution**:
  Converted both SVG diagrams to high-resolution PNG assets (`docs/architecture_diagram.png` and `docs/component_diagram.png`) using headless Chrome screenshot rendering, updated all markdown references in `README.md` and `docs/USER_GUIDE_AND_DEMO_SCRIPT.md`, and committed PNG assets to git.

---

## 3. Key Architecture Patterns & Lessons Learned

1. **A2A Protocol & Protobuf Handling**: Always use `google.protobuf.json_format.ParseDict` when deserializing camelCase JSON from cloud agent frameworks into Python Protobuf instances.
2. **Container Host URL Rewriting**: Always inspect container metadata returned by cloud runtimes and rewrite internal IPs (`0.0.0.0`) to public proxy endpoints.
3. **Session State Memory in RAG**: When building retrieval tools, maintain state tracking (e.g., `_SEEN_SPOTS` or Vertex AI Memory Bank) to prevent repetitive results.
4. **Rich Visual Chat UIs**: Combine plain text replies with custom markdown parsers for images, inline HTML5 audio controls, and native A2UI cards to maximize user engagement.
5. **PNG Diagrams for GitHub Compatibility**: Always provide rasterized PNG fallbacks alongside SVG diagrams so repository pages render cleanly on GitHub and mobile browsers.

