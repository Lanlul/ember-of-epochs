import pytest

from app.services.ending import EndingService, ENDINGS
from app.services.chronicle import ChronicleService
from app.models.world import Alignment, WorldState
from app.models.session import Session
from app.models.action import LLMOutput


class TestEndingService:
    def setup_method(self):
        self.svc = EndingService()

    def test_five_endings_defined(self):
        assert len(ENDINGS) == 5
        ids = [e.id for e in ENDINGS]
        assert ids == [
            "mechanical_epoch",
            "jade_epoch",
            "ashen_epoch",
            "primal_epoch",
            "eternal_cycle",
        ]

    def test_mechanical_epoch(self):
        ending = self.svc.determine_ending(
            Alignment(order=80, chaos=20, technology=85, nature=15)
        )
        assert ending.id == "mechanical_epoch"
        assert ending.title == "機械紀元"

    def test_jade_epoch(self):
        ending = self.svc.determine_ending(
            Alignment(order=75, chaos=25, technology=20, nature=80)
        )
        assert ending.id == "jade_epoch"
        assert ending.title == "翡翠紀元"

    def test_ashen_epoch(self):
        ending = self.svc.determine_ending(
            Alignment(order=15, chaos=85, technology=80, nature=20)
        )
        assert ending.id == "ashen_epoch"
        assert ending.title == "灰燼紀元"

    def test_primal_epoch(self):
        ending = self.svc.determine_ending(
            Alignment(order=20, chaos=80, technology=15, nature=85)
        )
        assert ending.id == "primal_epoch"
        assert ending.title == "野性紀元"

    def test_eternal_cycle(self):
        ending = self.svc.determine_ending(
            Alignment(order=55, chaos=45, technology=52, nature=48)
        )
        assert ending.id == "eternal_cycle"
        assert ending.title == "輪迴紀元"

    def test_is_ending_triggered_above_threshold(self):
        assert self.svc.is_ending_triggered(
            Alignment(order=70, chaos=30, technology=60, nature=40), 5
        ) is True

    def test_is_ending_triggered_below_threshold(self):
        assert self.svc.is_ending_triggered(Alignment(), 5) is False

    def test_is_ending_triggered_min_actions(self):
        assert self.svc.is_ending_triggered(
            Alignment(order=80, chaos=20, technology=70, nature=30), 3
        ) is False

    def test_ending_progress_shape(self):
        progress = self.svc.get_ending_progress(
            Alignment(order=50, chaos=50, technology=65, nature=35)
        )
        assert "dominant_moral" in progress
        assert "dominant_elemental" in progress
        assert "max_axis_value" in progress
        assert "progress_pct" in progress
        assert progress["max_axis_value"] == 65
        assert progress["progress_pct"] == 100

    def test_each_ending_has_scene_tags(self):
        for ending in ENDINGS:
            tags = ending.scene_tags
            assert tags.setting
            assert tags.mood
            assert tags.lighting
            assert len(tags.color_palette) >= 3
            assert tags.style
            assert tags.focus


class TestChronicleService:
    def setup_method(self):
        self.svc = ChronicleService(llm_provider=None)

    def test_build_chronicle_shape(self):
        session = Session(
            session_id="test",
            player_name="伊索",
            difficulty="normal",
            world_state=WorldState(
                continent="克洛諾斯廢土",
                alignment=Alignment(order=70, chaos=30, technology=60, nature=40),
                chapter=3,
            ),
        )
        session.history.append({
            "narrative": "你選擇了調查星盤。",
            "chosen_choice_id": "c1",
        })

        ending = ENDINGS[0]
        chronicle = self.svc.build_chronicle(session, ending)

        assert chronicle["player_name"] == "伊索"
        assert chronicle["ending"]["id"] == "mechanical_epoch"
        assert chronicle["ending"]["title"] == "機械紀元"
        assert "key_decisions" in chronicle
        assert "journey" in chronicle
        assert "final_alignment" in chronicle
        assert chronicle["journey"]["total_actions"] == 1

    def test_key_decisions_empty_history(self):
        session = Session(
            session_id="test",
            player_name="測試",
            world_state=WorldState(
                continent="克洛諾斯廢土",
                alignment=Alignment(),
                chapter=1,
            ),
        )
        ending = ENDINGS[4]
        chronicle = self.svc.build_chronicle(session, ending)
        assert len(chronicle["key_decisions"]) == 0

    def test_alignment_to_text(self):
        from app.services.chronicle import ChronicleService as CS
        assert CS._alignment_to_text(Alignment(order=70, chaos=30, technology=25, nature=75)) == "崇尚秩序、親近自然"
        assert CS._alignment_to_text(Alignment(order=20, chaos=80, technology=75, nature=25)) == "擁抱混沌、信賴科技"
        assert CS._alignment_to_text(Alignment()) == "維持均衡"
