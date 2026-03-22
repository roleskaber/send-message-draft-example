import os
import httpx
import random
from fastapi import FastAPI, Request
from openai import AsyncClient


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncClient()

app = FastAPI()

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


async def send_draft(chat_id, draft_id, text):
    async with httpx.AsyncClient() as http:
        r = await http.post(f"{TELEGRAM_API}/sendMessageDraft", json={
            "chat_id": chat_id,
            "draft_id": draft_id,
            "text": text
        })
        print("sendMessageDraft:", r.status_code, r.text)


async def send_message(chat_id, text):
    async with httpx.AsyncClient() as http:
        await http.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })


async def generate_stream(user_text):
    stream = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": user_text}],
        stream=True
    )
    async for chunk in stream:
        yield chunk


@app.post("/telegram/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return True

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")
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
            await send_draft(chat_id, draft_id, buffer)
            local_buffer = ""
        counter += 1

    await send_message(chat_id, buffer)
    return True
