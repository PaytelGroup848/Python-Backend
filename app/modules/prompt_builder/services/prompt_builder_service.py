from app.modules.prompt_builder.schemas.prompt_request import (
    PromptRequest
)

from app.modules.prompt_builder.schemas.prompt_response import (
    PromptResponse
)


class PromptBuilderService:

    async def build(

        self,

        request: PromptRequest

    ) -> PromptResponse:

        runtime = request.workspace_runtime

        system_prompt = ""

        if runtime.get("assistant_name"):

            system_prompt += (

                f"You are {runtime['assistant_name']}.\n"

            )

        if runtime.get("system_prompt"):

            system_prompt += (

                runtime["system_prompt"]

            )

        context = "\n\n".join(

            request.retrieved_context

        )

        history = "\n".join(

            request.chat_history

        )

        user_prompt = f"""
Retrieved Context
-----------------
{context}

Conversation History
--------------------
{history}

User Question
-------------
{request.user_message}
"""

        return PromptResponse(

            system_prompt=system_prompt,

            user_prompt=user_prompt

        )


prompt_builder_service = (
    PromptBuilderService()
)