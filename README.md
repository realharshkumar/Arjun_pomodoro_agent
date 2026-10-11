# Arjun — AI Study Focus Coach for Engineering Students

An on-demand, voice-first AI study coach powered by the Sarvam AI API suite and deployed on Render. Arjun helps engineering students overcome exam anxiety and procrastination by converting overwhelming workloads into structured Pomodoro focus blocks and keeping them accountable.

---

## 🚀 Live Demo & Links
- **Live App**: [INSERT_YOUR_RENDER_URL_HERE]
- **GitHub Repository**: [INSERT_YOUR_GITHUB_REPO_URL_HERE]

---

## 📌 Problem Statement
Engineering students in India often sit down to study with limited time and an unmanageable backlog of tasks (internals, lab records, assignments, placement prep). The result is procrastination, unfocused study sessions, and panic. Students lack an accessible, on-demand mentor to structure their study time realistically and stay accountable to the plan.

## 💡 Solution & Features
- **Arjun Coaching Persona**: A calm, pragmatic senior-mentor persona tailored for Indian engineering students. He focuses strictly on time management, prioritization, and accountability (declines academic tutoring to maintain coaching discipline).
- **Voice-First & Multimodal**: Talk or type to Arjun. Native microphone capture with immediate synthesized voice playback.
- **Dynamic Pomodoro Synchronization**: Arjun suggests concrete 25-minute or 50-minute deep work blocks, which instantly synchronize with the interactive browser countdown timer.
- **Mid-Session Accountability & Check-Ins**: Automated boundary checks when a focus block concludes to review progress, handle roadblocks without judgment, and launch the next block.

---

## 🛠️ Powered by Sarvam AI Suite
1. **Speech-to-Text (Saaras:v2)**: Transcribes Indian English and Indic accents seamlessly from the browser audio.
2. **LLM Engine (`sarvam-105b-conversations`)**: Drives Arjun's empathetic coaching prompts, session boundary transitions, and structured JSON plan extraction.
3. **Text-to-Speech (Bulbul:v3 - Aditya voice)**: Delivers natural, warm Indian-accented spoken responses.

---

## 🏗️ Architecture & Tech Stack
- **Backend**: FastAPI, Uvicorn, HTTPX (async REST client), Python-dotenv
- **Frontend**: Vanilla JS, HTML5 MediaRecorder API, Tailwind CSS
- **Deployment**: Render.com (Singapore region for low latency)
