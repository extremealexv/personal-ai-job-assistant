"""Unit tests for OpenAI provider."""
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from openai import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError as OpenAIRateLimitError,
)
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from app.core.ai_exceptions import (
    AIProviderError,
    ContentFilterError,
    InvalidAPIKeyError,
    ModelNotFoundError,
    RateLimitError,
    TokenLimitExceededError,
)
from app.core.ai_provider import AIModelConfig
from app.providers.openai_provider import OpenAIProvider


@pytest.fixture
def openai_provider():
    """Create OpenAI provider instance with mocked client."""
    with patch("app.providers.openai_provider.AsyncOpenAI"):
        provider = OpenAIProvider()
        provider.client = AsyncMock()
        return provider


@pytest.fixture
def mock_completion():
    """Create a mock OpenAI completion response."""

    def _create_completion(
        content: str = "Test response",
        model: str = "gpt-4",
        prompt_tokens: int = 100,
        completion_tokens: int = 50,
        finish_reason: str = "stop",
    ) -> ChatCompletion:
        return ChatCompletion(
            id="chatcmpl-123",
            object="chat.completion",
            created=1677652288,
            model=model,
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(role="assistant", content=content),
                    finish_reason=finish_reason,
                )
            ],
            usage=CompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

    return _create_completion


class TestOpenAIProviderInitialization:
    """Test OpenAI provider initialization."""

    @patch("app.providers.openai_provider.AsyncOpenAI")
    def test_initialization_success(self, mock_async_openai):
        """Test successful initialization."""
        provider = OpenAIProvider()

        assert provider.client is not None
        assert provider.default_model == "gpt-4"
        mock_async_openai.assert_called_once()

    @patch("app.config.settings.openai_api_key", None)
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(InvalidAPIKeyError):
            OpenAIProvider()


class TestGenerateCompletion:
    """Test generate_completion method."""

    @pytest.mark.asyncio
    async def test_basic_completion(self, openai_provider, mock_completion):
        """Test basic completion generation."""
        completion = mock_completion(content="Hello, world!")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        response = await openai_provider.generate_completion("Test prompt")

        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage.prompt_tokens == 100
        assert response.usage.completion_tokens == 50
        assert response.usage.total_tokens == 150
        assert response.usage.estimated_cost > 0

    @pytest.mark.asyncio
    async def test_completion_with_system_prompt(self, openai_provider, mock_completion):
        """Test completion with system prompt."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        await openai_provider.generate_completion(
            "Test prompt", system_prompt="You are a helpful assistant"
        )

        call_args = openai_provider.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_completion_with_custom_config(self, openai_provider, mock_completion):
        """Test completion with custom configuration."""
        completion = mock_completion(model="gpt-3.5-turbo")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        config = AIModelConfig(
            model="gpt-3.5-turbo", temperature=0.5, max_tokens=500, top_p=0.9
        )

        await openai_provider.generate_completion("Test prompt", config=config)

        call_args = openai_provider.client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-3.5-turbo"
        assert call_args.kwargs["temperature"] == 0.5
        assert call_args.kwargs["max_tokens"] == 500
        assert call_args.kwargs["top_p"] == 0.9

    @pytest.mark.asyncio
    async def test_completion_with_user_id(self, openai_provider, mock_completion):
        """Test completion tracks user ID for usage stats."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        user_id = uuid4()
        await openai_provider.generate_completion("Test prompt", user_id=user_id)

        stats = await openai_provider.get_usage_stats(user_id)
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 150


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_rate_limit_error_with_retry(self, openai_provider, mock_completion):
        """Test rate limit error triggers retry."""
        completion = mock_completion()

        # Fail twice, then succeed
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=[
                OpenAIRateLimitError("Rate limit", response=MagicMock(), body=None),
                OpenAIRateLimitError("Rate limit", response=MagicMock(), body=None),
                completion,
            ]
        )

        response = await openai_provider.generate_completion("Test prompt")
        assert response.content == "Test response"
        assert openai_provider.client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_rate_limit_error_exceeds_retries(self, openai_provider):
        """Test rate limit error after max retries."""
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=OpenAIRateLimitError("Rate limit", response=MagicMock(), body=None)
        )

        with pytest.raises(RateLimitError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_authentication_error(self, openai_provider):
        """Test authentication error."""
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=AuthenticationError("Invalid API key", response=MagicMock(), body=None)
        )

        with pytest.raises(InvalidAPIKeyError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_model_not_found_error(self, openai_provider):
        """Test model not found error."""
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=NotFoundError("Model not found", response=MagicMock(), body=None)
        )

        with pytest.raises(ModelNotFoundError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_token_limit_exceeded_error(self, openai_provider):
        """Test token limit exceeded error."""
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=BadRequestError(
                "maximum context length exceeded", response=MagicMock(), body=None
            )
        )

        with pytest.raises(TokenLimitExceededError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_content_filter_error(self, openai_provider, mock_completion):
        """Test content filter error."""
        completion = mock_completion(finish_reason="content_filter")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        with pytest.raises(ContentFilterError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_generic_error(self, openai_provider):
        """Test generic error handling."""
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=Exception("Unknown error")
        )

        with pytest.raises(AIProviderError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_generic_error_with_retry(self, openai_provider, mock_completion):
        """Test generic error retries then succeeds."""
        completion = mock_completion()

        # Fail twice with generic error, then succeed
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=[
                Exception("Network error"),
                Exception("Timeout"),
                completion,
            ]
        )

        response = await openai_provider.generate_completion("Test prompt")
        assert response.content == "Test response"
        assert openai_provider.client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_bad_request_error(self, openai_provider):
        """Test generic bad request error."""
        openai_provider.client.chat.completions.create = AsyncMock(
            side_effect=BadRequestError("Invalid parameters", response=MagicMock(), body=None)
        )

        with pytest.raises(AIProviderError):
            await openai_provider.generate_completion("Test prompt")

    @pytest.mark.asyncio
    async def test_missing_usage_data(self, openai_provider):
        """Test error when OpenAI response has no usage data."""
        # Create completion without usage data
        completion = ChatCompletion(
            id="chatcmpl-123",
            object="chat.completion",
            created=1677652288,
            model="gpt-4",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(role="assistant", content="Test"),
                    finish_reason="stop",
                )
            ],
            usage=None,  # Missing usage data
        )

        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        with pytest.raises(AIProviderError, match="No usage data"):
            await openai_provider.generate_completion("Test prompt")


