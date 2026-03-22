import os
import httpx


class TelegramApiManager:
    def __init__(self, token=None):
        token = token or os.getenv("TELEGRAM_TOKEN")
        self.TELEGRAM_API = f"https://api.telegram.org/bot{token}"

    async def send_draft(self, chat_id, draft_id, text):
        async with httpx.AsyncClient() as http:
            r = await http.post(f"{self.TELEGRAM_API}/sendMessageDraft", json={
                "chat_id": chat_id,
                "draft_id": draft_id,
                "text": text
            })
            print("sendMessageDraft:", r.status_code, r.text)

    async def send_message(self, chat_id, text):
        async with httpx.AsyncClient() as http:
            await http.post(f"{self.TELEGRAM_API}/sendMessage", json={
                "chat_id": chat_id,
                "text": text
            })
