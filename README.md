# 幻境編年史：紀元餘燼 (Ember of Epochs)

> LLM 驅動的文字冒險 RPG，結合 Stable Diffusion 即時場景繪製

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-5%2B-F97316?logo=gradio)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

---

## 目錄

- [Overview](#overview)
- [Core Features](#core-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Development](#development)
- [License](#license)

---

## Overview

玩家扮演一名失去記憶的「紀元行者」，在「大凋零」後碎裂成五塊浮空大陸的世界中探索。每一回合，LLM 根據玩家的選擇生成故事、三種行動選項、以及對應的場景圖像，最終導向五種截然不同的結局。

遊戲進程分為三章（共 15 個 Stage、30 回合），支持四個陣營軸線（秩序/混沌、科技/自然）的動態變化。

**核心機制：**

- LLM 輸出採用結構化標籤（`<story>` / `<options>` / `<visual_prompt>`），便於前端解析
- Static system prompt 設計最大化 KV-cache 重用
- 每次動作皆透過 Stable Diffusion 生成場景圖像

---

## Core Features

- **LLM 驅動敘事** — 支援 OpenAI API 與本地 GGUF 模型（llama-cpp-python）
- **即時 AI 繪圖** — 每次動作自動生成 512×512 場景圖像（SDXL-Turbo / Diffusers）
- **多線結局系統** — 5 種結局，根據玩家在四個陣營軸線上的累積傾向觸發
- **三幕劇腳本** — 3 章 × 5 Stage × 2 回合，附帶每階段情節指引與隨機事件主題
- **雙介面支援** — Gradio Web UI（主要前端）與 FastAPI REST API

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Gradio Web UI (7860)                        │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────────┐ │
│  │ Start    │  │ Narrative    │  │ Choice   │  │ Ending Screen  │ │
│  │ Screen   │  │ + Scene Img  │  │ Buttons  │  │ + Chronicle    │ │
│  └──────────┘  └──────────────┘  └──────────┘  └────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                        GameMaster (Core Loop)                       │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐  ┌───────────────┐ │
│  │ Prompt     │─→│ LLM        │─→│ Struct    │─→│ Alignment +   │ │
│  │ Generator  │  │ Provider   │  │ Parser    │  │ History Store │ │
│  └────────────┘  └────────────┘  └───────────┘  └───────────────┘ │
│                                                       │            │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐       │            │
│  │ Ending     │  │ Chronicle  │  │ Script    │       │            │
│  │ Service    │  │ Service    │  │ Config    │       │            │
│  └────────────┘  └────────────┘  └───────────┘       │            │
│                                                       ▼            │
│                                          ┌──────────────────────┐  │
│                                          │ BigPickle Pipeline   │  │
│                                          │ (SDXL-Turbo)         │  │
│                                          │  + SceneCompiler     │  │
│                                          │  + StyleController   │  │
│                                          └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

**Data Flow (per turn):**

1. 玩家選擇行動 → `make_choice()`
2. `GameMaster.process_action()` 建構 user prompt（含章節目標、情節指引、隨機事件主題）
3. LLM 產生結構化輸出（`<story>` JSON + `<options>` + `<visual_prompt>`）
4. `StructParser` 解析輸出，提取敘事、選項、alignment delta、scene tags
5. `AlignmentService` 套用陣營偏移
6. `BigPicklePipeline` 根據 scene tags / visual prompt 生成場景圖像
7. 歷史記錄寫入 Session，回傳 `ActionResponse` 至前端

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI 0.115+ | REST API 伺服器 |
| **Frontend** | Gradio 5+ | 互動式 Web UI |
| **LLM Backend** | OpenAI SDK / llama-cpp-python | 故事生成 |
| **Image Generation** | Diffusers + SDXL-Turbo | 場景繪圖 |
| **Image Processing** | Pillow 10+ | 佔位圖生成、影像處理 |
| **Data Validation** | Pydantic 2+ | 設定檔與資料模型 |
| **Optional GPU** | PyTorch 2.2+ / CUDA | 圖像生成加速 |

---

## Getting Started

### Requirements

- Python 3.10+
- pip / venv
- （可選）NVIDIA GPU + CUDA 以加速圖像生成
- （可選）GGUF 模型檔案用於本地 LLM 推理

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r ../requirements.txt
```

### Configuration

複製 `.env.example` 為 `.env` 並依環境修改：

```bash
cp ../.env.example .env
```

**主要設定項（`config.py`）：**

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openai` | `openai` 或 `local` |
| `LLM_MODEL_NAME` | `gpt-4o-mini` | 模型名稱或 GGUF 路徑 |
| `LLM_API_KEY` | `""` | OpenAI API Key |
| `LLM_API_BASE` | `""` | 自訂 API 端點 |
| `LLM_TEMPERATURE` | `0.7` | 生成溫度 |
| `LLM_MAX_TOKENS` | `2048` | 最大輸出 token 數 |
| `BIGPICKLE_MODEL_PATH` | `models/sdxl-turbo` | Diffusers 模型路徑 |
| `BIGPICKLE_DEVICE` | `cuda` | 推理裝置 |

### Run

**Gradio UI（主要使用方式）：**

```bash
python -m app.gradio_app
```

瀏覽器開啟 `http://localhost:7860`

**FastAPI Server（REST API）：**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API 文件自動產生於 `http://localhost:8000/docs`

---

## Usage

### Gradio Web UI

1. 輸入角色名稱，點選「踏入艾特拉」開始遊戲
2. 閱讀故事，從三個選項中擇一
3. 每次選擇後自動生成下一段故事與場景圖像
4. 遊戲結束時顯示結局畫面與旅程紀錄

### REST API

```bash
# 開新遊戲
curl -X POST http://localhost:8000/api/new-game \
  -H "Content-Type: application/json" \
  -d '{"player_name": "行者", "difficulty": "normal"}'

# 提交行動
curl -X POST http://localhost:8000/api/action \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "choice_id": "c1"}'

# 結局
curl -X POST http://localhost:8000/api/ending \
  -H "Content-Type: application/json" \
  -d '{"session_id": "..."}'
```

---

## Project Structure

```
app/
├── config.py                 # Pydantic Settings（環境變數載入）
├── main.py                   # FastAPI 應用入口
├── gradio_app.py             # Gradio Web UI
│
├── models/                   # 資料模型
│   ├── world.py              # Alignment, WorldState, SceneTags
│   ├── session.py            # Session, Choice
│   └── action.py             # 請求/回應模型、LLMOutput
│
├── routers/
│   └── game.py               # REST API 路由
│
├── services/
│   ├── game_master.py        # 核心遊戲循環（GameMaster）
│   ├── alignment.py          # 陣營軸線服務
│   ├── chronicle.py          # 旅程紀錄服務
│   ├── ending.py             # 結局判定服務（5 種結局）
│   ├── script_config.py      # 三幕劇腳本、回合計算、隨機事件
│   │
│   ├── llm/                  # LLM 整合
│   │   ├── provider.py       # OpenAI / Local LLM 供應商
│   │   ├── prompt_generator.py  # 提示詞建構
│   │   └── struct_parser.py  # 結構化輸出解析器
│   │
│   ├── image/                # 圖像生成管線
│   │   ├── big_pickle_pipeline.py  # Diffusers 封裝
│   │   ├── scene_compiler.py       # 場景標籤 → 英文 prompt
│   │   ├── style_controller.py     # 大陸 → 美術風格映射
│   │   ├── guidance_scheduler.py   # CFG 排程器
│   │   └── image_cache.py         # LRU 磁碟快取
│   │
│   └── prompts/              # 靜態提示詞模板
│       ├── system_prompt.py  # 輸出格式、多樣性規則
│       └── world_lore.py     # 世界觀設定
│
├── lora/                     # LoRA 權重檔（可選）
├── static/                   # 靜態資源／生成圖片
│
tests/                        # 測試
├── conftest.py               # Mock LLM / Mock BigPickle
├── test_ending.py            # 結局服務測試
├── test_frontend.py          # API 客戶端測試
└── test_integration.py       # 整合測試
```

---

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Prompts

| File | Description |
|---|---|
| `services/prompts/system_prompt.py` | Static system prompt（KV-cache 友好） |
| `services/llm/prompt_generator.py` | User prompt builder（含動態變數注入） |

### Adding a New Chapter

編輯 `services/script_config.py` 中的 `CHAPTERS` 列表，指定：

- `chapter` / `title` / `chapter_goal`
- `continents`（大陸列表，2 個時 Stage 1-3 用第一個、4-5 用第二個）
- `stages`（每 Stage 的 `plot_directive`、`label`）

### Adding a New Ending

1. 在 `services/ending.py` 新增 `EndingDef`
2. 設定觸發閾值（alignment 門檻）
3. 在 `test_ending.py` 新增對應測試

---

## License

MIT
