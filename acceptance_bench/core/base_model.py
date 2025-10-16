from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ModelResponse:
    """Standardized model response format"""

    content: str
    model_name: str
    temperature: float
    top_p: Optional[float]
    raw_response: Dict[str, Any]
    latency_ms: float
    token_count: Optional[int]


class BaseModel(ABC):
    """Abstract base class for all models"""

    def __init__(self, name: str, endpoint: str, **kwargs):
        self.name = name
        self.endpoint = endpoint
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: Optional[float] = None,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate a response from the model"""
        pass

    @abstractmethod
    def validate_endpoint(self) -> bool:
        """Validate the endpoint is accessible"""
        pass
