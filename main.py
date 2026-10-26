import asyncio
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError,
    UserBannedInChannelError,
    ChatWriteForbiddenError,
    ChannelPrivateError
)

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


# --- 2. ПОДКЛЮЧЕНИЕ К TELEGRAM ---
API_ID = 37787095
API_HASH = '8e8f268ad7ac6229969e7dcf75677b48'

SESSION_STRING = '1BVtsOHQBuxsu6PoXmwGcF4twEvSvpRLmCQATzgWP5jfYw-naAFtOclSxgsfM3bLQ2-ahVuPDMYUZs1F3M9ABQJ0FJMNVsM7DgQgWsQNa6583zTE9Y7qBsXWjvQs7gxsuYnZOgsVZLAHkljKHRapNu6noDSwYeZkqL0KW68wAoH569nIHDCdllwF_exWbo5TLxtSD3y6UKFZOD-i3HrsCqc_naUUZzeeSUKlI5Bs-DOPE10HFxHzKzctY50uNiU3yr-n01blB9Ir9bvIX8WHRX3W_rL1qdm_DolEJ_k0BTm8N5BBC3iAR8ItM-O1zKngjaw-dfhiokpfyjFQARIaUM_PllvkPSDw='

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


# --- ТЕКСТЫ ---
BROADCAST_TEXT = "Хочешь провести хорошо"

FIRST_REPLY = (
    "Привет если ты по поводу того что я\n"
    "и менеджера если хочешь узнать подроб\n"
    "82275 и скажи что хочешь узнать подр"
)

SECOND_REPLY = "Извини я щас занята если"

user_reply_count = {}
is_broadcasting = False


# --- АВТООТВЕТЧИК ТОЛЬКО В ЛИЧНЫХ СООБЩЕНИЯХ ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender_id = event
