import asyncio
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

# --- Заглушка веб-сервера для Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# Запускаем веб-сервер в отдельном потоке
Thread(target=run_web_server, daemon=True).start()

# --- Ваши ключи ---
API_ID = 37787095[span_3](start_span)[span_3](end_span)
API_HASH = '8e8f268ad7ac6229969e7dcf75677b48[span_4](start_span)'[span_4](end_span)

client = TelegramClient('anon', API_ID, API_HASH)[span_5](start_span)[span_5](end_span)

# --- ВАШИ ТЕКСТЫ ---
BROADCAST_TEXT = "Хочешь провести хорошо время? Если да, жду в лс 😉[span_6](start_span)"[span_6](end_span)

FIRST_REPLY = "Привет если ты по поводу того что я писала в чат жду тебя в телеграме[span_7](start_span)"[span_7](end_span)

SECOND_REPLY = "Я сейчас немного занята если есть вопросы пиши в телеграм[span_8](start_span)"[span_8](end_span)

user_reply_count = {}[span_9](start_span)[span_9](end_span)

# --- 1. АВТООТВЕТЧИК В ЛИЧКУ ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span)
async def auto_reply(event):
    sender_id = event.sender_id[span_12](start_span)[span_12](end_span)
    count = user_reply_count.get(sender_id, 0)[span_13](start_span)[span_13](end_span)

    if count == 0:
        await asyncio.sleep(60)[span_14](start_span)[span_14](end_span)
        await event.respond(FIRST_REPLY)[span_15](start_span)[span_15](end_span)[span_16](start_span)[span_16](end_span)
        user_reply_count[sender_id] = 1[span_17](start_span)[span_17](end_span)[span_18](start_span)[span_18](end_span)
        print(f"[Автоответ 1/2] Отправлен пользователю {sender_id}")[span_19](start_span)[span_19](end_span)[span_20](start_span)[span_20](end_span)
    elif count == 1:
        await asyncio.sleep(60)[span_21](start_span)[span_21](end_span)[span_22](start_span)[span_22](end_span)
        await event.respond(SECOND_REPLY)[span_23](start_span)[span_23](end_span)
        user_reply_count[sender_id] = 2[span_24](start_span)[span_24](end_span)
        print(f"[Автоответ 2/2] Отправлен пользователю {sender_id}")[span_25](start_span)[span_25](end_span)
    else:
        pass[span_26](start_span)[span_26](end_span)

# --- 2. РАССЫЛКА ПО ЧАТАМ ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.go$'))
async def run_broadcast(event):
    await event.edit("🚀 Начинаю рассылку по чатам...")[span_27](start_span)[span_27](end_span)
    success_count = 0[span_28](start_span)[span_28](end_span)

    async for dialog in client.iter_dialogs():[span_29](start_span)[span_29](end_span)
        if dialog.is_group or dialog.is_channel:[span_30](start_span)[span_30](end_span)
            try:
                await client.send_message(dialog.id, BROADCAST_TEXT)[span_31](start_span)[span_31](end_span)
                success_count += 1[span_32](start_span)[span_32](end_span)
                print(f"Отправлено в чат: {dialog.name}")[span_33](start_span)[span_33](end_span)
                await asyncio.sleep(45)[span_34](start_span)[span_34](end_span)
            except Exception as e:
                print(f"Ошибка отправки в {dialog.name}: {e}")[span_35](start_span)[span_35](end_span)

    await client.send_message('me', f"✅ Рассылка завершена! Успешно отправлено в {success_count} чатов.")[span_36](start_span)[span_36](end_span)

print("Бот запущен и работает с повышенной стабильностью!")[span_37](start_span)[span_37](end_span)
client.start()[span_38](start_span)[span_38](end_span)
client.run_until_disconnected()[span_39](start_span)[span_39](end_span)
