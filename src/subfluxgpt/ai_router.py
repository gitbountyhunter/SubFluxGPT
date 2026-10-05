"""
Multi-API LLM Router for SubFluxGPT
Supports: Gemini, Claude, OpenAI, Grok, DeepSeek
"""

import os
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    tokens_used: int
    success: bool
    error: Optional[str] = None


class LLMRouter:
    """Router for multiple LLM APIs with fallback support"""

    def __init__(self, primary_api: str = "gemini", fallback_apis: Optional[List[str]] = None):
        """
        Initialize the LLM router
        
        Args:
            primary_api: Primary API to use (gemini, claude, openai, grok, deepseek)
            fallback_apis: List of fallback APIs in order
        """
        self.primary_api = primary_api.lower()
        self.fallback_apis = fallback_apis or []
        self.api_chain = [self.primary_api] + self.fallback_apis
        
        # Load API keys from environment
        self.api_keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),
            "claude": os.getenv("CLAUDE_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "grok": os.getenv("GROK_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        }
        
        # Validate primary API key
        if not self.api_keys.get(self.primary_api):
            raise ValueError(f"API key for {self.primary_api} not found in environment variables")

    async def generate_subdomains(
        self,
        known_subdomains: List[str],
        count: int = 50,
        domain: str = ""
    ) -> LLMResponse:
        """
        Generate new subdomains using AI
        
        Args:
            known_subdomains: List of known subdomains
            count: Number of subdomains to generate
            domain: Target domain (for context)
            
        Returns:
            LLMResponse with generated subdomains
        """
        prompt = self._build_prompt(known_subdomains, count, domain)
        
        # Try each API in the chain
        for api_name in self.api_chain:
            if not self.api_keys.get(api_name):
                continue
                
            try:
                response = await self._call_api(api_name, prompt)
                if response.success:
                    return response
            except Exception as e:
                print(f"[!] {api_name} API failed: {str(e)}", file=__import__("sys").stderr)
                continue
        
        return LLMResponse(
            content="",
            model="none",
            tokens_used=0,
            success=False,
            error="All APIs failed"
        )

    def _build_prompt(self, known_subdomains: List[str], count: int, domain: str) -> str:
        """Build optimized prompt for subdomain generation"""
        # Token-efficient prompt
        subs_text = "\n".join(known_subdomains[:50])  # Limit to 50 for context
        
        prompt = f"""You are a subdomain enumeration expert. Analyze these existing subdomains for {domain} and predict {count} MORE subdomains that likely exist.

Existing subdomains:
{subs_text}

Rules:
1. Focus on common patterns: staging, dev, test, prod, admin, api, auth, etc.
2. Consider naming conventions from the existing subs
3. Include environment-specific subdomains
4. Include service-specific subdomains (db, cache, queue, etc.)
5. Return ONLY subdomain names, one per line
6. Do NOT include the domain suffix
7. No explanations, no numbering

Output format:
subdomain1
subdomain2
subdomain3
..."""
        return prompt

    async def _call_api(self, api_name: str, prompt: str) -> LLMResponse:
        """Call specific API based on name"""
        api_handlers = {
            "gemini": self._call_gemini,
            "claude": self._call_claude,
            "openai": self._call_openai,
            "grok": self._call_grok,
            "deepseek": self._call_deepseek,
        }
        
        handler = api_handlers.get(api_name)
        if not handler:
            raise ValueError(f"Unsupported API: {api_name}")
        
        return await handler(prompt)

    async def _call_gemini(self, prompt: str) -> LLMResponse:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_keys["gemini"])
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            response = model.generate_content(prompt)
            
            return LLMResponse(
                content=response.text,
                model="gemini-1.5-pro",
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                success=True
            )
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def _call_claude(self, prompt: str) -> LLMResponse:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_keys["claude"])
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                success=True
            )
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    async def _call_openai(self, prompt: str) -> LLMResponse:
        """Call OpenAI GPT API"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_keys["openai"])
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                success=True
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _call_grok(self, prompt: str) -> LLMResponse:
        """Call xAI Grok API"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=self.api_keys["grok"],
                base_url="https://api.x.ai/v1"
            )
            
            response = await client.chat.completions.create(
                model="grok-beta",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                success=True
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"Grok API error: {str(e)}")

    async def _call_deepseek(self, prompt: str) -> LLMResponse:
        """Call DeepSeek API"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=self.api_keys["deepseek"],
                base_url="https://api.deepseek.com"
            )
            
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                success=True
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")

    def parse_subdomains(self, response: str) -> List[str]:
        """Parse subdomains from LLM response"""
        subdomains = []
        for line in response.strip().split('\n'):
            line = line.strip()
            # Remove numbering, bullets, and other prefixes
            line = line.lstrip('0123456789.-* ')
            # Basic validation
            if line and ' ' not in line and len(line) <= 250:
                subdomains.append(line)
        return subdomains
