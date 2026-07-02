from app.modules.chat.providers.openai_provider import (
    OpenAIProvider
)

from app.modules.chat.providers.groq_provider import (
    GroqProvider
)

from app.modules.chat.providers.mistral_provider import (
    MistralProvider
)

from app.modules.chat.providers.gemini_provider import (
    GeminiProvider
)


provider_registry = {

    "openai": OpenAIProvider(),

    "groq": GroqProvider(),

    "mistral": MistralProvider(),

    "gemini": GeminiProvider()
}