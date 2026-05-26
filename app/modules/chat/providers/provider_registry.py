from app.modules.chat.providers.openai_provider import (
    OpenAIProvider
)

from app.modules.chat.providers.groq_provider import (
    GroqProvider
)

from app.modules.chat.providers.mistral_provider import (
    MistralProvider
)


provider_registry = {

    "openai":
        OpenAIProvider(),

    "llama":
        GroqProvider(),

    "mistral":
        MistralProvider(),
}