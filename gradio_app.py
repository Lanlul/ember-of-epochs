import logging
from pathlib import Path
from typing import AsyncGenerator, Optional, Tuple, Union

import gradio as gr

from .config import settings
from .services.game_master import GameMaster

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

_gm = GameMaster()
_STATIC_DIR = Path(settings.static_dir).resolve()


def _resolve_image(path: str) -> Union[str, "Image.Image", None]:
    p = path.lstrip("/") if path else ""
    full = (_STATIC_DIR / p).resolve()
    if full.exists() and full.is_file():
        return str(full)
    return _placeholder_image()


_PLACEHOLDER: Optional["Image.Image"] = None


def _placeholder_image() -> "Image.Image":
    global _PLACEHOLDER
    if _PLACEHOLDER is not None:
        return _PLACEHOLDER
    from PIL import Image, ImageDraw, ImageFont
    w, h = 768, 512
    img = Image.new("RGB", (w, h), (20, 18, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 32)
    except Exception:
        font = ImageFont.load_default()
    text = "幻境編年史"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) // 2, (h - th) // 2 - 20), text, fill=(230, 184, 92), font=font)
    draw.text(((w - tw) // 2, (h - th) // 2 + 30), "紀元餘燼", fill=(217, 74, 42), font=font)
    _PLACEHOLDER = img
    return _PLACEHOLDER


CSS = """
:root { --emoji-font: "Noto Color Emoji", sans-serif; }
.game-title { text-align: center; font-size: 2rem; font-weight: 700; color: #e6b85c; letter-spacing: 0.1em; }
.game-subtitle { text-align: center; font-size: 1.1rem; color: #d94a2a; margin-bottom: 1.5rem; }
.narrative-box { min-height: 120px; font-size: 1.05rem; line-height: 1.7; }
.choice-btn { min-height: 60px !important; font-size: 1rem !important; }
.status-label { font-size: 0.85rem; color: #a7a9be; }
"""


async def start_game(
    player_name: str,
) -> Tuple:
    if not player_name.strip():
        raise gr.Error("請輸入你的名字")

    resp = await _gm.new_game(player_name.strip())

    choice_labels = [c.text for c in resp.choices]
    choice_ids = [c.id for c in resp.choices]
    _update_choice_id_map(choice_labels, choice_ids)

    world = resp.world_state
    status = (
        f"回合 1 | Stage 1　"
        f"🌍 {world.continent}　"
        f"秩序 {world.alignment.order}　混沌 {world.alignment.chaos}　"
        f"科技 {world.alignment.technology}　自然 {world.alignment.nature}"
    )

    return (
        resp.narrative,
        gr.update(choices=choice_labels, value=None, visible=True),
        _resolve_image(resp.image_url),
        status,
        resp.session_id,
        gr.update(visible=False),
        gr.update(visible=True),
        player_name.strip(),
        gr.update(visible=True),
        "",
        _resolve_image(resp.image_url),
        gr.update(visible=False),
    )


async def make_choice(
    choice_label: str,
    session_id: str,
) -> AsyncGenerator[Tuple, None]:
    if not choice_label or not session_id:
        raise gr.Error("請先選擇一個選項")

    choice_id_map = _get_choice_id_map()
    choice_id = choice_id_map.get(choice_label, "")

    # ── Loading state: just hide choices, keep everything else ──
    yield (
        gr.update(),
        gr.update(visible=False),
        gr.update(),
        gr.update(),
        session_id,
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(visible=False),
        gr.update(),
        gr.update(),
        gr.update(),
    )

    try:
        final_resp = await _gm.process_action(session_id, choice_id)
    except Exception as exc:
        logger.error("Generation failed: %s", exc)
        raise gr.Error(str(exc))

    # ── Handle ending ──
    if final_resp.is_ending:
        ending_resp = await _gm.resolve_ending(session_id)
        ending = ending_resp.ending
        epilogue = ending_resp.epilogue
        chronicle = ending_resp.chronicle

        text = (
            f"## ✦ {ending.title} ─ {ending.subtitle}\n\n"
            f"{epilogue}\n\n"
            f"> **核心訊息：** {ending.moral}\n\n"
            f"---\n"
            f"### 旅程紀錄\n"
            f"- 玩家：{chronicle.player_name}\n"
            f"- 行動次數：{chronicle.journey['total_actions']}\n"
            f"- 最終傾向：{chronicle.journey['alignment_summary']}\n"
        )

        if chronicle.key_decisions:
            text += "\n### 關鍵抉擇\n"
            for d in chronicle.key_decisions:
                text += f"- 第 {d['chapter']} 章：{d['decision']}\n"

        yield (
            text,
            gr.update(choices=[], visible=False),
            _resolve_image(ending_resp.image_url),
            "",
            session_id,
            gr.update(visible=False),
            gr.update(visible=False),
            "",
            gr.update(visible=False),
            text,
            _resolve_image(ending_resp.image_url),
            gr.update(visible=True),
        )
        return

    # ── Normal turn ──
    choice_labels = [c.text for c in final_resp.choices]
    choice_ids = [c.id for c in final_resp.choices]
    _update_choice_id_map(choice_labels, choice_ids)

    world = final_resp.world_state
    status = (
        f"回合 {final_resp.current_turn} | Stage {final_resp.stage}　"
        f"🌍 {world.continent}　"
        f"秩序 {world.alignment.order}　混沌 {world.alignment.chaos}　"
        f"科技 {world.alignment.technology}　自然 {world.alignment.nature}"
    )

    yield (
        final_resp.narrative,
        gr.update(choices=choice_labels, value=None, visible=True),
        _resolve_image(final_resp.image_url),
        status,
        session_id,
        gr.update(visible=False),
        gr.update(visible=True),
        "",
        gr.update(visible=True),
        "",
        _resolve_image(final_resp.image_url),
        gr.update(visible=False),
    )


_choice_id_map: dict = {}


def _update_choice_id_map(labels, ids):
    global _choice_id_map
    _choice_id_map = dict(zip(labels, ids))


def _get_choice_id_map():
    return _choice_id_map


async def reset_game():
    global _choice_id_map
    _choice_id_map = {}
    return (
        "",
        gr.update(choices=[], value=None, visible=False),
        None,
        "",
        "",
        gr.update(visible=True),
        gr.update(visible=False),
        "",
        gr.update(visible=False),
        "",
        None,
        gr.update(visible=False),
    )


with gr.Blocks(
    title="幻境編年史：紀元餘燼",
) as demo:
    session_id = gr.State("")
    player_name_state = gr.State("")

    gr.HTML(
        '<div class="game-title">幻境編年史</div>'
        '<div class="game-subtitle">紀元餘燼</div>'
    )

    # ── Start Screen ──────────────────────────────────
    with gr.Column(visible=True, elem_id="start-screen") as start_screen:
        gr.Markdown(
            "大凋零之後，世界碎裂成五塊浮空大陸。"
            "你被一股未知的力量喚醒，身軀之下是冰冷的石台……"
        )
        name_input = gr.Textbox(
            label="你的名字",
            placeholder="輸入紀元行者的名字…",
            max_length=20,
        )
        start_btn = gr.Button("踏入艾特拉", variant="primary", size="lg")

    # ── Game Screen ───────────────────────────────────
    with gr.Column(visible=False, elem_id="game-screen") as game_screen:
        with gr.Row():
            with gr.Column(scale=1, min_width=280):
                scene_img = gr.Image(
                    label=None,
                    show_label=False,
                    height=340,
                    elem_classes="scene-image",
                )
                world_status = gr.Markdown(
                    "", elem_classes="status-label"
                )

            with gr.Column(scale=2):
                narrative = gr.Markdown(
                    "",
                    elem_classes="narrative-box",
                )
                choice_radio = gr.Radio(
                    choices=[],
                    label="選擇你的下一步",
                    visible=False,
                    interactive=True,
                )
                with gr.Row(visible=False) as action_row:
                    submit_btn = gr.Button("確認", variant="primary", size="sm", scale=0)

        with gr.Row():
            reset_btn = gr.Button("↺ 重新開始", size="sm", scale=0)

    # ── Ending Screen ─────────────────────────────────
    with gr.Column(visible=False, elem_id="ending-screen") as ending_screen:
        ending_text = gr.Markdown("")
        ending_img = gr.Image(
            label=None,
            show_label=False,
            height=400,
        )
        restart_btn = gr.Button("↺ 再次啟程", variant="primary", size="lg")

    # ── Event Wiring ──────────────────────────────────

    start_btn.click(
        fn=start_game,
        inputs=[name_input],
        outputs=[
            narrative,
            choice_radio,
            scene_img,
            world_status,
            session_id,
            start_screen,
            game_screen,
            player_name_state,
            action_row,
            ending_text,
            ending_img,
            ending_screen,
        ],
    )

    submit_btn.click(
        fn=make_choice,
        inputs=[choice_radio, session_id],
        outputs=[
            narrative,
            choice_radio,
            scene_img,
            world_status,
            session_id,
            start_screen,
            game_screen,
            player_name_state,
            action_row,
            ending_text,
            ending_img,
            ending_screen,
        ],
    )

    reset_btn.click(
        fn=reset_game,
        inputs=None,
        outputs=[
            narrative,
            choice_radio,
            scene_img,
            world_status,
            session_id,
            start_screen,
            game_screen,
            player_name_state,
            action_row,
            ending_text,
            ending_img,
            ending_screen,
        ],
    )

    restart_btn.click(
        fn=reset_game,
        inputs=None,
        outputs=[
            narrative,
            choice_radio,
            scene_img,
            world_status,
            session_id,
            start_screen,
            game_screen,
            player_name_state,
            action_row,
            ending_text,
            ending_img,
            ending_screen,
        ],
    )


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        allowed_paths=[str(_STATIC_DIR)],
        theme=gr.themes.Soft(
            primary_hue="orange",
            neutral_hue="slate",
            font=("Noto Serif TC", "sans-serif"),
        ),
        css=CSS,
        debug=True
    )
