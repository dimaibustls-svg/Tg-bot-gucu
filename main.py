import asyncio
import os
import base64
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
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


# --- 2. СОЗДАНИЕ ФАЙЛА СЕССИИ ИЗ ГОТОВОГО КОДА ---
API_ID = 37787095
API_HASH = '8e8f268ad7ac6229969e7dcf75677b48'

# Превращаем вашу строку сессии обратно в стандартный файл Telethon
# Используем готовую base64-строку вашей сессии без ошибок декодирования StringSession
SESSION_B64 = "1BVtsOHQBu2AwdLPqqAZ2NM9EXv-BKSvLtg-i2lmT19IYMIPZBhIsGnzgej1n0nMXjCJUPuJDUQcxXQj17AdzFucjAitS06jkoGzQ0PXG3ZSfv011vPfAmmlp8QaDSdfFaDtatgphX5fGKAGEz5B2q7DxicvD5_AcWaU2Eml1NvIBOl-dBE0WSHJ0LpEUta9ibTqlUJpmXR6qTrSOModoYAwayqptGchz0zI5aTqOwSz-CY1F-tYW7u_JgWyhKksbq7_DypmEeIHD2wZaQjPLUHxCae-TixlBYVqENyxNys_wb2QuJ3P540JRMXBRvEE_7M5FLliWyMyywxEZT5fCOZzPw4c="

# Записываем файл сессии на диск перед запуском клиента
# (Если StringSession капризничает, то файл .session работает всегда стабильно)
import sqlite3
# Создаем пустой файл session.session, если его нет
if not os.path.exists('session.session'):
    # Telethon использует SQLite для файлов сессий. 
    # Вместо хрупких строк распакуем через StringSession один раз безопасно:
    from telethon.sessions import StringSession
    temp_client = TelegramClient(StringSession(SESSION_B64), API_ID, API_HASH)
    # Сохраняем сессию в файл session.session
    temp_client.session.save()
    # Переименовываем или копируем в нужный файл
    if os.path.exists('anon.session'):
        os.replace('anon.session', 'session.session')

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
async def start_broadcast_task(event):
    global is_broadcasting
    is_broadcasting = True
    success_count = 0
    skipped_count = 0
    
    try:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.id, BROADCAST_TEXT)
                    success_count += 1
                    await asyncio.sleep(1)
                except FloodWaitError as e:
                    print(f"[FloodWait] На паузе {e.seconds} сек.")
                    skipped_count += 1
                    await asyncio.sleep(2)
                    continue
                except (UserBannedInChannelError, ChatWriteForbiddenError, ChannelPrivateError):
                    skipped_count += 1
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    print(f"[Ошибка] {e}")
                    skipped_count += 1
                    await asyncio.sleep(1)
                    continue
    finally:
        is_broadcasting = False
        await client.send_message(
            'me',
            f"✅ Рассылка завершена!\n\n"
            f"• Успешно: {success_count}\n"
            f"• Пропущено: {skipped_count}"
        )


# --- КОМАНДА .go ---
@client.on(events.NewMessage(pattern=r'\.go'))
async def run_broadcast(event):
    global is_broadcasting
    if is_broadcasting:
        await event.reply("⚠️ Рассылка уже выполняется!")
        return
    
    await event.reply("🚀 Начинаю рассылку по чатам...")
    asyncio.create_task(start_broadcast_task(event))


print("Бот запущен!")
client.start()
client.run_until_disconnected()
