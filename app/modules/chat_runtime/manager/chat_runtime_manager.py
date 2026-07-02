class ChatRuntimeManager:

    async def execute(

        self,

        callback,

        *args,

        **kwargs

    ):

        return await callback(
            *args,
            **kwargs
        )


chat_runtime_manager = (
    ChatRuntimeManager()
)