class TestResumeTailoring:
    """Test tailor_resume method."""

    @pytest.mark.asyncio
    async def test_tailor_resume_basic(self, openai_provider, mock_completion):
        """Test basic resume tailoring."""
        completion = mock_completion(content="Tailored resume JSON")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        master_resume = {
            "full_name": "John Doe",
            "work_experiences": [{"company": "TechCorp", "title": "Engineer"}],
        }
        job_description = "Looking for a senior engineer"
        prompt_template = "Tailor this resume:\n{master_resume}\n\nFor this job:\n{job_description}"

        response = await openai_provider.tailor_resume(
            master_resume, job_description, prompt_template=prompt_template
        )

        assert response.content == "Tailored resume JSON"
        assert response.model == "gpt-4"

        # Check system prompt was set
        call_args = openai_provider.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert "expert resume writer" in messages[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_tailor_resume_with_company_name(self, openai_provider, mock_completion):
        """Test resume tailoring with company name."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        master_resume = {"full_name": "John Doe"}
        prompt_template = "Company: {company_name}"

        await openai_provider.tailor_resume(
            master_resume, "Job desc", prompt_template=prompt_template, company_name="TechCorp"
        )

        call_args = openai_provider.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert "TechCorp" in messages[1]["content"]


class TestCoverLetterGeneration:
    """Test generate_cover_letter method."""

    @pytest.mark.asyncio
    async def test_generate_cover_letter_basic(self, openai_provider, mock_completion):
        """Test basic cover letter generation."""
        completion = mock_completion(content="Dear Hiring Manager...")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        prompt_template = (
            "Generate cover letter for {job_title} at {company_name}.\n"
            "Resume: {resume_summary}\nJob: {job_description}"
        )

        response = await openai_provider.generate_cover_letter(
            resume_summary="Experienced engineer",
            job_description="Senior role",
            prompt_template=prompt_template,
            company_name="TechCorp",
            job_title="Senior Engineer",
        )

        assert response.content == "Dear Hiring Manager..."

        # Check system prompt
        call_args = openai_provider.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert "cover letter writer" in messages[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_generate_cover_letter_formatting(self, openai_provider, mock_completion):
        """Test cover letter prompt formatting."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        prompt_template = "{company_name} - {job_title}"

        await openai_provider.generate_cover_letter(
            resume_summary="Summary",
            job_description="Desc",
            prompt_template=prompt_template,
            company_name="TechCorp",
            job_title="Engineer",
        )

        call_args = openai_provider.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert "TechCorp - Engineer" in messages[1]["content"]


class TestEmailClassification:
    """Test classify_email method."""

    @pytest.mark.asyncio
    async def test_classify_interview_email(self, openai_provider, mock_completion):
        """Test classifying an interview email."""
        completion = mock_completion(content="interview", model="gpt-3.5-turbo")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        classification = await openai_provider.classify_email(
            email_subject="Interview invitation",
            email_body="We would like to schedule an interview...",
        )

        assert classification == "interview"

        # Check using cheaper model
        call_args = openai_provider.client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-3.5-turbo"
        assert call_args.kwargs["temperature"] == 0.0

    @pytest.mark.asyncio
    async def test_classify_rejection_email(self, openai_provider, mock_completion):
        """Test classifying a rejection email."""
        completion = mock_completion(content="rejection", model="gpt-3.5-turbo")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        classification = await openai_provider.classify_email(
            email_subject="Application status",
            email_body="Unfortunately, we have decided to move forward...",
        )

        assert classification == "rejection"

    @pytest.mark.asyncio
    async def test_classify_invalid_category_defaults_to_other(
        self, openai_provider, mock_completion
    ):
        """Test invalid classification defaults to 'other'."""
        completion = mock_completion(content="invalid_category", model="gpt-3.5-turbo")
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        classification = await openai_provider.classify_email(
            email_subject="Test", email_body="Test body"
        )

        assert classification == "other"


class TestCostCalculation:
    """Test cost calculation."""

    def test_calculate_cost_gpt4(self, openai_provider):
        """Test cost calculation for GPT-4."""
        cost = openai_provider._calculate_cost("gpt-4", prompt_tokens=1000, completion_tokens=500)

        expected = (1000 / 1000 * 0.03) + (500 / 1000 * 0.06)
        assert cost == expected

    def test_calculate_cost_gpt35(self, openai_provider):
        """Test cost calculation for GPT-3.5-turbo."""
        cost = openai_provider._calculate_cost(
            "gpt-3.5-turbo", prompt_tokens=1000, completion_tokens=500
        )

        expected = (1000 / 1000 * 0.0005) + (500 / 1000 * 0.0015)
        assert cost == expected

    def test_calculate_cost_unknown_model_defaults_to_gpt4(self, openai_provider):
        """Test unknown model defaults to GPT-4 pricing."""
        cost = openai_provider._calculate_cost(
            "unknown-model", prompt_tokens=1000, completion_tokens=500
        )

        expected = (1000 / 1000 * 0.03) + (500 / 1000 * 0.06)
        assert cost == expected


class TestUsageTracking:
    """Test usage tracking."""

    @pytest.mark.asyncio
    async def test_track_single_request(self, openai_provider, mock_completion):
        """Test tracking a single request."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        user_id = uuid4()
        await openai_provider.generate_completion("Test", user_id=user_id)

        stats = await openai_provider.get_usage_stats(user_id)
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 150
        assert stats["total_cost"] > 0

    @pytest.mark.asyncio
    async def test_track_multiple_requests(self, openai_provider, mock_completion):
        """Test tracking multiple requests."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        user_id = uuid4()
        await openai_provider.generate_completion("Test 1", user_id=user_id)
        await openai_provider.generate_completion("Test 2", user_id=user_id)
        await openai_provider.generate_completion("Test 3", user_id=user_id)

        stats = await openai_provider.get_usage_stats(user_id)
        assert stats["total_requests"] == 3
        assert stats["total_tokens"] == 450

    @pytest.mark.asyncio
    async def test_track_by_model(self, openai_provider, mock_completion):
        """Test tracking by model."""
        gpt4_completion = mock_completion(model="gpt-4")
        gpt35_completion = mock_completion(model="gpt-3.5-turbo")

        user_id = uuid4()

        openai_provider.client.chat.completions.create = AsyncMock(return_value=gpt4_completion)
        await openai_provider.generate_completion("Test 1", user_id=user_id)

        openai_provider.client.chat.completions.create = AsyncMock(return_value=gpt35_completion)
        await openai_provider.generate_completion("Test 2", user_id=user_id)

        stats = await openai_provider.get_usage_stats(user_id)
        assert "gpt-4" in stats["by_model"]
        assert "gpt-3.5-turbo" in stats["by_model"]
        assert stats["by_model"]["gpt-4"]["requests"] == 1
        assert stats["by_model"]["gpt-3.5-turbo"]["requests"] == 1

    @pytest.mark.asyncio
    async def test_get_aggregate_stats(self, openai_provider, mock_completion):
        """Test getting aggregate stats across all users."""
        completion = mock_completion()
        openai_provider.client.chat.completions.create = AsyncMock(return_value=completion)

        user1 = uuid4()
        user2 = uuid4()

        await openai_provider.generate_completion("Test", user_id=user1)
        await openai_provider.generate_completion("Test", user_id=user2)

        aggregate_stats = await openai_provider.get_usage_stats()
        assert aggregate_stats["total_requests"] == 2
        assert aggregate_stats["users"] == 2
