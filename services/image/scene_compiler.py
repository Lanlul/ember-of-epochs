from typing import Optional

from ...models.world import SceneTags

CONTINENT_PROMPTS = {
    "克洛諾斯廢土": "ancient ruined wasteland with broken stone platforms and time-worn relics, apocalyptic sky with rift, dark atmospheric ruins",
    "渥爾肯機械之心": "vast mechanical steampunk city with gears and steam, brass and iron architecture, industrial revolution core",
    "翡翠密境": "jade-green mystical forest with glowing flora, ancient trees, ethereal mist, hidden stone temples",
    "永凍星環": "frozen tundra under aurora sky, ice crystals, snow-capped peaks, eternal winter landscape",
    "虛空迴廊": "impossible floating geometry in cosmic void, dimensional rifts, swirling nebulae, surreal space",
}

STYLE_PROMPTS = {
    "ruins_gothic": "gothic ruins, dramatic shadows, ornate stone carvings",
    "steampunk": "steampunk, brass machinery, intricate gears, victorian industrial",
    "biomagical": "bioluminescent fantasy, glowing plants, mystical nature, ethereal",
    "frost_epic": "epic frozen landscape, northern lights, ice magic, crystalline",
    "surreal": "surreal dreamscape, impossible architecture, cosmic otherworldly",
}

COLOR_MAP = {
    "深藍": "deep blue", "銀白": "silver white", "灰色": "grey",
    "金色": "golden", "暗紅": "dark red", "翠綠": "emerald green",
    "紫": "purple", "黑": "black", "白": "white", "藍": "blue",
    "紅": "red", "綠": "green", "黃": "yellow", "橙": "orange",
    "極光綠": "aurora green", "虛空黑": "void black",
    "赤紅": "crimson", "蒼白": "pale", "青": "cyan",
    "灰石": "stone grey", "古銅": "bronze",
    "琥珀": "amber", "墨綠": "dark green",
    "銅褐": "copper brown", "鐵灰": "iron grey",
    "火焰橙": "flame orange", "黑曜": "obsidian",
    "藤紫": "vine purple", "翡翠綠": "jade green",
    "螢光藍": "fluorescent blue", "冰藍": "ice blue",
    "雪白": "snow white", "霓虹紫": "neon purple",
    "電光藍": "electric blue", "鏽蝕橙": "rust orange",
    "金屬銀": "metallic silver", "大地棕": "earth brown",
    "天空藍": "sky blue", "夕陽金": "sunset gold",
    "星塵銀": "stardust silver", "深淵紫": "abyss purple",
    "紅棕": "reddish brown", "暗紫": "dark purple",
    "銀灰": "silver grey", "暗金": "dark gold",
    "灰白": "grey white", "橙黃": "orange yellow",
    "深黑": "deep black", "石頭": "stone",
    "夕陽": "sunset", "濃霧": "dense fog",
}

MOOD_MAP = {
    "神秘": "mysterious", "莊嚴": "solemn", "寧靜": "serene",
    "緊張": "tense", "詭異": "eerie", "雄偉": "majestic",
    "荒涼": "desolate", "希望": "hopeful", "絕望": "despairing",
    "沉思": "contemplative", "好奇": "curious", "寂靜": "silent",
    "神聖": "sacred", "壓抑": "oppressive", "悠遠": "timeless",
    "肅穆": "solemn", "溫馨": "warm", "陰森": "gloomy",
    "詭譎": "uncanny", "壯闊": "grand",
}

LIGHTING_MAP = {
    "微弱": "dim", "昏暗": "dim", "明亮": "bright",
    "光芒": "glowing light", "發光": "glowing",
    "藍光": "blue glow", "金光": "golden glow",
    "紅光": "red light", "白光": "white light",
    "暮光": "twilight", "月光": "moonlight",
    "陽光": "sunlight", "燭光": "candlelight",
    "火光": "firelight", "螢光": "bioluminescent glow",
    "極光": "aurora", "星光": "starlight",
}

NEGATIVE_PROMPT = (
    "low quality, worst quality, blurry, distorted, deformed, "
    "bad anatomy, watermark, text, signature, extra limbs, "
    "ugly, sketch, cartoon, 3d render, monochrome, bad proportions, "
    "letters, words, text"
)

FOCUS_MAP = {
    "紀元行者": "a lone traveler in cloak",
    "player_character": "the protagonist in hooded cloak",
    "traveler": "a lone traveler",
    "時光裝置": "ancient time device",
    "碑文": "glowing runic stele",
    "石台": "stone altar",
    "廢墟": "ruins",
    "殘骸": "ancient relics",
    "祭壇": "ritual altar",
    "熔爐": "giant furnace",
    "齒輪": "huge gears",
    "水晶": "glowing crystals",
    "傳送門": "glowing portal",
    "橋": "stone bridge",
    "高塔": "tower",
    "塔": "tower",
    "門": "doorway",
    "窗": "arched window",
    "階梯": "stone staircase",
    "massive_clockwork_city": "massive clockwork city",
    "living_tree_city": "living tree city",
    "evolving_mechanical_organism": "evolving mechanical organism",
    "primitive_wilderness": "primitive wilderness",
    "floating_continents_in_orbit": "floating continents in orbit",
    "ancient_machine": "ancient machine",
    "mysterious_artifact": "mysterious artifact",
}


