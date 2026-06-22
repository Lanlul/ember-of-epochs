# 開發日誌：幻境編年史：紀元餘燼 (Ember of Epochs)

> 產生日期：2026-06-22
> 協作模型：big-pickle (opencode build agent)
> 總計：輸入 1,061,754 tokens · 輸出 244,858 tokens · 推理 142,374 tokens

---

## 一、專案協作概覽 (Overview)

本專案的目標是打造一款 **LLM 驅動敘事、Diffusion Model 即時繪圖的文字 RPG 遊戲**。開發流程分為三個階段，由 opencode build agent 與使用者反覆協作完成：

| 階段 | 內容 | 產出 |
|------|------|------|
| **提案** | 產品定位、世界觀設計、技術選型 | `README.md` |
| **架構設計** | 系統架構圖、API 格式、任務拆解 | `ARCHITECTURE.md` |
| **實作 (T1-T7)** | 7 項任務依序疊代，含測試與除錯 | 完整 `app/` 後端 + `frontend/` 前端 + `tests/` |

最終產出一套包含 **FastAPI 後端、LLM 推論模組、Big Pickle 圖片生成管線、React 前端與 Gradio UI** 的全端應用，共 31 項測試全數通過。

---

## 二、關鍵 Prompt 紀錄 (Key Prompts)

### 2.1 專案啟動 Prompt

> 你現在是一位資深的 AI 產品經理。我要做一個「文字 RPG 遊戲」，遊戲能根據玩家的選擇推進劇情，並即時生成符合當下情況的情境圖片。故事背景請發揮創意自行設計。
>
> 請幫我在目前的資料夾中生成一份符合 Markdown 格式的專題提案，並自動存成 README.md 檔案。

**用途**：啟動整個專案的第一個 Prompt，要求生成完整的產品提案。Agent 自主設計了「幻境編年史：紀元餘燼」的世界觀——五座浮空大陸、大凋零、紀元行者，並給出了完整的技術堆疊規劃（LLM + Big Pickle Flow Matching）。

---

### 2.2 架構設計 Prompt

> 你現在是一位資深軟體架構師。請閱讀剛剛生成的 README.md，我們現在要進行「階段二：架構設計與任務拆解」。
>
> 請幫我產出一份 ARCHITECTURE.md，內容需包含：
> 1. 系統架構圖 (Mermaid 語法)
> 2. API 資料交換格式
> 3. 開發任務拆解清單 (5-7 個步驟)

**用途**：將產品概念轉化為可執行的技術架構。Agent 產出了 Mermaid 架構圖、完整的 JSON API 規格（`/api/new-game`、`/api/action`、`/api/ending`），以及 7 項具依賴關係的開發任務（T1-T7）。

---

### 2.3 任務實作迭代模式

```
使用者：請幫我根據 ARCHITECTURE.md 內容，首先撰寫 T1，等我說繼續下一個步驟，才能繼續
Agent：  (實作 T1 後回報)
使用者：請繼續實作下一步驟
Agent：  (詢問先進行 T2 或 T3 平行任務)
```

**用途**：採用「使用者觸發下一步」的疊代模式，每次只專注一項任務，確保每個步驟都經過驗證再繼續。Agent 會在必要時提問（如平行任務的優先順序），而非擅自決定。

---

### 2.4 問題診斷 Prompt

> gradio 無法連線

**用途**：簡潔的問題回報，觸發 Agent 進行系統性除錯。Agent 發現了兩個根因——`.env` 中殘留本地模型路徑導致導入錯誤、以及 Gradio 版本相容性問題，最終透過降級 Gradio 與修正 `.env` 解決。

---

### 2.5 技術轉向 Prompt

> 請幫我改用本地模型

**用途**：要求從 OpenAI API 切換為本地 GGUF 模型。Agent 自主完成了：下載 Qwen2.5-7B-Instruct GGUF、安裝 llama-cpp-python、修改 Provider 層支援本地推論、調整 `n_ctx` 與 `repeat_penalty` 等超參數。

---

## 三、工具組合應用 (Toolchain Usage)

### 3.1 角色分工

| 工具 | 角色 | 具體應用情境 |
|------|------|-------------|
| **opencode (big-pickle)** | **協作大腦** | Prompt 理解、程式碼生成、架構決策、除錯分析、任務拆解與排程 |
| **CLI (bash)** | **執行臂** | `mkdir -p` 建立目錄、`pip install` 安裝依賴、`uvicorn` 啟動驗證、`curl` API 測試、`pytest` 執行測試、`huggingface-cli` 下載模型 |
| **Big Pickle** | **圖片生成引擎** | Diffusers 封裝、SDXL-Turbo 推論、Scene Tags → English Prompt 編譯、LoRA 風格控制、CFG 排程 |

