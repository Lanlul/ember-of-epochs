from fastapi import APIRouter, HTTPException, status

from ..models.action import (
    NewGameRequest,
    NewGameResponse,
    ActionRequest,
    ActionResponse,
    ActionErrorResponse,
    EndingRequest,
    EndingResponse,
)
from ..services.game_master import GameMaster

router = APIRouter()

_gm = GameMaster()


@router.post("/new-game", response_model=NewGameResponse)
async def new_game(req: NewGameRequest):
    resp = await _gm.new_game(req.player_name, req.difficulty)
    return NewGameResponse(**resp.model_dump())


@router.post(
    "/action",
    response_model=ActionResponse,
    responses={400: {"model": ActionErrorResponse}},
)
async def take_action(req: ActionRequest):
    try:
        return await _gm.process_action(req.session_id, req.choice_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )


@router.post(
    "/ending",
    response_model=EndingResponse,
    responses={400: {"model": ActionErrorResponse}},
)
async def get_ending(req: EndingRequest):
    try:
        return await _gm.resolve_ending(req.session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
