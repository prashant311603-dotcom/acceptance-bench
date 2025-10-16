"""
Brightside model implementation using BYO provider (vLLM).

This model uses a custom endpoint and API key defined in the .env file.
"""

import os
from typing import Optional
from acceptance_bench.core.base_model import BaseModel, ModelResponse
from acceptance_bench.providers import BYOProvider


class Brightside(BaseModel):
    """
    Brightside model using custom vLLM endpoint (BYO provider).
    
    Configuration should be provided via environment variables:
    - BRIGHTSIDE_API_KEY: API key for authentication
    - BRIGHTSIDE_ENDPOINT: Model endpoint URL
    - BRIGHTSIDE_MODEL_ID: Model identifier (default: brightside-v3)
    """

    def __init__(
        self,
        name: str = "brightside-v3",
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Brightside model.
        
        Args:
            name: Model name for identification
            api_key: API key (falls back to BRIGHTSIDE_API_KEY env var)
            endpoint: Endpoint URL (falls back to BRIGHTSIDE_ENDPOINT env var)
            model_id: Model ID (falls back to BRIGHTSIDE_MODEL_ID env var or "brightside-v3")
            **kwargs: Additional configuration
        """
        # Get configuration from environment or arguments
        api_key = api_key or os.getenv("BRIGHTSIDE_API_KEY")
        endpoint = endpoint or os.getenv("BRIGHTSIDE_ENDPOINT")
        model_id = model_id or os.getenv("BRIGHTSIDE_MODEL_ID", "brightside-v3")

        if not api_key:
            raise ValueError(
                "BRIGHTSIDE_API_KEY must be provided via argument or environment variable"
            )
        if not endpoint:
            raise ValueError(
                "BRIGHTSIDE_ENDPOINT must be provided via argument or environment variable"
            )

        super().__init__(name=name, endpoint=endpoint, **kwargs)

        # Initialize BYO provider
        self.provider = BYOProvider(
            api_key=api_key,
            endpoint=endpoint,
            model_id=model_id,
            **kwargs
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: Optional[float] = None,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a response from Brightside.
        
        Args:
            prompt: The user prompt
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            ModelResponse with generated content
        """
        result = await self.provider.generate(
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs
        )

        return ModelResponse(
            content=result["content"],
            model_name=self.name,
            temperature=temperature,
            top_p=top_p,
            raw_response=result["raw_response"],
            latency_ms=result["latency_ms"],
            token_count=result["token_count"],
        )

    def validate_endpoint(self) -> bool:
        """
        Validate the Brightside endpoint.
        
        Returns:
            True if endpoint is accessible
        """
        return self.provider.validate_endpoint()