### 3.2 協作流程範例

以 T2 (LLM 模組) 實作為例，展示三工具如何配合：

```
1. [opencode] 規劃 LLM Provider 抽象層、Prompt Generator、Struct Parser 三個子模組
2. [opencode] 寫入 provider.py / prompt_generator.py / struct_parser.py
3. [CLI]      python -c "測試 Struct Parser 能否正確解析 JSON 輸出"
4. [opencode] 根據測試結果修正 regex 與 fallback 邏輯
5. [CLI]      uvicorn + curl 進行端到端 API 驗證
6. [opencode] 更新 todo list，標記 T2 完成
```

### 3.3 關鍵整合點

- **opencode ↔ CLI**：Agent 透過 bash 執行所有環境操作（安裝、啟動、測試），並從 CLI 輸出中讀取錯誤訊息進行診斷
- **opencode ↔ Big Pickle**：Agent 撰寫 `BigPicklePipeline` 封裝 Diffusers，並在 `GameMaster._finalize_turn()` 中呼叫，實現 LLM 輸出 → Scene Tags → 圖片生成的完整鏈路
- **Big Pickle ↔ CLI**：Big Pickle 依賴 `torch` + `diffusers`，透過 CLI 安裝；SDXL-Turbo 模型透過 `huggingface-cli` 下載

---

## 四、Agent 協助解決之技術問題 (Technical Challenges Resolved)

### 4.1 Gradio 無法連線

**現象**：Gradio 啟動後瀏覽器無法連線，且 log 出現 `StarletteDeprecationWarning`。

**診斷過程**：
1. Agent 檢查 `.env`，發現殘留 `LLM_PROVIDER=local` + `LLM_MODEL_NAME=.../Qwen2.5...gguf`，但 GGUF 不存在導致模型載入失敗，阻斷了 Gradio 啟動
2. 進一步發現 Gradio 5.x 的 `gr.Slider` 改用 `scale` 替代 `step`，與現有程式碼不相容
3. Agent 最後發現兩個 Gradio 程序爭搶 GPU 導致 CUDA OOM

**解決方案**：
- 清除 `.env` 中不相關的設定，改用預設值 (OpenAI)
- 降級 Gradio 至相容版本或修正 API 用法
- 引入 CUDA 清理機制，確保舊程序先釋放 GPU 資源

---

### 4.2 LLM Struct Parser JSON 解析失敗

**現象**：LLM 輸出 JSON 因 `max_tokens` 上限被截斷（卡在 `"charac`），導致 `json.loads` 失敗。

**診斷過程**：
1. Agent 檢視 error log，發現 JSON 在 `scene_tags.character_state` 欄位中被截斷
2. 計算輸出長度：JSON narrative + 3 choices + scene_tags 7 欄位 ≈ 900 tokens，加上 `<options>` + `<visual_prompt>` ≈ 1200 tokens
3. 原設定 `llm_max_tokens=1024` 幾乎沒有餘量

**解決方案**：
- 將 `llm_max_tokens` 從 1024 提高至 2048
- 在 `_fallback_parse` 中實作 regex 容錯機制，即使 JSON 截斷也能提取已產生的欄位

---

### 4.3 本地模型 Context 長度不足

**現象**：使用 Qwen2.5-7B GGUF 時，完整歷史記錄（30 回合）超出 `n_ctx` 限制。

**診斷過程**：
1. Agent 檢查 `LocalProvider` 初始化參數，發現 `n_ctx` 未設定（使用 llama.cpp 預設值 512）
2. 計算每回合 token 用量：System prompt (static) ≈ 700t + 30 回合 × (narrative 200t + user choice 20t) ≈ 7,300t

**解決方案**：
- 將 `n_ctx` 設定為 8192，足以容納完整 30 回合遊戲
- 同時引入 rolling-window 機制作為安全邊界（`MAX_PROMPT_CHARS=6000`）

---

### 4.4 React 前端無法與 API 連線

**現象**：`Vite` 開發伺服器的請求遭 CORS 阻擋，且 `POST /api/action` 因 session UUID 格式問題回傳 422。

**診斷過程**：
1. Agent 檢查 Vite proxy 設定，發現未將 `/api` 路徑轉發至 FastAPI 後端
2. 檢查 FastAPI 端 `POST /api/action` 的 session_id 驗證，發現未使用 UUID 格式

**解決方案**：
- 在 `vite.config.js` 中加入 `server.proxy` 設定
- 統一使用 `uuid4()` 產生 session_id，確保格式一致性

---

### 4.5 CUDA GPU 記憶體競爭