def _translate_color(cn: str) -> str:
    if cn in COLOR_MAP:
        return COLOR_MAP[cn]
    parts = [COLOR_MAP.get(w, w) for w in cn.replace("的", " ").split()]
    return " ".join(parts) if parts else cn


def _translate_mood(cn: str) -> str:
    parts = [v for k, v in MOOD_MAP.items() if k in cn]
    return ", ".join(parts) if parts else "atmospheric"


def _translate_lighting(cn: str) -> str:
    for k, v in LIGHTING_MAP.items():
        if k in cn:
            return v
    return cn


def _translate_focus(cn: str) -> str:
    for k, v in FOCUS_MAP.items():
        if k in cn:
            return v
    return cn


class SceneCompiler:
    def compile(
        self,
        scene_tags: SceneTags,
        style_override: Optional[str] = None,
        continent: str = "克洛諾斯廢土",
    ) -> dict:
        style = style_override or scene_tags.style
        continent_prompt = CONTINENT_PROMPTS.get(continent, CONTINENT_PROMPTS["克洛諾斯廢土"])
        style_prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["ruins_gothic"])

        mood_en = _translate_mood(scene_tags.mood)
        lighting_en = _translate_lighting(scene_tags.lighting)
        focus_en = _translate_focus(scene_tags.focus)
        color_en = ", ".join(_translate_color(c) for c in scene_tags.color_palette) if scene_tags.color_palette else ""

        scene_parts = []

        if scene_tags.setting:
            setting_en = _translate_setting_to_english(scene_tags.setting)
            if setting_en:
                scene_parts.append(setting_en)
            else:
                for kw, en in FOCUS_MAP.items():
                    if kw in scene_tags.setting and kw not in ("player_character", "紀元行者"):
                        scene_parts.append(en)
                        break

        if focus_en:
            scene_parts.append(focus_en)

        if scene_tags.character_state:
            state_en = _translate_character_state(scene_tags.character_state)
            if state_en:
                scene_parts.append(state_en)

        if mood_en:
            scene_parts.append(f"{mood_en} atmosphere")

        if lighting_en:
            scene_parts.append(f"{lighting_en} lighting")

        if color_en:
            scene_parts.append(f"color scheme {color_en}")

        scene_parts.append(style_prompt)
        scene_parts.append(continent_prompt)
        scene_parts.append("cinematic epic, intricate detail, digital painting, fantasy art")

        prompt = ", ".join(scene_parts)

        return {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "style": style,
        }


_SETTING_MAP = {
    "克洛諾斯高塔": "ancient chronos tower", "機械之心": "mechanical heart",
    "翡翠密境": "jade forest", "永凍星環": "frozen ring",
    "虛空迴廊": "void corridor", "時光裝置": "ancient time device",
    "廢土": "barren wasteland", "遺跡": "ancient ruins",
    "建築": "ancient architecture", "森林": "forest",
    "洞穴": "dark cave", "河流": "river",
    "山": "mountain", "峽谷": "canyon",
    "平台": "stone platform", "大廳": "great hall",
    "房間": "chamber", "高塔": "tower",
    "塔": "tower", "城": "fortress",
    "花園": "garden", "宮殿": "palace",
    "工廠": "factory", "圖書館": "library",
    "實驗室": "laboratory", "通道": "passageway",
    "橋": "bridge", "祭壇": "altar",
    "墓": "tomb", "神殿": "temple",
    "市集": "marketplace", "廣場": "plaza",
    "碼頭": "dock", "船": "ship",
    "飛船": "airship", "穹頂": "dome",
    "裂縫": "rift", "廢墟": "ruins",
    "濃霧": "dense fog", "迷霧": "misty",
    "石碑": "stone stele",
}


def _translate_setting_to_english(cn: str) -> str:
    best = ""
    best_len = 0
    for kw, en in _SETTING_MAP.items():
        if kw in cn and len(kw) > best_len:
            best = en
            best_len = len(kw)
    return best


_STATE_PARTS = {
    "迷茫": "bewildered", "好奇": "curious", "沉靜": "calm",
    "警戒": "alert", "恐懼": "fearful", "堅定": "determined",
    "疲憊": "weary", "興奮": "excited", "平靜": "serene",
    "嚴肅": "serious", "專注": "focused",
}


def _translate_character_state(cn: str) -> str:
    parts = [en for kw, en in _STATE_PARTS.items() if kw in cn]
    return ", ".join(parts) if parts else ""
