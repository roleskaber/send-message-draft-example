from openai import AsyncClient
from openai.types.responses import ResponseStreamEvent, ResponseTextDeltaEvent, ResponseTextDoneEvent


class GptProcessor:
    def __init__(self):
        self.client = AsyncClient()

    async def generate_stream(self, user_text):
        stream = await self.client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": "user", "content": user_text}],
            stream=True
        )
        async for chunk in stream:
            yield chunk

    @staticmethod
    def dispatch(body: ResponseStreamEvent):
        if isinstance(body, ResponseTextDeltaEvent):
            return body.delta
        return None

