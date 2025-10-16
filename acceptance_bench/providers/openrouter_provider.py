"""
OpenRouter API provider implementation.
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional
from .base_provider import BaseProvider


class OpenRouterProvider(BaseProvider):
    """
    Provider for OpenRouter API.
    
    OpenRouter provides unified access to multiple LLM providers
    through a single API interface.
    """

    def __init__(
        self,
        api_key: str,
        model_id: str,
        endpoint: str = "https://openrouter.ai/api/v1/chat/completions",
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key
            model_id: Model identifier (e.g., "openai/gpt-4-turbo")
            endpoint: API endpoint (default: OpenRouter standard endpoint)
            site_url: Your site URL for rankings (optional)
            site_name: Your site name for rankings (optional)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, endpoint, model_id, **kwargs)
        self.site_url = site_url or kwargs.get("site_url", "https://github.com/ellydee")
        self.site_name = site_name or kwargs.get("site_name", "acceptance-bench")

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
        Generate a response using OpenRouter API.
        
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
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
        }

        messages = self._format_messages(prompt, system_prompt)

        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Only add reasoning parameter for models that support it
        # Some models don't support this and will 404
        # Uncomment if needed:
        payload["reasoning"] = {"effort": "low", "exclude": True}
        
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
        content = response["choices"][0]["message"]["content"]
        
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
        payload: Dict[str, Any],
        max_retries: int = 5
    ) -> Dict[str, Any]:
        """
        Make the actual HTTP request with exponential backoff retry logic.
        
        Args:
            session: aiohttp session
            headers: Request headers
            payload: Request payload
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response JSON
        """
        for attempt in range(max_retries):
            try:
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 429:
                        # Rate limited - exponential backoff
                        wait_time = (2 ** attempt) * 1.0  # 1s, 2s, 4s, 8s, 16s
                        print(f"    ⚠️  Rate limited (429), waiting {wait_time:.0f}s before retry {attempt + 1}/{max_retries}...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) * 1.0
                print(f"    ⚠️  Request failed: {e}, retrying in {wait_time:.0f}s...")
                await asyncio.sleep(wait_time)
        
        raise Exception(f"Failed after {max_retries} attempts")

    def validate_endpoint(self) -> bool:
        """
        Validate OpenRouter endpoint accessibility.
        
        Returns:
            True if endpoint is accessible
        """
        import requests
        
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"OpenRouter endpoint validation failed: {e}")
            print(f"HTTP {response.status_code} - {response.text[:200]}...")
            return False

