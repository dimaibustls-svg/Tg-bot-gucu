import asyncio
import os
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError,
    UserBannedInChannelError,
    ChatWriteForbiddenError,
    ChannelPrivateError
)

# --- 1. ПРОСТОЙ ВЕБ-СЕРВЕР ДЛЯ RENDER (aiohttp) ---
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер успешно запущен на порту {port}")


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


# --- АВТООТВЕТЧИК В ЛИЧНЫХ СООБЩЕНИЯХ (задержка 60 секунд) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender_id = event.sender_id
    count = user_reply_count.get(sender_id, 0)
    
    if count >= 2:
        return

    if count == 0:
        user_reply_count[sender_id] = 1
        await asyncio.sleep(60)
        await event.respond(FIRST_REPLY)
        print(f"[Автоответ 1/2 в ЛС] Отправлен")

    elif count == 1:
        user_reply_count[sender_id] = 2
        await asyncio.sleep(60)
        await event.respond(SECOND_REPLY)
        print(f"[Автоответ 2/2 в ЛС] Отправлен")


# --- БЫСТРАЯ РАССЫЛКА С ЖИВЫМИ ОТЧЕТАМИ ---
async def start_broadcast_task(event):
    global is_broadcasting
    is_broadcasting = True
    success_count = 0
    skipped_count = 0
    total_checked = 0
    
    try:
        await client.send_message('me', "🚀 Начинаю рассылку, слежу за процессом...")
        dialogs = await client.get_dialogs()
        
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                total_checked += 1
                try:
                    await client.send_message(dialog.id, BROADCAST_TEXT)
                    success_count += 1
                    print(f"[Успех] Отправлено в чат: {dialog.title}")
                    
                    # Оптимальная пауза 4 секунды, чтобы не вешать скрипт и не спамить
                    await asyncio.sleep(4)
                    
                except FloodWaitError as e:
                    print(f"[FloodWait] Пауза {e.seconds} сек.")
                    skipped_count += 1
                    await asyncio.sleep(e.seconds + 2)
                    continue
                except (UserBannedInChannelError, ChatWriteForbiddenError, ChannelPrivateError):
                    skipped_count += 1
                    continue
                except Exception as ex:
                    print(f"[Пропуск] Ошибка: {ex}")
                    skipped_count += 1
                    continue
    except Exception as e:
        print(f"[Критическая ошибка рассылки]: {e}")
    finally:
        is_broadcasting = False
        # Финальный отчет
        await client.send_message(
            'me',
            f"✅ **Рассылка успешно завершена!**\n\n"
            f"• Проверено чатов: {total_checked}\n"
            f"• Успешно отправлено: {success_count}\n"
            f"• Пропущено / Ошибки: {skipped_count}"
        )


# --- КОМАНДА .go ---
@client.on(events.NewMessage(pattern=r'\.go'))
async def run_broadcast(event):
    global is_broadcasting
    if is_broadcasting:
        await event.reply("⚠️ Рассылка уже выполняется!")
        return
    
    await event.reply("🚀 Запускаю шуструю рассылку...")
    asyncio.create_task(start_broadcast_task(event))


# --- ГЛАВНАЯ ТОЧКА ВХОДА ---
async def main():
    await start_web_server()
    print("Подключаемся к Telegram...")
    await client.start()
    print("Бот успешно запущен и работает!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
