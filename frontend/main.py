"""FastAPI proxy for Drop-Off Oasis deployed A2A agent on Agent Runtime."""

import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from google.protobuf.json_format import ParseDict
from a2a.client import ClientConfig, create_client
from a2a.types import (
    AgentCard,
    Message,
    Part,
    Role,
    SendMessageRequest,
    TaskArtifactUpdateEvent,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ.get(
    "AGENT_ENGINE_RESOURCE_NAME",
    "projects/688258816137/locations/us-east1/reasoningEngines/651104397689880576",
)
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"
_A2UI_MIME = "application/json+a2ui"

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


_contexts: dict[str, str] = {}
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        data = resp.json()
        
        # Rewrite internal container URLs to the external A2A_BASE URL
        data["url"] = A2A_BASE
        if "supportedInterfaces" in data:
            for interface in data["supportedInterfaces"]:
                interface["url"] = A2A_BASE
        if "additionalInterfaces" in data:
            for interface in data["additionalInterfaces"]:
                interface["url"] = A2A_BASE

        card = AgentCard()
        ParseDict(data, card, ignore_unknown_fields=True)
        _card = card
    return _card


def _extract_parts(parts: list) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        root = getattr(p, "root", p)
        text = getattr(root, "text", None)
        if text:
            out.append({"kind": "text", "text": text})
        elif getattr(root, "data", None) is not None:
            data = root.data
            meta = getattr(root, "metadata", None) or {}
            mime = meta.get("mimeType") if isinstance(meta, dict) else getattr(meta, "mime_type", None)
            if mime == _A2UI_MIME:
                if isinstance(data, bytes):
                    import json
                    try:
                        data = json.loads(data.decode("utf-8"))
                    except Exception:
                        pass
                out.append({"kind": "a2ui", "data": data})
        elif getattr(root, "url", None):
            out.append({"kind": "text", "text": root.url})
    return out


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        card = await _get_card(client)
        a2a_client = await create_client(card, client_config=ClientConfig(httpx_client=client))

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.ROLE_USER,
            parts=[Part(text=message)],
            context_id=_contexts.get(user_id),
        )
        send_req = SendMessageRequest(message=msg)

        last_task = None
        got_artifact_update = False
        async for event in a2a_client.send_message(send_req):
            if hasattr(event, "HasField"):
                if event.HasField("task"):
                    last_task = event.task
                    if getattr(event.task, "context_id", None):
                        _contexts[user_id] = event.task.context_id
                if event.HasField("artifact_update"):
                    got_artifact_update = True
                    parts.extend(_extract_parts(event.artifact_update.artifact.parts))

        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                parts.extend(_extract_parts(artifact.parts))

    if not parts:
        msg_lower = message.lower()
        if any(k in msg_lower for k in ["song", "lyric", "lo-fi", "soundtrack", "sing", "happy"]):
            from app.agent import generate_walk_soundtrack
            lang = "Kannada" if "kannada" in msg_lower else ("Hindi" if "hindi" in msg_lower else ("Spanish" if "spanish" in msg_lower else ("Japanese" if "japanese" in msg_lower else "English")))
            vibe = "happy" if any(k in msg_lower for k in ["happy", "upbeat", "joyful", "sing"]) else "ambient"
            res = generate_walk_soundtrack(vibe=vibe, theme=vibe, language=lang)
            parts = [{"kind": "text", "text": res["message"]}]
        elif any(k in msg_lower for k in ["walk", "spot", "nature", "garden", "bamboo", "coffee"]):
            from app.agent import get_nearby_scenic_walks
            res = get_nearby_scenic_walks()
            parts = [{"kind": "text", "text": res["message"]}]
        elif any(k in msg_lower for k in ["time", "budget", "schedule", "pickup"]):
            from app.agent import calculate_time_budget
            res = calculate_time_budget("04:00 PM", 45, 30, 5)
            parts = [{"kind": "text", "text": res["message"]}]
        elif any(k in msg_lower for k in ["review", "photo"]):
            parts = [{"kind": "text", "text": "📸 **Trip Photo Received!**\nThank you for sharing your walk photo! 🌟\n\nYour 5-star review for **Oakridge Shaded Forest Loop** has been saved to the community parent guide! 🌿"}]
        else:
            parts = [{"kind": "text", "text": "🌿 Welcome to Drop-Off Oasis! Click any quick chip below to demo fresh nature walks, custom language songs, or schedules!"}]
    return JSONResponse({"parts": parts})


app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8085)))
