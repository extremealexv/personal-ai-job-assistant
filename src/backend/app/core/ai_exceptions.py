"""Custom exceptions for AI provider."""


class AIProviderError(Exception):
    """Base exception for AI provider errors."""

    pass


class RateLimitError(AIProviderError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message)


class InvalidAPIKeyError(AIProviderError):
    """Invalid or missing API key."""

    pass


class ModelNotFoundError(AIProviderError):
    """Requested model not found or not available."""

    pass


class TokenLimitExceededError(AIProviderError):
    """Token limit exceeded for request."""

    def __init__(self, message: str, requested_tokens: int, max_tokens: int):
        self.requested_tokens = requested_tokens
        self.max_tokens = max_tokens
        super().__init__(message)


class ContentFilterError(AIProviderError):
    """Content filtered by provider's safety system."""

    pass
