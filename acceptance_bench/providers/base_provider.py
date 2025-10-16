"""
Base provider interface for LLM API providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time


class BaseProvider(ABC):
    """
    Abstract base class for all LLM API providers.
    
    This provides a common interface for different API providers
    (OpenRouter, custom endpoints, etc.) to ensure consistency
    across the benchmarking framework.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model_id: str,
        **kwargs
    ):
        """
        Initialize the provider.
        
        Args:
            api_key: API key for authentication
            endpoint: API endpoint URL
            model_id: Model identifier (e.g., "openai/gpt-4")
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.model_id = model_id
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
    ) -> Dict[str, Any]:
        """
        Generate a response from the model.
        
        Args:
            prompt: The user prompt
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing:
                - content: Generated text
                - raw_response: Raw API response
                - latency_ms: Generation latency in milliseconds
                - token_count: Number of tokens (if available)
        """
        pass

    @abstractmethod
    def validate_endpoint(self) -> bool:
        """
        Validate that the endpoint is accessible.
        
        Returns:
            True if endpoint is valid and accessible
        """
        pass

    def _format_messages(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> list:
        """
        Format messages for chat completion APIs.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            List of message dictionaries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def _measure_latency(self, func, *args, **kwargs):
        """
        Measure latency of an async function call.
        
        Args:
            func: Async function to measure
            *args, **kwargs: Function arguments
            
        Returns:
            Tuple of (result, latency_ms)
        """
        start_time = time.time()
        result = await func(*args, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        return result, latency_ms

