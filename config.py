from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Ember of Epochs"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    static_dir: str = "static"
    image_output_dir: str = "static/images/scenes"
    max_history: int = 100

    llm_provider: str = "openai"
    llm_model_name: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_api_base: str = ""
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_repetition_penalty: float = 1.15
    llm_frequency_penalty: float = 0.5
    llm_presence_penalty: float = 0.0

    bigpickle_model_path: str = "models/sdxl-turbo"
    bigpickle_device: str = "cuda"
    bigpickle_inference_steps: int = 4
    bigpickle_cfg_scale: float = 0.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
