import asyncio
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

# --- 1. ВЕБ-СЕРВЕР ДЛЯ RENDER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_web_server, daemon=True).start()

# --- 2. НАСТРОЙКА БОТА ---
API_ID = 37787095
API_HASH = '8e8f268ad7ac6229969e7dcf75677b48'

client = TelegramClient('anon', API_ID, API_HASH)

BROADCAST_TEXT = "Хочешь провести хорошо время? Если да, жду в лс 😉"
FIRST_REPLY = "Привет если ты по поводу того что я писала в чат жду тебя в телеграме"
SECOND_REPLY = "Я сейчас немного занята если есть вопросы пиши в телеграм"

user_reply_count = {}

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender_id = event.sender_id
    count = user_reply_count.get(sender_id, 0)

    if count == 0:
        await asyncio.sleep(60)
        await event.respond(FIRST_REPLY)
        user_reply_count[sender_id] = 1
    elif count == 1:
        await asyncio.sleep(60)
        await event.respond(SECOND_REPLY)
        user_reply_count[sender_id] = 2

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.go$'))
async def run_broadcast(event):
    await event.edit("🚀 Начинаю рассылку по чатам...")
    success_count = 0

    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            try:
                await client.send_message(dialog.id, BROADCAST_TEXT)
                success_count += 1
                await asyncio.sleep(45)
            except Exception as e:
                print(f"Ошибка: {e}")

    await client.send_message('me', f"✅ Рассылка завершена! Успешно отправлено в {success_count} чатов.")

print("Бот запущен!")
client.start()
client.run_until_disconnected()
