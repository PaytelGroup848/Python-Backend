from app.modules.providers.openai_provider import (
    OpenAIProvider
)

from app.modules.providers.groq_provider import (
    GroqProvider
)

from app.modules.providers.mistral_provider import (
    MistralProvider
)

from app.modules.providers.gemini_provider import (
    GeminiProvider
)


provider_registry = {

    "openai": OpenAIProvider(),

    "groq": GroqProvider(),

    "mistral": MistralProvider(),

    "gemini": GeminiProvider()
}