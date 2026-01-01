"""OpenAI provider implementation."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.config import settings
from app.core.ai_exceptions import (
    AIProviderError,
    ContentFilterError,
    InvalidAPIKeyError,
    ModelNotFoundError,
    RateLimitError,
    TokenLimitExceededError,
)
from app.core.ai_provider import AIModelConfig, AIProvider, AIResponse, AIUsageMetrics

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI API provider implementation."""

    # Token pricing (per 1K tokens) - Updated for GPT-4
    MODEL_PRICING = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
        "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
    }

    def __init__(self):
        """Initialize OpenAI provider."""
        if not settings.openai_api_key:
            raise InvalidAPIKeyError("OpenAI API key not configured")

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout,
            max_retries=settings.openai_max_retries,
        )
        self.default_model = settings.openai_model
        self.default_temperature = settings.openai_temperature
        self.default_max_tokens = settings.openai_max_tokens

        # Usage tracking (in-memory for now, should be Redis/DB in production)
        self._usage_stats: dict[str, dict[str, Any]] = {}

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost for API call."""
        pricing = self.MODEL_PRICING.get(model, self.MODEL_PRICING["gpt-4"])
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        return prompt_cost + completion_cost

    def _track_usage(
        self,
        user_id: Optional[UUID],
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ) -> None:
        """Track API usage."""
        key = str(user_id) if user_id else "anonymous"

        if key not in self._usage_stats:
            self._usage_stats[key] = {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "by_model": {},
            }

        stats = self._usage_stats[key]
        stats["total_requests"] += 1
        stats["total_tokens"] += prompt_tokens + completion_tokens
        stats["total_cost"] += cost

        if model not in stats["by_model"]:
            stats["by_model"][model] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0,
            }

        model_stats = stats["by_model"][model]
        model_stats["requests"] += 1
        model_stats["tokens"] += prompt_tokens + completion_tokens
        model_stats["cost"] += cost

    async def _call_openai_api(
        self,
        messages: list[dict[str, str]],
        config: AIModelConfig,
        user_id: Optional[UUID] = None,
    ) -> ChatCompletion:
        """Call OpenAI Chat Completions API with retry logic."""
        retry_count = 0
        max_retries = settings.openai_max_retries

        while retry_count <= max_retries:
            try:
                response = await self.client.chat.completions.create(
                    model=config.model,
                    messages=messages,  # type: ignore
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                    frequency_penalty=config.frequency_penalty,
                    presence_penalty=config.presence_penalty,
                )
                return response

            except openai.RateLimitError as e:
                logger.warning(f"OpenAI rate limit hit: {e}")
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    retry_count += 1
                else:
                    raise RateLimitError(
                        "OpenAI rate limit exceeded, please try again later", retry_after=60
                    )

            except openai.AuthenticationError as e:
                logger.error(f"OpenAI authentication failed: {e}")
                raise InvalidAPIKeyError(f"Invalid OpenAI API key: {e}")

            except openai.NotFoundError as e:
                logger.error(f"OpenAI model not found: {e}")
                raise ModelNotFoundError(f"Model '{config.model}' not found")

            except openai.BadRequestError as e:
                logger.error(f"OpenAI bad request: {e}")
                if "maximum context length" in str(e).lower():
                    raise TokenLimitExceededError(
                        "Request exceeds token limit",
                        requested_tokens=0,  # Would need to count tokens
                        max_tokens=config.max_tokens or self.default_max_tokens,
                    )
                raise AIProviderError(f"Invalid request to OpenAI: {e}")

            except Exception as e:
                logger.error(f"Unexpected OpenAI error: {e}")
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    await asyncio.sleep(wait_time)
                    retry_count += 1
                else:
                    raise AIProviderError(f"OpenAI API error: {e}")

        raise AIProviderError("Max retries exceeded")

    def _create_ai_response(
        self, completion: ChatCompletion, user_id: Optional[UUID] = None
    ) -> AIResponse:
        """Convert OpenAI completion to AIResponse."""
        usage = completion.usage
        if not usage:
            raise AIProviderError("No usage data in OpenAI response")

        # Calculate cost
        cost = self._calculate_cost(
            completion.model, usage.prompt_tokens, usage.completion_tokens
        )

        # Track usage
        self._track_usage(
            user_id, completion.model, usage.prompt_tokens, usage.completion_tokens, cost
        )

        # Extract content
        choice = completion.choices[0]
        content = choice.message.content or ""

        return AIResponse(
            content=content,
            model=completion.model,
            usage=AIUsageMetrics(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=cost,
            ),
            finish_reason=choice.finish_reason,
            provider="openai",
        )

    async def generate_completion(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        config: Optional[AIModelConfig] = None,
        user_id: Optional[UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AIResponse:
        """Generate a completion from OpenAI."""
        # Use provided config or defaults
        if config is None:
            config = AIModelConfig(
                model=self.default_model,
                temperature=self.default_temperature,
                max_tokens=self.default_max_tokens,
            )

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Log request
        logger.info(
            f"OpenAI request - Model: {config.model}, User: {user_id}, "
            f"Prompt length: {len(prompt)}"
        )

        # Call API
        completion = await self._call_openai_api(messages, config, user_id)

        # Check for content filtering
        if completion.choices[0].finish_reason == "content_filter":
            raise ContentFilterError("Content was filtered by OpenAI's safety system")

        # Create response
        response = self._create_ai_response(completion, user_id)

        logger.info(
            f"OpenAI response - Tokens: {response.usage.total_tokens}, "
            f"Cost: ${response.usage.estimated_cost:.4f}"
        )

        return response

    async def tailor_resume(
        self,
        master_resume: dict[str, Any],
        job_description: str,
        *,
        prompt_template: str,
        company_name: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> AIResponse:
        """Tailor a resume for a specific job using OpenAI."""
        # Format the prompt with actual data
        prompt = prompt_template.format(
            master_resume=json.dumps(master_resume, indent=2),
            job_description=job_description,
            company_name=company_name or "the company",
        )

        # System prompt for resume tailoring
        system_prompt = (
            "You are an expert resume writer with 20+ years of experience "
            "helping candidates land jobs at top tech companies. Your expertise "
            "includes ATS optimization, executive positioning, and quantifiable "
            "impact storytelling. You never fabricate information and always "
            "maintain factual accuracy while maximizing relevance and impact."
        )

        # Use higher temperature for more creative tailoring
        config = AIModelConfig(
            model=self.default_model,
            temperature=0.7,
            max_tokens=4000,
        )

        return await self.generate_completion(
            prompt,
            system_prompt=system_prompt,
            config=config,
            user_id=user_id,
            metadata={"task": "resume_tailoring", "company": company_name},
        )

    async def generate_cover_letter(
        self,
        resume_summary: str,
        job_description: str,
        *,
        prompt_template: str,
        company_name: str,
        job_title: str,
        user_id: Optional[UUID] = None,
    ) -> AIResponse:
        """Generate a cover letter using OpenAI."""
        # Format the prompt
        prompt = prompt_template.format(
            resume_summary=resume_summary,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
        )

        # System prompt for cover letter generation
        system_prompt = (
            "You are an expert cover letter writer specializing in executive-level "
            "communication. You craft compelling, personalized cover letters that "
            "demonstrate genuine interest, strong fit, and unique value. Your letters "
            "are confident but not desperate, specific but not generic, and persuasive "
            "but authentic."
        )

        # Use slightly higher temperature for more engaging writing
        config = AIModelConfig(
            model=self.default_model,
            temperature=0.8,
            max_tokens=1500,
        )

        return await self.generate_completion(
            prompt,
            system_prompt=system_prompt,
            config=config,
            user_id=user_id,
            metadata={
                "task": "cover_letter_generation",
                "company": company_name,
                "job_title": job_title,
            },
        )

    async def classify_email(
        self,
        email_subject: str,
        email_body: str,
        *,
        user_id: Optional[UUID] = None,
    ) -> str:
        """Classify an email using OpenAI."""
        prompt = f"""Classify this email into ONE of these categories:
