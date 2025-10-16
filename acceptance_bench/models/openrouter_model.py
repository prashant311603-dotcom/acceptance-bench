"""
Generic OpenRouter model implementation.

This single class works for ALL OpenRouter models.
No need to create separate files for each model!
"""

import os
from typing import Optional
from acceptance_bench.core.base_model import BaseModel, ModelResponse
from acceptance_bench.providers import OpenRouterProvider


class OpenRouterModel(BaseModel):
    """
    Generic OpenRouter model that works for any model on OpenRouter.
    
    The model_id is the ONLY thing that differs between models,
    so we parameterize it instead of creating separate classes.
    
    Configuration from models.yaml:
    - model_id: The OpenRouter model identifier (e.g., "x-ai/grok-4")
    - api_key_env: Environment variable name (default: OPENROUTER_API_KEY)
    - site_url: Optional site URL for rankings
    - site_name: Optional site name for rankings
    """

    def __init__(
        self,
        name: str,
        model_id: str,
        api_key: Optional[str] = None,
        api_key_env: str = "OPENROUTER_API_KEY",
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenRouter model.
        
        Args:
            name: Model name for identification (e.g., "grok-4")
            model_id: OpenRouter model ID (e.g., "x-ai/grok-4")
            api_key: OpenRouter API key (or None to use env var)
            api_key_env: Name of env var containing API key
            site_url: Your site URL for OpenRouter rankings
            site_name: Your site name for OpenRouter rankings
            **kwargs: Additional configuration
        """
        # Get API key from argument or environment
        api_key = api_key or os.getenv(api_key_env)

        if not api_key:
            raise ValueError(
                f"{api_key_env} must be set or api_key must be provided"
            )

        endpoint = kwargs.pop("endpoint", "https://openrouter.ai/api/v1/chat/completions")

        super().__init__(name=name, endpoint=endpoint)

        # Initialize OpenRouter provider
        self.provider = OpenRouterProvider(
            api_key=api_key,
            model_id=model_id,
            endpoint=endpoint,
            site_url=site_url,
            site_name=site_name,
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
        Generate a response from the OpenRouter model.
        
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
        Validate the OpenRouter endpoint.
        
        Returns:
            True if endpoint is accessible
        """
        return self.provider.validate_endpoint()

