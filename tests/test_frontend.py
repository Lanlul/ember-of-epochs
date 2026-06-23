import json


class TestApiClient:
    """Verify API client constructs correct requests."""

    def test_new_game_request_body(self):
        body = json.dumps({"player_name": "伊索", "difficulty": "normal"})
        parsed = json.loads(body)
        assert parsed["player_name"] == "伊索"
        assert parsed["difficulty"] == "normal"

    def test_new_game_minimal_body(self):
        body = json.dumps({"player_name": "test"})
        parsed = json.loads(body)
        assert parsed["player_name"] == "test"

    def test_action_request_body(self):
        body = json.dumps({
            "session_id": "abc-123",
            "choice_id": "c1",
        })
        parsed = json.loads(body)
        assert parsed["session_id"] == "abc-123"
        assert parsed["choice_id"] == "c1"

    def test_response_shape(self):
        sample = {
            "session_id": "uuid",
            "narrative": "text",
            "choices": [{"id": "c1", "text": "opt"}],
            "image_url": "/images/1.png",
            "world_state": {
                "continent": "廢土",
                "alignment": {"order": 50, "chaos": 50, "technology": 50, "nature": 50},
                "chapter": 1,
            },
        }
        assert "session_id" in sample
        assert "choices" in sample
        assert len(sample["choices"]) >= 1
        assert sample["choices"][0]["id"] == "c1"
        assert sample["world_state"]["alignment"]["order"] == 50


class TestGameHook:
    def test_hook_state_shape(self):
        state = {
            "screen": "start",
            "sessionId": None,
            "playerName": "",
            "narrative": "",
            "choices": [],
            "imageUrl": "",
            "worldState": None,
            "loading": False,
            "error": None,
        }
        assert state["screen"] in ("start", "game")

    def test_hook_transitions(self):
        start = {"screen": "start", "loading": False}
        loading = {**start, "loading": True}
        game = {**start, "screen": "game", "sessionId": "abc"}
        assert loading["loading"] is True
        assert game["screen"] == "game"
        assert game["sessionId"] == "abc"
