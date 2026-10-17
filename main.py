import asyncio
from telethon import TelegramClient, events

# Ваши ключи
API_ID = 37787095  
API_HASH = '8e8f268ad7ac622969e7dcf75677b48'

client = TelegramClient('anon', API_ID, API_HASH)


# --- ВАШИ ТЕКСТЫ ---
BROADCAST_TEXT = "Хочешь провести хорошо время? Если хочешь узнать больше напиши в личные сообщения))"

FIRST_REPLY = "Привет если ты по поводу того что я написала в чате то работаю через агентство и менджера если хочешь узнать подробности или прайс напиши менджеру мой персональный код 30866 и скажи что хочешь узнать подробности или оформить заказ"

SECOND_REPLY = "Я сейчас немного занята если есть вопросы можешь задавать отвечу как освобожусь"

# Словарь для учета количества ответов пользователям
user_reply_count = {}

# --- 1. АВТООТВЕТЧИК В ЛИЧКУ (с задержкой 60 секунд для каждого) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender_id = event.sender_id
    
    count = user_reply_count.get(sender_id, 0)
    
    if count == 0:
        # Пауза 60 секунд перед первым ответом (имитация живого человека)
        await asyncio.sleep(60)
        await event.respond(FIRST_REPLY)
        user_reply_count[sender_id] = 1
        print(f"[Автоответ 1/2] Отправлен пользователю {sender_id}")
    elif count == 1:
        # Пауза 60 секунд перед вторым ответом
        await asyncio.sleep(60)
        await event.respond(SECOND_REPLY)
        user_reply_count[sender_id] = 2
        print(f"[Автоответ 2/2] Отправлен пользователю {sender_id}")
    else:
        # Больше 2 раз одному и тому же человеку не отвечаем
        pass

# --- 2. РАССЫЛКА ПО ЧАТАМ (с паузой 45 секунд) ---
# Чтобы запустить рассылку, отправьте команду: .рассылка в свои "Избранное"
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.рассылка'))
async def run_broadcast(event):
    await event.edit("🚀 Начинаю рассылку по чатам (с безопасными паузами)...")
    success_count = 0
    
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            try:
                await client.send_message(dialog.id, BROADCAST_TEXT)
                success_count += 1
                print(f"Отправлено в чат: {dialog.title}")
                # Пауза 45 секунд между сообщениями в группы
                await asyncio.sleep(45) 
            except Exception as e:
                print(f"Ошибка отправки в {dialog.title}: {e}")
                
    await client.send_message('me', f"✅ Рассылка окончена! Отправлено в {success_count} чатов.")

print("Бот запущен и работает с повышенной безопасностью...")
client.start()
client.run_until_disconnected()
