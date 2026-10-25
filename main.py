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


# --- 2. НАСТРОЙКА БОТА ---
API_ID = 37787095
API_HASH = '8e8f268ad7ac6229969e7dcf75677b48'

# Безопасная инициализация клиента с защитой от повреждения строки сессии
SESSION_STRING = os.environ.get('SESSION_STRING', '')
if SESSION_STRING.strip():
    try:
        client = TelegramClient(StringSession(SESSION_STRING.strip()), API_ID, API_HASH)
        print("[Клиент] Используется StringSession из переменных окружения.")
    except Exception as e:
        print(f"[Ошибка сессии] Не удалось загрузить StringSession: {e}. Переход на файловую сессию.")
        client = TelegramClient('session', API_ID, API_HASH)
else:
    print("[Клиент] SESSION_STRING не найдена, используется файловая сессия.")
    client = TelegramClient('session', API_ID, API_HASH)


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


# --- АВТООТВЕТЧИК В ЛИЧКУ ---
@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    sender_id = event.sender_id
    count = user_reply_count.get(sender_id, 0)
    
    if count >= 2:
        return

    if count == 0:
        user_reply_count[sender_id] = 1
        await asyncio.sleep(60)
        await event.respond(FIRST_REPLY)
        print(f"[Автоответ 1/2] Отправлен")

    elif count == 1:
        user_reply_count[sender_id] = 2
        await asyncio.sleep(60)
        await event.respond(SECOND_REPLY)
        print(f"[Автоответ 2/2] Отправлен")


# --- ФУНКЦИЯ РАССЫЛКИ ПО ЧАТАМ ---
