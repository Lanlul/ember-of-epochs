from pydantic import BaseModel, Field
from typing import List


class Alignment(BaseModel):
    order: int = Field(default=50, ge=0, le=100)
    chaos: int = Field(default=50, ge=0, le=100)
    technology: int = Field(default=50, ge=0, le=100)
    nature: int = Field(default=50, ge=0, le=100)


class WorldState(BaseModel):
    continent: str
    alignment: Alignment
    chapter: int = Field(default=1, ge=1)


class SceneTags(BaseModel):
    setting: str
    mood: str
    lighting: str
    color_palette: List[str]
    style: str
    focus: str
    character_state: str
