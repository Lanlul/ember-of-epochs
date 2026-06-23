import pytest
from unittest.mock import patch, AsyncMock

from app.services.game_master import GameMaster
from app.services.llm import StructParser
from app.models.world import Alignment

from .fixtures.llm_responses import (
    RAW_JSON,
    RAW_JSON_CODEBLOCK,
    RAW_MALFORMED,
)


class TestStructParser:
    def test_parse_plain_json(self):
        parser = StructParser()
        result = parser.parse(RAW_JSON)
        assert "星象塔" in result.narrative
        assert len(result.choices) == 3
        assert result.scene_tags.style == "ruins_gothic"

    def test_parse_codeblock_json(self):
        parser = StructParser()
        result = parser.parse(RAW_JSON_CODEBLOCK)
        assert "石門" in result.narrative
        assert len(result.choices) == 1

    def test_parse_malformed_falls_back(self):
        parser = StructParser()
        result = parser.parse(RAW_MALFORMED)
        assert "這不是 JSON" in result.narrative
        assert result.visual_prompt == ""
        assert result.options == []


@pytest.mark.asyncio
class TestGameMaster:
    async def test_new_game_returns_valid_response(self, game_master):
        resp = await game_master.new_game("伊索", "normal")
        assert resp.session_id
        assert len(resp.narrative) > 20
        assert len(resp.choices) == 3
        assert resp.image_url.startswith("/images/scenes/")
        assert resp.world_state.continent == "克洛諾斯廢土"
        assert resp.world_state.alignment == Alignment()

    async def test_process_action_returns_next_scene(self, game_master):
        new = await game_master.new_game("測試者")
        resp = await game_master.process_action(new.session_id, "c1")
        assert resp.narrative
        assert len(resp.choices) == 3
        assert resp.image_url != new.image_url
        assert resp.session_id == new.session_id

    async def test_process_action_updates_alignment(self, game_master, mock_llm):
        new = await game_master.new_game("伊索")
        initial = new.world_state.alignment.model_copy()

        resp = await game_master.process_action(new.session_id, "c1")
        final = resp.world_state.alignment

        deltas = [
            (final.order, initial.order, "order"),
            (final.chaos, initial.chaos, "chaos"),
            (final.technology, initial.technology, "technology"),
            (final.nature, initial.nature, "nature"),
        ]
        any_changed = any(a != b for a, b, _ in deltas)
        assert any_changed, (
            f"Expected at least one axis to change: "
            f"initial={initial}, final={final}"
        )
        assert mock_llm.call_count == 1

    async def test_session_history_accumulates(self, game_master):
        new = await game_master.new_game("伊索")
        await game_master.process_action(new.session_id, "c1")
        await game_master.process_action(new.session_id, "c4")

        session = game_master.get_session(new.session_id)
        assert session is not None
        assert len(session.history) == 2

    async def test_invalid_session_raises(self, game_master):
        with pytest.raises(ValueError, match="Session not found"):
            await game_master.process_action("bad-id", "c1")

    async def test_session_count(self, game_master):
        assert game_master.session_count() == 0
        await game_master.new_game("A")
        await game_master.new_game("B")
        await game_master.new_game("C")
        assert game_master.session_count() == 3


@pytest.mark.asyncio
class TestAlignmentEdgeCases:
    async def test_alignment_clamps_at_bounds(self, game_master, mock_llm):
        mock_llm.response = RAW_JSON
        new = await game_master.new_game("伊索")

        for _ in range(20):
            await game_master.process_action(new.session_id, "c1")

        align = game_master.get_session(new.session_id).world_state.alignment
        for axis in ["order", "chaos", "technology", "nature"]:
            val = getattr(align, axis)
            assert 0 <= val <= 100, f"{axis}={val} out of range"

    async def test_multiple_sessions_independent(self, game_master):
        s1 = await game_master.new_game("A")
        s2 = await game_master.new_game("B")

        await game_master.process_action(s1.session_id, "c1")
        assert game_master.get_session(s2.session_id).history == []