- confirmation: Application received/confirmed
- interview: Interview invitation or scheduling
- rejection: Application rejected
- offer: Job offer received
- other: None of the above

Email Subject: {email_subject}
Email Body: {email_body[:1000]}

Respond with ONLY the category name, nothing else."""

        # Use lower temperature for classification
        config = AIModelConfig(
            model="gpt-3.5-turbo",  # Cheaper model for simple classification
            temperature=0.0,
            max_tokens=10,
        )

        response = await self.generate_completion(
            prompt, config=config, user_id=user_id, metadata={"task": "email_classification"}
        )

        # Extract and validate classification
        classification = response.content.strip().lower()
        valid_categories = {"confirmation", "interview", "rejection", "offer", "other"}

        if classification not in valid_categories:
            logger.warning(f"Invalid classification '{classification}', defaulting to 'other'")
            return "other"

        return classification

    async def get_usage_stats(self, user_id: Optional[UUID] = None) -> dict[str, Any]:
        """Get usage statistics."""
        if user_id:
            key = str(user_id)
            return self._usage_stats.get(key, {})

        # Return aggregate stats
        total_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "users": len(self._usage_stats),
        }

        for stats in self._usage_stats.values():
            total_stats["total_requests"] += stats.get("total_requests", 0)
            total_stats["total_tokens"] += stats.get("total_tokens", 0)
            total_stats["total_cost"] += stats.get("total_cost", 0.0)

        return total_stats
