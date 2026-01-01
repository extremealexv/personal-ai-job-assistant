"""Abstract base class for AI providers."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class AIModelConfig(BaseModel):
    """Configuration for AI model."""

    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class AIUsageMetrics(BaseModel):
    """Metrics for AI API usage."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float


class AIResponse(BaseModel):
    """Response from AI provider."""

    content: str
    model: str
    usage: AIUsageMetrics
    finish_reason: str
    provider: str


class AIProvider(ABC):
    """Abstract base class for AI providers.
    
    This interface allows swapping between different AI providers (OpenAI, Anthropic, etc.)
    without changing business logic.
    """

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        config: Optional[AIModelConfig] = None,
        user_id: Optional[UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AIResponse:
        """Generate a completion from the AI model.
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt to set behavior
            config: Model configuration (temperature, max_tokens, etc.)
            user_id: User ID for tracking/rate limiting
            metadata: Additional metadata for logging/tracking
            
        Returns:
            AIResponse with content and usage metrics
            
        Raises:
            AIProviderError: If API call fails
            RateLimitError: If rate limit exceeded
        """
        pass

    @abstractmethod
    async def tailor_resume(
        self,
        master_resume: dict[str, Any],
        job_description: str,
        *,
        prompt_template: str,
        company_name: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> AIResponse:
        """Tailor a resume for a specific job.
        
        Args:
            master_resume: Structured master resume data
            job_description: Target job description
            prompt_template: Prompt template with placeholders
            company_name: Target company name
            user_id: User ID for tracking
            
        Returns:
            AIResponse with tailored resume content
        """
        pass

    @abstractmethod
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
        """Generate a cover letter.
        
        Args:
            resume_summary: Summary of candidate's experience
            job_description: Target job description
            prompt_template: Prompt template with placeholders
            company_name: Target company name
            job_title: Target job title
            user_id: User ID for tracking
            
        Returns:
            AIResponse with cover letter content
        """
        pass

    @abstractmethod
    async def classify_email(
        self,
        email_subject: str,
        email_body: str,
        *,
        user_id: Optional[UUID] = None,
    ) -> str:
        """Classify an email (confirmation, interview, rejection, etc.).
        
        Args:
            email_subject: Email subject line
            email_body: Email body text
            user_id: User ID for tracking
            
        Returns:
            Classification category
        """
        pass

    @abstractmethod
    async def get_usage_stats(self, user_id: Optional[UUID] = None) -> dict[str, Any]:
        """Get usage statistics.
        
        Args:
            user_id: Optional user ID to filter stats
            
        Returns:
            Dictionary with usage statistics
        """
        pass
