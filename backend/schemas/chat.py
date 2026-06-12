from pydantic import BaseModel
from typing import Any


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ConfirmRequest(BaseModel):
    session_id: str
    confirmed: bool


class EmergencyRequest(BaseModel):
    session_id: str
    safeword: str


class ActionTaken(BaseModel):
    type: str
    status: str
    data: dict[str, Any] = {}


class ChatResponse(BaseModel):
    reply: str
    action_taken: ActionTaken | None = None
    requires_confirmation: bool = False
    pending_action: dict[str, Any] | None = None
