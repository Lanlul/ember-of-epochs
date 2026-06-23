import pytest
from typing import Optional

from app.services.llm.provider import LLMProvider
from app.services.game_master import GameMaster

from .fixtures.llm_responses import RAW_JSON


class MockLLMProvider(LLMProvider):
    def __init__(self, response: Optional[str] = None):
        self.response = response or RAW_JSON
        self.call_count = 0
        self.last_messages = None

    async def generate(self, messages: list) -> str:
        self.call_count += 1
        self.last_messages = messages
        return self.response



class MockBigPicklePipeline:
    async def initialize(self):
        pass

    async def generate(self, **kwargs):
        return None


@pytest.fixture
def mock_llm():
    return MockLLMProvider()


@pytest.fixture
def mock_image():
    return MockBigPicklePipeline()


@pytest.fixture
def game_master(mock_llm, mock_image):
    return GameMaster(llm_provider=mock_llm, bigpickle_pipeline=mock_image)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
