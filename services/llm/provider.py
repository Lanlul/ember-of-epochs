import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict

from ...config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self):
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key or None,
            base_url=settings.llm_api_base or None,
        )
        self._model = settings.llm_model_name

    async def generate(self, messages: List[Dict[str, str]]) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            frequency_penalty=settings.llm_frequency_penalty,
            presence_penalty=settings.llm_presence_penalty,
            messages=messages,
        )
        return resp.choices[0].message.content or ""

class LocalProvider(LLMProvider):
    def __init__(self):
        self._model_name = settings.llm_model_name
        self._llm = None

    def _load(self):
        if self._llm is not None:
            return
        try:
            import llama_cpp

            n_gpu = -1 if llama_cpp.llama_supports_gpu_offload() else 0
            self._llm = llama_cpp.Llama(
                model_path=self._model_name,
                n_ctx=32768,
                n_gpu_layers=n_gpu,
                verbose=False,
            )
            logger.info(
                "Local model loaded: %s (GPU layers: %s)",
                self._model_name, n_gpu,
            )
        except ImportError:
            raise RuntimeError(
                "llama-cpp-python is not installed. "
                "Run: pip install llama-cpp-python"
            )

    async def generate(self, messages: List[Dict[str, str]]) -> str:
        self._load()
        loop = asyncio.get_running_loop()

        def _run():
            output = self._llm.create_chat_completion(
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                repeat_penalty=settings.llm_repetition_penalty,
            )
            return output["choices"][0]["message"]["content"]

        return await loop.run_in_executor(None, _run)

def create_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider()
    elif settings.llm_provider == "local":
        return LocalProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
