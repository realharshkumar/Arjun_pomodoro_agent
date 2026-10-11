import httpx
import json
import re
from typing import Optional, Tuple, Dict, Any
from backend.config import SARVAM_API_KEY, SARVAM_BASE_URL
from backend.prompts import ARJUN_SYSTEM_PROMPT


class SarvamClient:
    def __init__(self, api_key: str = SARVAM_API_KEY):
        self.api_key = api_key
        self.headers = {
            "api-subscription-key": self.api_key,
        }

    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribes speech using Sarvam STT (Saaras:v2).
        """
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not configured.")

        url = f"{SARVAM_BASE_URL}/speech-to-text"
        files = {
            "file": (filename, audio_bytes, "audio/wav")
        }
        data = {
            "model": "saaras:v2",
            "language_code": "en-IN",
            "with_diarization": "false"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={"api-subscription-key": self.api_key},
                data=data,
                files=files
            )
            response.raise_for_status()
            result = response.json()
            return result.get("transcript", "")

    async def chat_completion(self, history: list) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Calls Sarvam Chat/LLM API with conversation history.
        Using active model 'sarvam-105b-conversations'.
        """
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not configured.")

        url = f"{SARVAM_BASE_URL}/v1/chat/completions"
        messages = [{"role": "system", "content": ARJUN_SYSTEM_PROMPT}] + history

        payload = {
            "model": "sarvam-105b-conversations",
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 400
        }

        headers = {
            **self.headers,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]

        # Parse optional JSON state block
        state_data = None
        clean_text = raw_text
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            try:
                state_data = json.loads(match.group(1))
                clean_text = raw_text.replace(match.group(0), "").strip()
            except Exception:
                pass

        return clean_text, state_data

    async def synthesize_speech(self, text: str) -> Optional[str]:
        """
        Synthesizes text to speech using active Sarvam TTS ('bulbul:v3' with speaker 'aditya').
        """
        if not self.api_key:
            return None

        url = f"{SARVAM_BASE_URL}/text-to-speech"
        payload = {
            "inputs": [text[:500]],  # Cap text to keep synthesis fast and reliable
            "target_language_code": "en-IN",
            "speaker": "aditya",
            "model": "bulbul:v3"
        }

        headers = {
            **self.headers,
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    audios = data.get("audios", [])
                    if audios:
                        return audios[0]
                else:
                    print(f"TTS warning ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"TTS synthesis exception: {e}")

        return None
