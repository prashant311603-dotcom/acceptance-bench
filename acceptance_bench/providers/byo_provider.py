"""
BYO (Bring Your Own) provider for custom endpoints.
"""

import aiohttp
import json
from typing import Dict, Any, Optional
from .base_provider import BaseProvider


class BYOProvider(BaseProvider):
    """
    BYO (Bring Your Own) provider for custom model endpoints.
    
    This provider allows teams to benchmark their own models by
    providing a custom endpoint and API key. It follows the
    OpenAI-compatible chat completions API format.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model_id: str,
        **kwargs
    ):
        """
        Initialize BYO provider.
        
        Args:
            api_key: API key for your custom endpoint
            endpoint: Your custom endpoint URL
            model_id: Your model identifier
            **kwargs: Additional configuration
        """
        super().__init__(api_key, endpoint, model_id, **kwargs)

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
        Generate a response using custom endpoint.
        
        Expects an OpenAI-compatible chat completions API.
        
        Args:
            prompt: The user prompt
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing response data
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Add custom headers from config
        if "headers" in self.config:
            headers.update(self.config["headers"])

        messages = self._format_messages(prompt, system_prompt)

        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # Disable reasoning/thinking tokens for vLLM
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }

        if top_p is not None:
            payload["top_p"] = top_p

        # Add any additional kwargs to payload
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value

        async with aiohttp.ClientSession() as session:
            response, latency_ms = await self._measure_latency(
                self._make_request,
                session,
                headers,
                payload
            )

        # Extract content and metadata
        # Try OpenAI-compatible format first
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            # Fallback to direct content field
            content = response.get("content", str(response))
        
        # Extract token count if available
        token_count = None
        if "usage" in response:
            token_count = response["usage"].get("completion_tokens")

        return {
            "content": content,
            "raw_response": response,
            "latency_ms": latency_ms,
            "token_count": token_count,
        }

    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make the actual HTTP request.
        
        Args:
            session: aiohttp session
            headers: Request headers
            payload: Request payload
            
        Returns:
            Response JSON
        """
        async with session.post(
            self.endpoint,
            headers=headers,
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()

    def validate_endpoint(self) -> bool:
        """
        Validate custom endpoint accessibility.
        
        Returns:
            True if endpoint is accessible
        """
        import requests
        
        try:
            # Simple health check - try a minimal request
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                },
                timeout=30
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"BYO endpoint validation failed: {e}")
            return False

