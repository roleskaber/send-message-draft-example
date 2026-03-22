import random
from fastapi import FastAPI, Body
from openai import AsyncClient

from telegram_api_manager import TelegramApiManager

client = AsyncClient()
telegram_api_manager = TelegramApiManager()
app = FastAPI()


async def generate_stream(user_text):
    stream = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": user_text}],
        stream=True
    )
    async for chunk in stream:
        yield chunk


@app.post("/telegram/webhook")
async def webhook(body: dict = Body(...)):
    if "message" not in body:
        return True

    chat_id = body["message"]["chat"]["id"]
    user_text = body["message"].get("text", "")

    # for animation
    draft_id = random.randint(1, 2_147_483_647)
    # global buffer
    buffer = ""

    local_buffer = ""
    counter = 0

    async for chunk in generate_stream(user_text):
        delta = chunk.choices[0].delta.content or ""
        if not delta:
            continue
        buffer += delta
        local_buffer += delta
        if counter % 2 == 0:
            await telegram_api_manager.send_draft(chat_id, draft_id, buffer)
            local_buffer = ""
        counter += 1

    await telegram_api_manager.send_message(chat_id, buffer)
    return True
