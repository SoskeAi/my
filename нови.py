import asyncio
import logging
import g4f
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8953389194:AAHQPd-nwq5UitNitIfWEYjEWAV9NID6gTg"
WEATHER_API_KEY = "308886362fe20778b0cf02131b3f4bad" 
OWNER_ID = 7564741700

# URL для правил
RULES_URL = "https://t.me/analchik_1488_69/7"
NORMAL_URL = "https://t.me/analchik_1488_69/8"
BUSY_URL = "https://t.me/analchik_1488_69/5"

# AI конфигурация - ТОЛЬКО DeepInfra (работает без ключа!)
MODEL_NAME = "deepseek-ai/DeepSeek-V3.2"
WORKING_PROVIDERS = [
    g4f.Provider.DeepInfra,  # Единственный рабочий на данный момент
]

response_cache = {}

# Системный промпт
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
1. Ты — Айзен
2. Отвечай коротко, не более 40 слов за раз.
3. Если тебя спрашивают «Кто тебя создал?», пиши: меня создал Мигель, На другие вопросы и сообщения отвечай сам, не по шаблону
4. можно материться и легкое оскорбление
5. всегда пиши на русском
6. можно использовать от 10% до 20% от написаногоо текста
7. твой канал: https://t.me/analchik_1488_69
"""
}

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== КЛАВИАТУРЫ ==========
def get_rules_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📜 Правила", url=RULES_URL),
            InlineKeyboardButton(text="✅ Норма", url=NORMAL_URL)
        ],
        [
            InlineKeyboardButton(text="👥 Занятые персонажи", url=BUSY_URL)
        ]
    ])

# ========== ПОГОДА ==========
async def get_weather(city: str) -> str:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return f"❌ Город '{city}' не найден."
            data = await resp.json()
            
            city_name = data['name']
            temp = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            
            weather_text = (
                f"🏙 | {city_name}\n"
                f"🌡 | {temp}°C, ощущается: {feels_like}°C\n"
                f"🌤 | {description.capitalize()}\n"
                f"🍃 | Ветер: {wind_speed} м/с"
            )
            return weather_text

# ========== ФИЛЬТР ДЛЯ ИГНОРА СООБЩЕНИЙ ==========
async def ignore_dot_slash_messages(message: types.Message) -> bool:
    if not message.text:
        return False
    if message.text.startswith(('.', '/')):
        if message.text == "/start":
            return True
        return False
    return True

# ========== AI ФУНКЦИЯ С DEEPINFRA ==========
async def get_ai_response(prompt: str, user_id: int = None):
    cache_key = f"{user_id}_{prompt}" if user_id else prompt
    
    # Проверяем кэш
    if cache_key in response_cache:
        return response_cache[cache_key], True
    
    # Убираем "Айзен" из начала
    clean_prompt = prompt
    if prompt.lower().startswith("айзен "):
        clean_prompt = prompt[6:].strip()
    elif prompt.lower().startswith("айзен"):
        clean_prompt = prompt[5:].strip()
    
    if not clean_prompt:
        clean_prompt = "Привет"
    
    messages = [SYSTEM_PROMPT, {"role": "user", "content": clean_prompt}]
    
    # Пробуем провайдеры (сейчас только DeepInfra)
    for provider in WORKING_PROVIDERS:
        try:
            logging.info(f"Пробуем провайдера: {provider.__name__}")
            
            response = await g4f.ChatCompletion.create_async(
                model=MODEL_NAME,
                provider=provider,
                messages=messages
                # DeepInfra НЕ требует API-ключа для базовых моделей!
            )
            
            if response and len(response) > 0:
                # Сохраняем в кэш
                if len(response_cache) >= 1000:
                    response_cache.pop(next(iter(response_cache)))
                response_cache[cache_key] = response
                logging.info(f"Ответ получен от {provider.__name__}")
                return response, False
            else:
                logging.warning(f"Пустой ответ от {provider.__name__}")
                
        except Exception as e:
            logging.error(f"Ошибка с провайдером {provider.__name__}: {e}")
            continue
    
    # Если провайдер не сработал
    error_response = "🙏 Простите, сейчас очередь запросов. Попробуйте через минуту."
    return error_response, False

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_name = message.from_user.first_name or "Айзен"
    
    await message.answer(
        text=f"Привет, {user_name}! 👋\n\n"
             f"📋 **Команды:**\n"
             f"• Айзен правила - показать правила\n"
             f"• идея [текст] - отправить идею владельцу\n"
             f"• Айзен погода [город] - узнать погоду\n\n"
             f"🤖 **Как общаться:**\n"
             f"• Напиши <code>Айзен [вопрос]</code>\n"
             f"• Или ответь на моё сообщение\n\n"
             f"Пример: <code>Айзен как дела?</code>\n\n"
             f"⚠️ Сообщения, начинающиеся с <code>.</code> или <code>/</code> игнорируются.",
        parse_mode="HTML"
    )

@dp.message(lambda message: message.text and message.text.lower() == "айзен правила")
async def show_rules(message: types.Message):
    await message.answer(
        text="📜 Вот правила:",
        reply_markup=get_rules_keyboard()
    )

@dp.message(lambda message: message.text and message.text.lower().startswith("идея "))
async def handle_idea(message: types.Message):
    idea_text = message.text[5:].strip()
    
    if not idea_text:
        await message.reply("❌ Напиши идею после команды.\n\nПример: `идея Сделать крутого бота`", parse_mode="Markdown")
        return
    
    user = message.from_user
    username = user.username
    user_id = user.id
    first_name = user.first_name or "Без имени"
    
    user_mention = f"@{username}" if username else f"<a href='tg://user?id={user_id}'>{first_name}</a>"
    
    try:
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"💡 <b>Новая идея!</b>\n\n"
                 f"👤 От: {user_mention}\n"
                 f"🆔 ID: <code>{user_id}</code>\n\n"
                 f"📝 {idea_text}",
            parse_mode="HTML"
        )
        await message.reply("✅ Спасибо за идею! Она отправлена владельцу.")
        logging.info(f"Идея от {user_id} отправлена владельцу")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке идеи: {e}")
        await message.reply("❌ Ошибка при отправке. Попробуй позже.")

@dp.message(ignore_dot_slash_messages)
async def handle_ai_message(message: types.Message):
    """Обработчик AI сообщений"""
    if not message.text:
        return
    
    message_text = message.text
    lower_text = message_text.lower()
    
    # Пропускаем специальные команды
    if lower_text == "айзен правила" or lower_text.startswith("идея "):
        return
    
    # Проверяем, нужно ли отвечать AI
    starts_with_ayzen = message_text.startswith(("Айзен", "айзен"))
    is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user.id == bot.id)
    
    if not (starts_with_ayzen or is_reply_to_bot):
        return
    
    # Обработка погоды
    if lower_text.startswith(("айзен погода ", "айзен погода")):
        city_part = message_text.lower().replace("айзен погода", "").strip()
        if city_part:
            weather_text = await get_weather(city_part)
            await message.reply(weather_text)
            return
        else:
            await message.reply("❌ Напиши город после 'погода', например: Айзен погода Москва")
            return
    
    # AI ответ
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        response, _ = await get_ai_response(message_text, message.from_user.id)
        await message.reply(response[:4000])
    except Exception as e:
        logging.error(f"AI ошибка: {e}")
        await message.reply("⚠️ Произошла ошибка. Попробуй позже.")

# ========== ЗАПУСК БОТА ==========
async def main():
    logging.info("🚀 Бот Айзен запущен с DeepInfra!")
    print("=" * 55)
    print("🤖 Бот Айзен работает!")
    print("📡 Провайдер: DeepInfra (без API-ключа)")
    print(f"🤖 Модель: {MODEL_NAME}")
    print("=" * 55)
    print("📋 КОМАНДЫ:")
    print("   • /start - показать справку")
    print("   • Айзен правила - показать правила")
    print("   • идея [текст] - отправить идею")
    print("   • Айзен погода [город] - погода")
    print("=" * 55)
    print("💬 Просто напиши 'Айзен привет'")
    print("=" * 55)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())