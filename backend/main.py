import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from backend.config import PORT
from backend.sarvam_client import SarvamClient
from backend.session import session_manager

app = FastAPI(title="Arjun - AI Study Focus Coach")

# CORS middleware for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sarvam_client = SarvamClient()


class TextChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language_code: Optional[str] = "en-IN"


class CheckInRequest(BaseModel):
    session_id: str
    event: str  # "block_finished", "break_finished", "timer_abandoned"
    language_code: Optional[str] = "en-IN"


@app.post("/api/chat/text")
async def chat_text(req: TextChatRequest):
    session = session_manager.get_or_create(req.session_id)
    session_manager.add_user_message(session.session_id, req.message)

    try:
        reply_text, state_data = await sarvam_client.chat_completion(session.history)
        session_manager.add_assistant_message(session.session_id, reply_text)
        if state_data:
            session_manager.update_state(session.session_id, state_data)

        audio_base64 = await sarvam_client.synthesize_speech(reply_text, language_code=req.language_code or "en-IN")

        return {
            "session_id": session.session_id,
            "reply": reply_text,
            "audio_base64": audio_base64,
            "phase": session.phase,
            "current_task": session.current_task,
            "block_duration_minutes": session.block_duration_minutes,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/voice")
async def chat_voice(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    language_code: Optional[str] = Form(None)
):
    session = session_manager.get_or_create(session_id)

    try:
        audio_bytes = await file.read()
        print(f"DEBUG: Received audio file {file.filename}, size {len(audio_bytes)} bytes, requested lang: {language_code}")
        
        try:
            transcribed_text, detected_lang = await sarvam_client.transcribe_audio(
                audio_bytes, filename=file.filename or "recording.wav", language_code=language_code
            )
            print(f"DEBUG: Transcribed text: '{transcribed_text}', Detected lang: {detected_lang}")
        except Exception as stt_err:
            print(f"DEBUG: STT Error details: {stt_err}")
            raise stt_err

        if not transcribed_text.strip():
            return {
                "session_id": session.session_id,
                "user_text": "",
                "reply": "I couldn't quite catch that audio. Try speaking clearly or type your message.",
                "audio_base64": None,
                "phase": session.phase,
            }

        session_manager.add_user_message(session.session_id, transcribed_text)

        reply_text, state_data = await sarvam_client.chat_completion(session.history)
        session_manager.add_assistant_message(session.session_id, reply_text)
        if state_data:
            session_manager.update_state(session.session_id, state_data)

        # Synthesize speech in detected or requested Indic language
        tts_lang = language_code if (language_code and language_code != "auto") else detected_lang
        audio_base64 = await sarvam_client.synthesize_speech(reply_text, language_code=tts_lang)

        return {
            "session_id": session.session_id,
            "user_text": transcribed_text,
            "detected_lang": detected_lang,
            "reply": reply_text,
            "audio_base64": audio_base64,
            "phase": session.phase,
            "current_task": session.current_task,
            "block_duration_minutes": session.block_duration_minutes,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/check-in")
async def session_check_in(req: CheckInRequest):
    session = session_manager.get_or_create(req.session_id)
    prompt_message = ""
    if req.event == "block_finished":
        session.completed_blocks += 1
        prompt_message = f"[SYSTEM NOTIFICATION: Focus block completed for '{session.current_task or 'task'}'. Check in with the student now.]"
    elif req.event == "break_finished":
        prompt_message = "[SYSTEM NOTIFICATION: Short break ended. Prompt the student to begin the next focus block.]"

    session_manager.add_user_message(session.session_id, prompt_message)

    try:
        reply_text, state_data = await sarvam_client.chat_completion(session.history)
        session_manager.add_assistant_message(session.session_id, reply_text)
        if state_data:
            session_manager.update_state(session.session_id, state_data)

        audio_base64 = await sarvam_client.synthesize_speech(reply_text)

        return {
            "session_id": session.session_id,
            "reply": reply_text,
            "audio_base64": audio_base64,
            "phase": session.phase,
            "current_task": session.current_task,
            "completed_blocks": session.completed_blocks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static frontend files if folder exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"status": "Arjun backend running. Frontend index.html not found yet."}
