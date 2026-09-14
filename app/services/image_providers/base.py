from abc import ABC, abstractmethod
from typing import Tuple


class ContentPolicyViolationError(Exception):
    """Raised when a prompt violates safety or content policy. Should NOT fallback."""
    pass


class ProviderTimeoutError(Exception):
    """Raised when provider request times out. Eligible for fallback."""
    pass


class ProviderAPIError(Exception):
    """Raised when provider returns 5xx or connection error. Eligible for fallback."""
    pass


class BaseImageProvider(ABC):
    """Abstract base class for all image generation providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'openai', 'flux')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the model (e.g., 'dall-e-3', 'flux-1.1-pro')."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Tuple[bytes, str]:
        """
        Generates an image from a prompt.
        Returns:
            Tuple of (raw_image_bytes, revised_prompt_or_original)
        """
        pass
