import random
from fastapi import FastAPI, Body

from gpt import GptProcessor
from telegram_api_manager import TelegramApiManager

telegram_api_manager = TelegramApiManager()
gpt_client = GptProcessor()
app = FastAPI()



@app.post("/telegram/webhook")
async def webhook(body: dict = Body(...)):
    if "message" not in body:
        return True

    chat_id = body["message"]["chat"]["id"]
    user_text = body["message"].get("text", "")
    buffer = ""
    # for animation
    draft_id = random.randint(1, 2_147_483_647)
    # global buffer
    counter = 0

    async for chunk in gpt_client.generate_stream(user_text):
        delta = gpt_client.dispatch(chunk)
        if not delta: continue
        buffer += delta
        if counter % 2 == 0:
            await telegram_api_manager.send_draft(chat_id, draft_id, buffer)
        counter += 1
    await telegram_api_manager.send_message(chat_id, buffer)
    return True
