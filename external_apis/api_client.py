"""
External AI API clients for production inference.
Supports multiple providers: OpenAI, Anthropic, Cohere, etc.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
import json

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Response from external API."""
    provider: str
    model: str
    content: str
    tokens_used: int
    latency_ms: float
    success: bool
    error: Optional[str] = None


class BaseAPIClient:
    """Base class for API clients."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = httpx.Client(timeout=120.0)
    
    async def generate(self, prompt: str, max_tokens: int = 1000, **kwargs) -> APIResponse:
        """Generate text from prompt."""
        raise NotImplementedError
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


class OpenAIClient(BaseAPIClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        super().__init__(api_key, model)
        self.base_url = "https://api.openai.com/v1"
    
    async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> APIResponse:
        import time
        start_time = time.time()
        
        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            latency_ms = (time.time() - start_time) * 1000
            
            return APIResponse(
                provider="openai",
                model=self.model,
                content=content,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                success=True
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return APIResponse(
                provider="openai",
                model=self.model,
                content="",
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )


class AnthropicClient(BaseAPIClient):
    """Anthropic API client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        super().__init__(api_key, model)
        self.base_url = "https://api.anthropic.com/v1"
    
    async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> APIResponse:
        import time
        start_time = time.time()
        
        try:
            response = self.client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["content"][0]["text"]
            tokens_used = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            latency_ms = (time.time() - start_time) * 1000
            
            return APIResponse(
                provider="anthropic",
                model=self.model,
                content=content,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                success=True
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return APIResponse(
                provider="anthropic",
                model=self.model,
                content="",
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )


class CohereClient(BaseAPIClient):
    """Cohere API client."""
    
    def __init__(self, api_key: str, model: str = "command"):
        super().__init__(api_key, model)
        self.base_url = "https://api.cohere.ai/v1"
    
    async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> APIResponse:
        import time
        start_time = time.time()
        
        try:
            response = self.client.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["generations"][0]["text"]
            tokens_used = data.get("meta", {}).get("billed_units", {}).get("output_tokens", 0)
            latency_ms = (time.time() - start_time) * 1000
            
            return APIResponse(
                provider="cohere",
                model=self.model,
                content=content,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                success=True
            )
        except Exception as e:
            logger.error(f"Cohere API error: {e}")
            return APIResponse(
                provider="cohere",
                model=self.model,
                content="",
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )


class APIClientFactory:
    """Factory for creating API clients."""
    
    @staticmethod
    def create_client(provider: str, api_key: str, model: str) -> BaseAPIClient:
        """Create an API client for the given provider."""
        clients = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "cohere": CohereClient,
        }
        
        client_class = clients.get(provider.lower())
        if not client_class:
            raise ValueError(f"Unknown provider: {provider}")
        
        return client_class(api_key, model)


class MultiAPIClient:
    """Manages multiple API clients for load balancing and comparison."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize multiple API clients.
        
        Args:
            config: Dictionary of provider configurations
                {
                    "openai": {"api_key": "...", "model": "gpt-4-turbo"},
                    "anthropic": {"api_key": "...", "model": "claude-3-opus-20240229"},
                    ...
                }
        """
        self.clients = {}
        self.config = config
        
        for provider, provider_config in config.items():
            if provider_config.get("api_key"):
                try:
                    client = APIClientFactory.create_client(
                        provider,
                        provider_config["api_key"],
                        provider_config.get("model", "default")
                    )
                    self.clients[provider] = client
                    logger.info(f"Initialized {provider} client with model {provider_config.get('model')}")
                except Exception as e:
                    logger.error(f"Failed to initialize {provider} client: {e}")
    
    async def generate_all(self, prompt: str, max_tokens: int = 1000, **kwargs) -> List[APIResponse]:
        """
        Generate text using all available clients in parallel.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            List of APIResponse objects
        """
        import asyncio
        
        tasks = [
            client.generate(prompt, max_tokens, **kwargs)
            for client in self.clients.values()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider = list(self.clients.keys())[i]
                logger.error(f"Error from {provider}: {result}")
                responses.append(APIResponse(
                    provider=provider,
                    model="unknown",
                    content="",
                    tokens_used=0,
                    latency_ms=0,
                    success=False,
                    error=str(result)
                ))
            else:
                responses.append(result)
        
        return responses
    
    async def generate(self, provider: str, prompt: str, max_tokens: int = 1000, **kwargs) -> APIResponse:
        """
        Generate text using a specific provider.
        
        Args:
            provider: Provider name
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            APIResponse object
        """
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} not available")
        
        return await self.clients[provider].generate(prompt, max_tokens, **kwargs)
    
    def close_all(self):
        """Close all HTTP clients."""
        for client in self.clients.values():
            client.close()
