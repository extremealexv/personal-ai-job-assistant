"""Google Gemini provider implementation."""
import asyncio
import json
import logging
from typing import Any, Optional
from uuid import UUID

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmBlockThreshold, HarmCategory

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
from app.services.cost_tracking_service import cost_tracking_service
from app.services.rate_limit_service import rate_limit_service

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Google Gemini API provider implementation."""

    # Token pricing (per 1M tokens) - Gemini Pro is FREE up to 60 RPM
    MODEL_PRICING = {
        "gemini-pro": {"prompt": 0.0, "completion": 0.0},  # Free tier
        "gemini-1.5-pro": {"prompt": 0.00125, "completion": 0.005},
        "gemini-1.5-flash": {"prompt": 0.000075, "completion": 0.0003},
    }

    def __init__(self):
        """Initialize Gemini provider."""
        if not settings.gemini_api_key:
            raise InvalidAPIKeyError("Gemini API key not configured")

        genai.configure(api_key=settings.gemini_api_key)
        
        self.default_model = settings.gemini_model
        self.default_temperature = settings.gemini_temperature
        self.default_max_tokens = settings.gemini_max_tokens

        # Usage tracking (in-memory for now)
        self._usage_stats: dict[str, dict[str, Any]] = {}

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost for API call."""
        pricing = self.MODEL_PRICING.get(model, self.MODEL_PRICING["gemini-pro"])
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
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

    def _create_generation_config(self, config: AIModelConfig) -> GenerationConfig:
        """Create Gemini generation config from AIModelConfig."""
        return GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
            top_p=config.top_p,
        )

    def _create_ai_response(
        self, response: Any, model: str, user_id: Optional[UUID]
    ) -> AIResponse:
        """Convert Gemini response to AIResponse."""
        # Extract text from response
        content = response.text

        # Get usage metadata (Gemini provides token counts)
        prompt_tokens = response.usage_metadata.prompt_token_count
        completion_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count

        # Calculate cost
        estimated_cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

        # Track usage
        self._track_usage(user_id, model, prompt_tokens, completion_tokens, estimated_cost)

        # Get finish reason
        finish_reason = "stop"
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "finish_reason"):
                finish_reason = str(candidate.finish_reason)

        return AIResponse(
            content=content,
            model=model,
            usage=AIUsageMetrics(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
            ),
            finish_reason=finish_reason,
            provider="gemini",
        )

    async def _call_gemini_api(
        self, prompt: str, config: AIModelConfig, user_id: Optional[UUID] = None
    ) -> Any:
        """Call Gemini API with retry logic."""
        retry_count = 0
        max_retries = settings.gemini_max_retries

        generation_config = self._create_generation_config(config)
        
        # Safety settings - allow all content for resume/job description processing
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        while retry_count <= max_retries:
            try:
                model = genai.GenerativeModel(
                    model_name=config.model,
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                )

                # Generate content asynchronously
                response = await asyncio.to_thread(
                    model.generate_content, prompt
                )

                # Check for content filtering
                if response.prompt_feedback.block_reason:
                    raise ContentFilterError(
                        f"Content was blocked: {response.prompt_feedback.block_reason}"
                    )

                return response

            except Exception as e:
                error_msg = str(e).lower()
                
                # Log full error for debugging
                logger.error(f"Gemini API error (attempt {retry_count + 1}/{max_retries}): {type(e).__name__}: {e}")

                # Handle specific errors
                if "quota" in error_msg or "rate" in error_msg or "429" in error_msg or "resource_exhausted" in error_msg:
                    if retry_count < max_retries:
                        wait_time = 2**retry_count
                        logger.warning(
                            f"Gemini rate limit hit, retrying in {wait_time}s (attempt {retry_count + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                        continue
                    logger.error(f"Gemini rate limit exceeded after {max_retries} retries. Full error: {e}")
                    raise RateLimitError(f"Gemini API rate limit exceeded: {e}")

                elif "invalid" in error_msg and ("key" in error_msg or "api_key" in error_msg or "api key" in error_msg):
                    raise InvalidAPIKeyError(f"Invalid Gemini API key: {e}")

                elif "not found" in error_msg or ("model" in error_msg and "not" in error_msg):
                    raise ModelNotFoundError(f"Model '{config.model}' not found: {e}")

                elif "token" in error_msg and "limit" in error_msg:
                    raise TokenLimitExceededError(f"Token limit exceeded: {e}")

                else:
                    logger.error(f"Unhandled Gemini API error: {type(e).__name__}: {e}")
                    raise AIProviderError(f"Gemini API call failed: {e}")

        raise AIProviderError("Max retries exceeded")

    async def generate_completion(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        config: Optional[AIModelConfig] = None,
        user_id: Optional[UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AIResponse:
        """Generate a completion from Gemini."""
        # Check rate limits first
        await rate_limit_service.check_rate_limit(user_id)

        # Use provided config or defaults
        if config is None:
            config = AIModelConfig(
                model=self.default_model,
                temperature=self.default_temperature,
                max_tokens=self.default_max_tokens,
            )

        # Combine system prompt and user prompt (Gemini doesn't have separate system role)
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Log request
        logger.info(
            f"Gemini request - Model: {config.model}, User: {user_id}, "
            f"Prompt length: {len(full_prompt)}"
        )

        # Call API
        response = await self._call_gemini_api(full_prompt, config, user_id)

        # Create response
        ai_response = self._create_ai_response(response, config.model, user_id)

        # Record actual cost (will be $0 for free tier)
        await cost_tracking_service.record_cost(user_id, ai_response.usage.estimated_cost)

        # Record successful request for rate limiting
        await rate_limit_service.record_request(user_id)

        logger.info(
            f"Gemini response - Tokens: {ai_response.usage.total_tokens}, "
            f"Cost: ${ai_response.usage.estimated_cost:.4f}"
        )

        return ai_response

    async def tailor_resume(
        self,
        master_resume: dict[str, Any],
        job_description: str,
        *,
        prompt_template: str,
        company_name: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> AIResponse:
        """Tailor a resume for a specific job using Gemini."""
        # Format the prompt with actual data
        try:
            from string import Template

            resume_json = json.dumps(master_resume, indent=2)
            logger.debug(f"Resume JSON length: {len(resume_json)}")

            # Replace format-style placeholders with Template-style
            template_str = prompt_template.replace("{master_resume}", "$master_resume")
            template_str = template_str.replace("{job_description}", "$job_description")
            template_str = template_str.replace("{company_name}", "$company_name")

            template = Template(template_str)
            prompt = template.safe_substitute(
                master_resume=resume_json,
                job_description=job_description,
                company_name=company_name or "the company",
            )
        except Exception as e:
            logger.error(f"Failed to format prompt template: {e}")
            logger.error(f"Prompt template: {prompt_template[:200]}")
            raise AIProviderError(f"Failed to format resume tailoring prompt: {e}")

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
        """Generate a cover letter using Gemini."""
        from string import Template

        template = Template(prompt_template)
        prompt = template.safe_substitute(
            resume_summary=resume_summary,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
        )

        system_prompt = (
            "You are an expert cover letter writer specializing in executive-level "
            "professional communications. Create persuasive, personalized cover letters "
            "that demonstrate cultural fit and quantifiable value."
        )

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
            metadata={"task": "cover_letter", "company": company_name},
        )

    async def classify_email(
        self,
        email_subject: str,
        email_body: str,
        *,
        user_id: Optional[UUID] = None,
    ) -> str:
        """Classify an email using Gemini."""
        prompt = f"""Classify this email into one of these categories:
- confirmation: Application received confirmation
- interview: Interview invitation or scheduling
- rejection: Application rejection
- offer: Job offer
- other: Other correspondence

Email Subject: {email_subject}
Email Body: {email_body}

Return only the category name, nothing else."""

        config = AIModelConfig(
            model=self.default_model,
            temperature=0.1,
            max_tokens=20,
        )

        response = await self.generate_completion(prompt, config=config, user_id=user_id)
        return response.content.strip().lower()

    async def get_usage_stats(self, user_id: Optional[UUID] = None) -> dict[str, Any]:
        """Get usage statistics."""
        if user_id:
            key = str(user_id)
            return self._usage_stats.get(key, {})
        return self._usage_stats
