SAMPLE_LLM_RESPONSE = {
    "narrative": "你環顧四周，發現自己身處一座傾倒的星象塔內部。"
                 "破碎的星盤散落一地，牆上的壁畫描繪著天空裂開的景象。"
                 "東側的樓梯通往塔頂，西側的拱門外則是荒蕪的廢土。",
    "choices": [
        {
            "id": "c4",
            "text": "調查塔頂的殘缺星盤",
            "alignment_delta": {"technology": 3, "order": 1},
        },
        {
            "id": "c5",
            "text": "推開腳邊的破舊日誌",
            "alignment_delta": {"order": 2},
        },
        {
            "id": "c6",
            "text": "往塔外廢墟前進",
            "alignment_delta": {"chaos": 2, "nature": 1},
        },
    ],
    "scene_tags": {
        "setting": "傾倒的星象塔內部",
        "mood": "神秘而寂靜",
        "lighting": "月光從屋頂裂縫灑落",
        "color_palette": ["深藍", "灰石", "銀白"],
        "style": "ruins_gothic",
        "focus": "player_character",
        "character_state": "迷茫但警覺",
    },
}

SAMPLE_ENDING_RESPONSE = {
    "title": "秩序的代價",
    "narrative": "你站在克洛諾斯廢土的最高處，手中握著最後一塊紀元碎片。"
                 "天空的裂痕開始癒合，但你深知——"
                 "所有秩序都伴隨著犧牲。",
    "scene_tags": {
        "setting": "廢土之巔，裂痕癒合的蒼穹",
        "mood": "莊嚴而哀傷",
        "lighting": "金色曙光穿透雲層",
        "color_palette": ["金色", "深藍", "純白"],
        "style": "ruins_gothic",
        "focus": "player_character_silhouette",
        "character_state": "疲憊但堅定",
    },
}

RAW_JSON = """{
    "narrative": "你環顧四周，發現自己身處一座傾倒的星象塔內部。破碎的星盤散落一地。",
    "choices": [
        {
            "id": "c4",
            "text": "調查塔頂的殘缺星盤",
            "alignment_delta": {"technology": 3, "order": 1}
        },
        {
            "id": "c5",
            "text": "推開腳邊的破舊日誌",
            "alignment_delta": {"order": 2}
        },
        {
            "id": "c6",
            "text": "往塔外廢墟前進",
            "alignment_delta": {"chaos": 2, "nature": 1}
        }
    ],
    "alignment_delta": {"order": 2, "technology": 1},
    "scene_tags": {
        "setting": "傾倒的星象塔內部",
        "mood": "神秘而寂靜",
        "lighting": "月光從屋頂裂縫灑落",
        "color_palette": ["深藍", "灰石", "銀白"],
        "style": "ruins_gothic",
        "focus": "player_character",
        "character_state": "迷茫但警覺"
    }
}"""

RAW_JSON_CODEBLOCK = """一些前綴文字

```json
{
    "narrative": "你向前走去，推開了沉重的石門。",
    "choices": [
        {
            "id": "c10",
            "text": "走入門內",
            "alignment_delta": {"order": 1}
        }
    ],
    "scene_tags": {
        "setting": "石門之後",
        "mood": "陰森",
        "lighting": "火炬光芒",
        "color_palette": ["暗紅", "黑", "灰"],
        "style": "ruins_gothic",
        "focus": "doorway",
        "character_state": "謹慎"
    }
}
```

一些後綴文字"""

RAW_MALFORMED = "這不是 JSON"
