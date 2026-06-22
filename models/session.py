from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .world import WorldState, Alignment


class Choice(BaseModel):
    id: str
    text: str
    alignment_delta: Optional[Dict[str, int]] = None


class Session(BaseModel):
    session_id: str
    player_name: str
    difficulty: str = "normal"
    world_state: WorldState
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
