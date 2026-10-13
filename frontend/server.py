import os
import sys
import uuid
import asyncio

# Ensure Vertex AI environment variables are set
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-04-598b0d494368"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path
sys.path.insert(0, "/config/.gemini/antigravity/scratch/aizen-ai")

from app.agent import root_agent, app as adk_app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI(title="Aizen AI Demo")

session_service = InMemorySessionService()
runner = Runner(
    app=adk_app,
    session_service=session_service,
)

USER_ID = "demo_user"

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not user_msg:
        return JSONResponse({"reply": "Please say something!", "session_id": session_id})

    # Ensure session exists
    session = await session_service.get_session(session_id=session_id, app_name=adk_app.name, user_id=USER_ID)
    if not session:
        session = await session_service.create_session(
            session_id=session_id,
            user_id=USER_ID,
            app_name=adk_app.name,
        )

    # Run agent step with new_message
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_msg)]
    )

    replies = []
    async for event in runner.run_async(
        session_id=session_id,
        user_id=USER_ID,
        new_message=user_content,
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    replies.append(part.text)

    final_reply = "".join(replies).strip() or "(No response returned)"
    return JSONResponse({"reply": final_reply, "session_id": session_id})

# Serve static files
app.mount("/", StaticFiles(directory="/config/.gemini/antigravity/scratch/aizen-ai/frontend/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
