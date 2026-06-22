from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from .world import WorldState, SceneTags
from .session import Choice


class NewGameRequest(BaseModel):
    player_name: str
    difficulty: str = "normal"


class NewGameResponse(BaseModel):
    session_id: str
    narrative: str
    choices: List[Choice]
    image_url: str
    world_state: WorldState


class ActionRequest(BaseModel):
    session_id: str
    choice_id: str


class ActionResponse(BaseModel):
    session_id: str
    narrative: str
    choices: List[Choice]
    image_url: str
    world_state: WorldState
    is_ending: bool = False
    stage: int = 1
    current_turn: int = 1


class ActionErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class LLMOutput(BaseModel):
    narrative: str
    choices: List[Choice]
    scene_tags: SceneTags
    alignment_delta: Optional[Dict[str, int]] = None
    visual_prompt: str = ""
    options: List[str] = Field(default_factory=list)


class EndingInfo(BaseModel):
    id: str
    title: str
    subtitle: str
    moral: str
    description: str


class ChronicleData(BaseModel):
    player_name: str
    ending: EndingInfo
    journey: Dict
    key_decisions: List[Dict]
    final_alignment: Dict


class EndingRequest(BaseModel):
    session_id: str


class EndingResponse(BaseModel):
    session_id: str
    ending: EndingInfo
    chronicle: ChronicleData
    epilogue: str
    image_url: str
