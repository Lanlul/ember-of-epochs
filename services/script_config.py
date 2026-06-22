TURNS_PER_CHAPTER = 10
STAGES_PER_CHAPTER = 5
TURNS_PER_STAGE = 2

CHAPTERS = [
    {
        "chapter": 1,
        "title": "甦醒與真相",
        "chapter_goal": "目標：查明古紀元遺跡的秘密，理解世界崩壞的起因。",
        "continents": ["克洛諾斯廢土", "渥爾肯機械之心"],
        "stages": [
            {
                "stage": 1,
                "turns": (1, 2),
                "label": "甦醒與探索",
                "plot_directive": (
                    "描述周遭環境，讓主角意識到自己身處一個崩壞的世界。"
                    "暗示遺跡中藏有古老的秘密，並給出第一個明確的探索方向。"
                ),
            },
            {
                "stage": 2,
                "turns": (3, 4),
                "label": "危機浮現",
                "plot_directive": (
                    "潛伏的威脅開始顯露——可能是環境異變、陷阱啟動，"
                    "或是敵對勢力的蹤跡。迫使主角做出第一次關鍵抉擇。"
                ),
            },
            {
                "stage": 3,
                "turns": (5, 6),
                "label": "初現轉機",
                "plot_directive": (
                    "主角在危機中找到線索或獲得幫助——"
                    "可能是一個古老裝置的啟動、一段記憶碎片的重現，或遇到首個關鍵角色。"
                ),
            },
            {
                "stage": 4,
                "turns": (7, 8),
                "label": "首章高潮",
                "plot_directive": (
                    "第一章的衝突達到頂點。主角面對第一個重大難關，"
                    "必須動用所有已獲得的線索與資源才能突破。氣氛緊張。"
                ),
            },
            {
                "stage": 5,
                "turns": (9, 10),
                "label": "懸念揭曉",
                "plot_directive": (
                    "【章節結尾】主角解決了眼前的危機，但立刻發現這只是一個更大陰謀的冰山一角。"
                    "請寫出令人震驚的轉折，留下強烈的懸念，引導主角前往下一片大陸。"
                    "禁止總結故事——這是章節結尾，不是全劇終。"
                ),
            },
        ],
    },
    {
        "chapter": 2,
        "title": "追尋與抗爭",
        "chapter_goal": "目標：穿越危機四伏的新大陸，尋找阻止世界崩壞的關鍵力量。",
        "continents": ["翡翠密境", "永凍星環"],
        "stages": [
            {
                "stage": 1,
                "turns": (1, 2),
                "label": "承先啟後",
                "plot_directive": (
                    "【章節開端】緊接著上一幕的震撼發現，主角還在消化情緒，"
                    "但環境迫使他必須立刻啟程前往下一個未知區域。"
                    "請描寫轉移陣地的過程與主角內心的決意。"
                ),
            },
            {
                "stage": 2,
                "turns": (3, 4),
                "label": "新大陸的考驗",
                "plot_directive": (
                    "新大陸的獨特環境帶來全新的挑戰——"
                    "可能是極端的氣候、奇異的生態，或是此處特有的古紀元防衛機制。"
                ),
            },
            {
                "stage": 3,
                "turns": (5, 6),
                "label": "關鍵線索",
                "plot_directive": (
                    "主角在此大陸的核心區域發現了與第一章遺跡相關聯的關鍵證據，"
                    "逐漸拼湊出古紀元崩壞的全貌。獲得重要道具或能力提升。"
                ),
            },
            {
                "stage": 4,
                "turns": (7, 8),
                "label": "迫近核心",
                "plot_directive": (
                    "主角逼近第二章的核心衝突點——"
                    "可能是一座巨大的古紀元設施、一個操控大陸生態的裝置，"
                    "或是一個掌握關鍵真相的存在。進入戰鬥或對峙。"
                ),
            },
            {
                "stage": 5,
                "turns": (9, 10),
                "label": "真相浮現",
                "plot_directive": (
                    "【中章結局】主角成功突破了第二章的難關，獲得重大真相——"
                    "但這個真相顯示最終的威脅遠比想像的更加巨大。"
                    "請寫出一個階段性的勝利與隨之而來的更大懸念。"
                    "禁止總結故事——這是中章結尾，不是全劇終。"
                ),
            },
        ],
    },
    {
        "chapter": 3,
        "title": "終焉與紀元",
        "chapter_goal": "目標：集結所有力量，面對古紀元災變的源頭，決定世界的命運。",
        "continents": ["虛空迴廊"],
        "stages": [
            {
                "stage": 1,
                "turns": (1, 2),
                "label": "終局開端",
                "plot_directive": (
                    "【最終章開端】主角帶著前兩章的線索與力量，"
                    "穿越虛空抵達一切災變的源頭。最終舞台的壯闊與危險撲面而來。"
                ),
            },
            {
                "stage": 2,
                "turns": (3, 4),
                "label": "最後的考驗",
                "plot_directive": (
                    "最終區域的防衛機制全力運轉，主角面對最艱難的挑戰——"
                    "這可能是古紀元最強的守護者、時空錯亂的陷阱，"
                    "或是主角內心最深處的心魔實體化。"
                ),
            },
            {
                "stage": 3,
                "turns": (5, 6),
                "label": "最終覺醒",
                "plot_directive": (
                    "在極限壓力下，主角激發出真正的力量或理解了一切真相——"
                    "古紀元行者的使命與世界的真正命運在此揭曉。"
                ),
            },
            {
                "stage": 4,
                "turns": (7, 8),
                "label": "最終對決",
                "plot_directive": (
                    "與災變源頭的最終對決。"
                    "所有伏筆在此回收，主角必須做出最後的關鍵抉擇，"
                    "這個抉擇將直接決定結局走向。氣氛極度緊張。"
                ),
            },
            {
                "stage": 5,
                "turns": (9, 10),
                "label": "大結局",
                "plot_directive": (
                    "根據主角最後的抉擇與整趟旅程的傾向，"
                    "給出一個明確且無懸念的結局（生存或死亡、救贖或毀滅）。"
                    "故事必須在這裡徹底畫下句點。"
                ),
            },
        ],
    },
]

