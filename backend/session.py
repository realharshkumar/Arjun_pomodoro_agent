import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SessionState(BaseModel):
    session_id: str
    phase: str = "INTAKE"  # INTAKE, PLANNING, FOCUS_BLOCK, BREAK, WRAPUP
    current_task: Optional[str] = None
    block_duration_minutes: int = 25
    completed_blocks: int = 0
    history: List[Dict[str, str]] = Field(default_factory=list)


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> SessionState:
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            self._sessions[new_id] = SessionState(session_id=new_id)
            return self._sessions[new_id]
        return self._sessions[session_id]

    def add_user_message(self, session_id: str, message: str):
        session = self.get_or_create(session_id)
        session.history.append({"role": "user", "content": message})

    def add_assistant_message(self, session_id: str, message: str):
        session = self.get_or_create(session_id)
        session.history.append({"role": "assistant", "content": message})

    def update_state(self, session_id: str, state_update: Dict[str, Any]):
        session = self.get_or_create(session_id)
        if "phase" in state_update and state_update["phase"]:
            session.phase = state_update["phase"]
        if "current_task" in state_update and state_update["current_task"]:
            session.current_task = state_update["current_task"]
        if "block_duration_minutes" in state_update and state_update["block_duration_minutes"]:
            session.block_duration_minutes = state_update["block_duration_minutes"]


session_manager = SessionManager()
