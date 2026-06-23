# 幻境編年史：紀元餘燼 (Ember of Epochs)

> LLM-driven interactive text adventure RPG with real-time AI-generated scene illustrations.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-5%2B-F97316?logo=gradio)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

---

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Development](#development)
- [License](#license)

---

## Overview

玩家扮演一名失去記憶的「紀元行者」，在「大凋零」後碎裂成五塊浮空大陸的世界中探索。每一回合，LLM 根據玩家的選擇生成故事、三種行動選項，並透過 Stable Diffusion 繪製對應的場景圖像，最終導向五種截然不同的結局。

遊戲進程由三幕劇腳本驅動：3 章 × 5 個 Stage × 2 回合，共 30 回合。支援四個陣營軸線（秩序／混沌、科技／自然）的動態偏移，影響劇情走向與結局判定。

### Key Design Decisions

- **結構化 LLM 輸出** — LLM 回傳 `<story>`（JSON）、`<options>`、`<visual_prompt>` 三個區塊，前端無需二次推理解析
- **Static System Prompt** — 系統提示詞完全靜態，最大化 LLM KV-cache 重用，降低延遲與成本
- **多供應商抽象** — 同一 `LLMProvider` 介面支援 OpenAI API 與本地 GGUF 模型，切換僅需修改環境變數

---

## Core Features

- **LLM 驅動敘事** — 支援 OpenAI API（GPT-4o-mini）與本地 GGUF 模型（llama-cpp-python / Qwen2.5），temperature、repetition penalty 等超參可調
- **即時 AI 繪圖** — 每回合自動生成 512×512 場景圖像（SDXL-Turbo / Diffusers），支援五種大陸風格（哥德廢土、蒸氣龐克、生機魔法、冰霜史詩、超現實虛空）
- **多線結局系統** — 5 種結局，根據玩家在四個陣營軸線上的累積傾向（秩序／混沌、科技／自然）自動觸發，附 LLM 生成的 epilogue 與旅程回顧
- **三幕劇腳本引擎** — 3 章 × 5 Stage × 2 回合的固定結構，每 Stage 附獨立情節指引（plot directive），Stage 2/4 有機率觸發隨機事件主題
- **雙介面支援** — Gradio Web UI 為主要互動前端，同時提供 FastAPI REST API 供外部整合

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Gradio Web UI (:7860)                          │
│  ┌──────────┐  ┌────────────────┐  ┌──────────┐                 │
│  │ Start    │  │ Narrative      │  │ Choice   │                 │
│  │ Screen   │  │ + Scene Image  │  │ Buttons  │                 │
│  └──────────┘  └────────────────┘  └──────────┘                 │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                       GameMaster (Core Loop)                     │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────┐             │
│  │ Prompt      │──→│ LLM          │──→│ Struct    │             │
│  │ Generator   │   │ Provider     │   │ Parser    │             │
│  └─────────────┘   └──────────────┘   └───────────┘             │
│                                            │                     │
│  ┌─────────────┐   ┌──────────────┐        ▼                     │
│  │ Ending      │   │ Chronicle    │  ┌───────────────┐           │
│  │ Service     │   │ Service      │  │ Alignment +   │           │
│  └─────────────┘   └──────────────┘  │ History Store │           │
│                                       └───────┬───────┘           │
│                                               ▼                   │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │              BigPickle Pipeline (SDXL-Turbo)              │    │
│  │  SceneCompiler → StyleController → GuidanceScheduler      │    │
│  │  → Diffusers → ImageCache (LRU)                          │    │
│  └───────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow (per turn)

1. 玩家選擇行動 → `make_choice()` via Gradio
2. `GameMaster.process_action()` 建構 user prompt（含章節目標、情節指引、玩家上次選擇、隨機事件主題）
3. LLM 產生結構化輸出（`<story>` JSON + `<options>` + `<visual_prompt>`）
4. `StructParser` 解析：提取敘事、選項文字、alignment delta、scene tags
5. 若 LLM 未產生選項（空 `choices`），自動用 `<options>` 區塊補上並最多重試 2 次
6. `AlignmentService` 套用陣營偏移，寫入 Session 歷史
7. `BigPicklePipeline` 根據 scene tags 或 visual prompt 生成場景圖像（mock 模式若無模型）
8. 回傳 `ActionResponse` 至前端更新畫面

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI 0.115+ | REST API 伺服器 |
| **Frontend** | Gradio 5+ | 互動式 Web UI |
| **LLM Backend** | OpenAI SDK / llama-cpp-python | 故事生成與結構化輸出 |
| **Image Generation** | Diffusers + SDXL-Turbo | 場景圖像繪製 |
| **Image Processing** | Pillow 10+ | 佔位圖生成 |
| **Data Validation** | Pydantic 2+ / Pydantic Settings | 設定檔與資料模型 |
| **Optional GPU** | PyTorch 2.2+ / CUDA | 圖像生成硬體加速 |

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip + virtualenv (recommended)
- (Optional) NVIDIA GPU with CUDA for image generation
- (Optional) GGUF model file for local LLM inference

### Clone & Setup

```bash
git clone <your-repo-url>
cd app

python -m venv venv
source venv/bin/activate      # Linux / macOS
# venv\Scripts\activate       # Windows

pip install -r ../requirements.txt
```

### Environment Variables

複製 `.env.example` 為 `.env`，依執行環境修改：

```bash
cp ../.env.example .env
```

**核心變數：**

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openai` | `openai` 或 `local` |
| `LLM_MODEL_NAME` | `gpt-4o-mini` | 模型名稱或 GGUF 檔案路徑 |
| `LLM_API_KEY` | `""` | OpenAI API Key（provider=openai 時必填） |
| `LLM_TEMPERATURE` | `0.7` | 生成溫度 |
| `LLM_MAX_TOKENS` | `2048` | 最大輸出 token 數 |
| `LLM_REPETITION_PENALTY` | `1.15` | 重複懲罰（local 用） |
| `BIGPICKLE_MODEL_PATH` | `models/sdxl-turbo` | Diffusers 模型路徑 |
| `BIGPICKLE_DEVICE` | `cuda` | 推理裝置（cuda / cpu） |
| `BIGPICKLE_INFERENCE_STEPS` | `4` | 推論步數 |

**本地 LLM 範例（.env）：**

```env
LLM_PROVIDER=local
LLM_MODEL_NAME=/path/to/Qwen2.5-7B-Instruct.Q4_K_M.gguf
LLM_TEMPERATURE=0.65
LLM_MAX_TOKENS=1024
LLM_REPETITION_PENALTY=1.15
```

### Run

**Gradio Web UI（主要使用方式）：**

```bash
python -m app.gradio_app
```

開啟瀏覽器前往 `http://localhost:7860`

**FastAPI Server（REST API）：**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API 文件：`http://localhost:8000/docs`

---

## Usage

### Gradio Web UI

1. 輸入角色名稱，點選「踏入艾特拉」開始遊戲
2. 序幕故事出現後，從三個行動選項中選擇一個
3. 每次選擇後自動生成下一段敘事、新選項與場景圖像
4. Stage 2/4 有機率觸發隨機事件（環境危機、不速之客等）
5. 最終章 Stage 5 觸發結局，顯示旅程紀錄

### REST API

```bash
# 開新遊戲
curl -s -X POST http://localhost:8000/api/new-game \
  -H "Content-Type: application/json" \
  -d '{"player_name": "行者"}' | jq .

# 提交行動（從上一步回傳的 choices 中選擇 id）
curl -s -X POST http://localhost:8000/api/action \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session_id>", "choice_id": "c1"}' | jq .

# 查詢結局
curl -s -X POST http://localhost:8000/api/ending \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session_id>"}' | jq .
```

---

## Project Structure

```
app/
├── config.py                  # Pydantic Settings（.env → 型別安全設定）
├── main.py                    # FastAPI 應用入口
├── gradio_app.py              # Gradio Web UI
│
├── models/                    # 資料模型（Pydantic BaseModel）
│   ├── world.py               # Alignment, WorldState, SceneTags
│   ├── session.py             # Session, Choice
│   └── action.py              # API 請求/回應、LLMOutput、EndingResponse
│
├── routers/
│   └── game.py                # REST API 路由
│
├── services/
│   ├── game_master.py         # 核心遊戲循環（GameMaster）
│   ├── alignment.py           # 陣營軸線服務
│   ├── chronicle.py           # 旅程回顧與 epilogue 生成
│   ├── ending.py              # 結局判定（5 種結局、alignment 閾值）
│   ├── script_config.py       # 三幕劇腳本、回合計算、隨機事件
│   │
│   ├── llm/                   # LLM 供應商與提示詞
│   │   ├── provider.py        # OpenAI / Local provider 抽象層
│   │   ├── prompt_generator.py # System / User prompt 建構
│   │   └── struct_parser.py   # LLM 結構化輸出解析器（JSON + 標籤）
│   │
│   ├── image/                 # 圖像生成管線
│   │   ├── big_pickle_pipeline.py  # Diffusers 封裝（mock 模式降級）
│   │   ├── scene_compiler.py       # SceneTags → 英文繪圖 prompt
│   │   ├── style_controller.py     # 大陸名稱 → 美術風格映射
│   │   ├── guidance_scheduler.py   # CFG scale 排程
│   │   └── image_cache.py         # LRU 磁碟快取（SHA256 key）
│   │
│   └── prompts/               # 靜態提示詞模板
│       └── system_prompt.py   # 世界觀、輸出格式、多樣性規則
│
├── lora/                      # LoRA 權重檔（選用）
├── static/                    # 靜態資源與生成圖片
│
tests/
├── conftest.py                # Mock LLM / Mock BigPickle  fixtures
├── test_ending.py             # 結局判定測試
├── test_frontend.py           # API 客戶端測試
└── test_integration.py        # 整合測試
```

---

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
ruff check .                    # Lint
ruff format --check .           # Format check
```

### Extending the Script

**Adding a Chapter —** 編輯 `services/script_config.py` 中的 `CHAPTERS` 列表：

```python
{
    "chapter": 4,
    "title": "新章節",
    "chapter_goal": "目標描述",
    "continents": ["大陸A", "大陸B"],
    "stages": [
        {"stage": 1, "turns": (1, 2), "label": "開端", "plot_directive": "..."},
        ...
    ],
}
```

**Adding an Ending —** 在 `services/ending.py` 新增 `EndingDef`，設定 alignment 觸發閾值。

### Prompt Engineering

| File | Description |
|---|---|
| `services/prompts/system_prompt.py` | Static system prompt（KV-cache 友好，不隨回合變化） |
| `services/llm/prompt_generator.py` | User prompt builder（章節目標、情節指引、玩家選擇、隨機事件） |
| `services/llm/struct_parser.py` | LLM 輸出解析器（JSON extraction、tag parsing、lenient fallback） |

LLM 輸出格式為三個連續區塊：

```
<story>
{ "narrative": "...", "choices": [...], "scene_tags": {...} }
</story>
<options>
選項A|選項B|選項C
</options>
<visual_prompt>
1girl, cloak, stone altar, cinematic lighting, masterpiece, 8k resolution
</visual_prompt>
```

---

## License

MIT
