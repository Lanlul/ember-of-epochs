from typing import Optional, Dict, Any


CONTINENT_STYLE_MAP = {
    "克洛諾斯廢土": "ruins_gothic",
    "渥爾肯機械之心": "steampunk",
    "翡翠密境": "biomagical",
    "永凍星環": "frost_epic",
    "虛空迴廊": "surreal",
}

LORA_WEIGHT_MAP = {
    "ruins_gothic": 0.75,
    "steampunk": 0.8,
    "biomagical": 0.7,
    "frost_epic": 0.85,
    "surreal": 0.9,
}


class StyleController:
    def resolve_style(self, continent: str) -> str:
        return CONTINENT_STYLE_MAP.get(continent, "ruins_gothic")

    def get_lora_config(self, style: str) -> Optional[Dict[str, Any]]:
        weight = LORA_WEIGHT_MAP.get(style)
        if weight is None:
            return None
        return {
            "lora_path": f"lora/{style}.safetensors",
            "weight": weight,
        }