**現象**：同時啟動 Gradio (載入 LLM + Big Pickle) 與其他 CUDA 程序時，出現 `CUDA out of memory`。

**診斷過程**：
1. Agent 檢查 `nvidia-smi` 輸出，發現多個 Python 程序佔用 GPU 記憶體
2. 確認問題根源：先前測試遺留的 Python 程序未釋放 CUDA context

**解決方案**：
- 啟動前加入 `fuser -k` 清理佔用 GPU 的程序
- 在 `BigPicklePipeline` 中加入 `torch.cuda.empty_cache()` 調用
- 建議將 LLM (CPU) 與 Big Pickle (CUDA) 分離在不同程序執行

---

## 五、Agent 協作歷程時間軸 (Agent Collaboration Timeline)

```
Phase 1: 提案
├── [1] 使用者要求生成 RPG 專題提案
├── [2] Agent 產出 README.md（世界觀、功能、技術堆疊）

Phase 2: 架構設計
├── [3] 使用者要求架構設計與任務拆解
├── [4] Agent 產出 ARCHITECTURE.md（Mermaid 圖、API 規格、T1-T7）

Phase 3: T1 — FastAPI 骨架
├── [5] Agent 建立 app/ 目錄結構
├── [6] 撰寫 Pydantic Models (Alignment, WorldState, Session, Choice, ActionRequest/Response)
├── [7] 撰寫 config.py + main.py (CORS / Static mount)
├── [8] 撰寫 game router (POST /api/new-game 200, POST /api/action 501)
├── [9] 驗證：伺服器啟動 + API 回測 OK

Phase 4: T2 — LLM 推論模組
├── [10] 使用者選擇 "先實作 T2"
├── [11] Agent 撰寫 LLMProvider 抽象層（OpenAI + Local）
├── [12] 撰寫 PromptGenerator（static system prompt + dynamic user prompt）
├── [13] 撰寫 StructParser（JSON 解析 + fallback + 標籤提取）
├── [14] 端到端驗證

Phase 5: T3 — Big Pickle 圖片 Pipeline
├── [15] 使用者選擇 "實作 T3"
├── [16] Agent 撰寫 SceneCompiler（SceneTags → 英文 prompt）
├── [17] 撰寫 StyleController（大陸 → 美術風格 + LoRA）
├── [18] 撰寫 GuidanceScheduler（CFG 排程）
├── [19] 撰寫 BigPicklePipeline（Diffusers 封裝）
├── [20] 撰寫 ImageCache（LRU 磁碟快取）
├── [21] 實作 Mock mode（無模型時產生佔位圖）

Phase 6: T4 — Game Master 核心迴圈
├── [22] 使用者選擇 "先實作 T4"
├── [23] Agent 重構 GameMaster（準備、動作、最終化三段式）
├── [24] 實作 AlignmentService（四軸傾向計算）
├── [25] 串接 LLM + Big Pickle + Struct Parser
├── [26] 驗證：choice_id → narrative + choices + image_url

Phase 7: T5 — React 前端
├── [27] 使用者選擇 "先實作 T5"
├── [28] Agent 建立 Vite + React + Tailwind 專案
├── [29] 撰寫 GameScreen 元件
├── [30] 設定 Vite proxy 解決 CORS

Phase 8: T6 — 整合測試
├── [31] Agent 撰寫 conftest.py（MockLLM + MockBigPickle）
├── [32] 撰寫 StructParser / GameMaster 測試
├── [33] 全 17 項測試通過

Phase 9: T7 — 結局系統
├── [34] Agent 撰寫 EndingService（5 種結局）
├── [35] 撰寫 ChronicleService（旅程總結）
├── [36] 新增 14 項測試 → 全 31 項通過

Phase 10: Gradio UI 封裝
├── [37] 使用者要求 "介面封裝與總結"
├── [38] Agent 建立 gradio_app.py
├── [39] 提供 3 種啟動方式

Phase 11: 除錯與調優
├── [40] Gradio 無法連線 → 修正 .env + 版本 + CUDA
├── [41] LLM 輸出截斷 → max_tokens 1024→2048
├── [42] 串流輸出功能實作與移除
├── [43] 切換至本地 GGUF 模型

Phase 12: 最終調整
├── [44] 大陸自動切換功能
├── [45] README.md 更新與 GitHub 推送
```

---

## 附錄：統計數據

| 指標 | 數值 |
|------|------|
| 總對話輪數 | 50+ |
| 總輸入 Token | 1,061,754 |
| 總輸出 Token | 244,858 |
| 推理 Token | 142,374 |
| 快取讀取 | 62,403,968 bytes |
| 實作檔案數 | 31+ |
| 測試案例 | 31 |
| Agent 模式 | build (全權實作) |
