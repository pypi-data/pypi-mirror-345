from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable

from kirara_ai.config.global_config import ModelConfig
from kirara_ai.llm.format.request import LLMChatRequest
from kirara_ai.llm.format.response import LLMChatResponse
from kirara_ai.media.manager import MediaManager
from kirara_ai.tracing.llm_tracer import LLMTracer


@runtime_checkable
class AutoDetectModelsProtocol(Protocol):
    async def auto_detect_models(self) -> List[ModelConfig]: ...


class LLMBackendAdapter(ABC):
    backend_name: str
    media_manager: MediaManager
    tracer: LLMTracer
    
    @abstractmethod
    def chat(self, req: LLMChatRequest) -> LLMChatResponse:
        raise NotImplementedError("Unsupported model method")