EVENT_THEMES = [
    "環境與空間危機",
    "不速之客的介入",
    "關鍵資源或裝備的損壞與匱乏",
    "主角身體或心理的突發狀況",
    "意外發現的隱藏資訊",
]

TRIGGER_STAGES = {2, 4}
TRIGGER_PROBABILITY = 0.6

FINAL_STAGE_WARNING = (
    "【絕對警告】這是整個遊戲的最終結局。你必須在本次回覆中徹底結束整個故事，"
    "寫出結局。絕對禁止留下伏筆、絕對禁止反問玩家要做什麼，"
    "故事必須在這裡畫下句點。"
)


def global_turn_to_chapter(global_turn: int) -> int:
    return (global_turn - 1) // TURNS_PER_CHAPTER + 1


def global_turn_to_local_turn(global_turn: int) -> int:
    return (global_turn - 1) % TURNS_PER_CHAPTER + 1


def chapter_stage_from_turn(global_turn: int):
    chapter = global_turn_to_chapter(global_turn)
    local_turn = global_turn_to_local_turn(global_turn)
    stage = (local_turn - 1) // TURNS_PER_STAGE + 1
    stage_turn = (local_turn - 1) % TURNS_PER_STAGE + 1
    return chapter, stage, stage_turn


def get_chapter_config(chapter: int) -> dict:
    for c in CHAPTERS:
        if c["chapter"] == chapter:
            return c
    return CHAPTERS[-1]


def get_stage_config(global_turn: int) -> dict:
    chapter, stage, _ = chapter_stage_from_turn(global_turn)
    chapter_cfg = get_chapter_config(chapter)
    for s in chapter_cfg["stages"]:
        if s["stage"] == stage:
            return s
    return chapter_cfg["stages"][-1]


def get_chapter_goal(global_turn: int) -> str:
    chapter = global_turn_to_chapter(global_turn)
    return get_chapter_config(chapter)["chapter_goal"]


def get_plot_directive(global_turn: int) -> str:
    return get_stage_config(global_turn)["plot_directive"]


def get_label(global_turn: int) -> str:
    return get_stage_config(global_turn)["label"]


def get_continent_for_turn(global_turn: int) -> str:
    chapter, stage, _ = chapter_stage_from_turn(global_turn)
    chapter_cfg = get_chapter_config(chapter)
    continents = chapter_cfg["continents"]
    if len(continents) == 1:
        return continents[0]
    if stage <= 3:
        return continents[0]
    return continents[1]


def is_final_stage(global_turn: int) -> bool:
    chapter, stage, _ = chapter_stage_from_turn(global_turn)
    return chapter == 3 and stage == 5


def is_chapter_boundary(global_turn: int) -> bool:
    _, stage, stage_turn = chapter_stage_from_turn(global_turn)
    return stage == 5 and stage_turn == 2


def total_turns() -> int:
    return len(CHAPTERS) * TURNS_PER_CHAPTER
