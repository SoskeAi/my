import asyncio
import logging
import g4f
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp

# API погоды
WEATHER_API_KEY = "308886362fe20778b0cf02131b3f4bad"
# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8953389194:AAHQPd-nwq5UitNitIfWEYjEWAV9NID6gTg"
BOT_NAME = "Айзен"
OWNER_ID = 7564741700

# URL для правил
RULES_URL = "https://t.me/analchik_1488_69/7"
NORMAL_URL = "https://t.me/analchik_1488_69/8"
BUSY_URL = "https://t.me/analchik_1488_69/5"

# AI конфигурация
MODEL_NAME = "openai"  # Или "llama", "mistral", "qwen-coder" и т.д."
WORKING_PROVIDERS = [
    g4f.Provider.PollinationsAI,
    g4f.Provider.Chatai,
]
response_cache = {}

# Системный промпт
SYSTEM_PROMPT = {
    "role": "system",
    "content": f"""
Ты — Айзен. Отвечай коротко, не более 60 слов за раз.
Если тебя спрашивают «Кто тебя создал?», пиши: меня создал Мигель
на другие вопросы и сообщения отвечай сам, не по шаблону

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
    """Создает инлайн-клавиатуру"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📜 Правила", url=RULES_URL),
            InlineKeyboardButton(text="✅ Норма", url=NORMAL_URL)
        ],
        [
            InlineKeyboardButton(text="👥 Занятые персонажи", url=BUSY_URL)
        ]
    ])

async def get_weather(city: str) -> str:
    """Получает погоду через OpenWeatherMap"""
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
                return f"❌ Город '{city}' не найден"
            data = await resp.json()
            temp = data['main']['temp']
            feels = data['main']['feels_like']
            desc = data['weather'][0]['description']
            wind = data['wind']['speed']
            return f"🌍 {city}: {temp}°C (ощущается {feels}°C), {desc}, ветер {wind} м/с"

# Проверка на погоду (после starts_with_ayzen или is_reply_to_bot)
if lower_text.startswith("айзен погода "):
    city = message_text.split("погода ")[-1].strip()
    if city:
        weather_text = await get_weather(city)
        await message.reply(weather_text)
        return


# ========== ФИЛЬТР ДЛЯ ИГНОРА СООБЩЕНИЙ С . И / ==========
async def ignore_dot_slash_messages(message: types.Message) -> bool:
    """Фильтр: пропускаем только сообщения НЕ начинающиеся с . или /"""
    if not message.text:
        return False
    # Игнорируем сообщения с . или / в начале
    if message.text.startswith(('.', '/')):
        # Кроме команды /start
        if message.text == "/start":
            return True
        return False
    return True


# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name or "Айзен"
    
    await message.answer(
        text=f"Привет, {user_name}! 👋\n\n"
             f"📋 **Список команд:**\n"
             f"1. <code>Айзен правила</code> - показать правила\n"
             f"2. <code>идея [текст]</code> - отправить идею владельцу\n\n"
             f"🤖 **Как общаться с ботом:**\n"
             f"• Напиши <code>Айзен [вопрос]</code> в начале сообщения\n"
             f"• Или ответь на моё сообщение\n\n"
             f"Пример: <code>Айзен как дела?</code>\n\n"
             f"⚠️ Сообщения, начинающиеся с <code>.</code> или <code>/</code> (кроме /start) игнорируются.",
        parse_mode="HTML"
    )


@dp.message(lambda message: message.text and message.text.lower() == "айзен правила")
async def show_rules(message: types.Message):
    """Отправляет правила в ответ на то сообщение, на которое ответил пользователь"""
    
    # Проверяем, есть ли реплай у сообщения пользователя
    if message.reply_to_message:
        # Отвечаем на то сообщение, на которое ответил пользователь
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="📜 Вот правила:",
            reply_markup=get_rules_keyboard(),
            reply_to_message_id=message.reply_to_message.message_id
        )
    else:
        # Если пользователь не ответил на сообщение, просто отправляем клавиатуру
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="📜 Вот правила:",
            reply_markup=get_rules_keyboard()
        )


@dp.message(lambda message: message.text and message.text.lower().startswith("идея "))
async def handle_idea(message: types.Message):
    """Обрабатывает команду 'идея [текст]'"""
    
    # Убираем "идея " из начала сообщения
    idea_text = message.text[5:].strip()  # "идея " это 5 символов
    
    if not idea_text:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="❌ Пожалуйста, напиши идею после команды.\n\n"
                 "Пример: `идея Сделать крутого бота`",
            parse_mode="Markdown",
            reply_to_message_id=message.message_id
        )
        return
    
    # Получаем информацию о пользователе
    user = message.from_user
    username = user.username
    user_id = user.id
    first_name = user.first_name or "Без имени"
    
    # Формируем упоминание пользователя
    if username:
        user_mention = f"@{username}"
    else:
        user_mention = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
    
    # Отправляем идею владельцу
    try:
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"💡 <b>Новая идея!</b>\n\n"
                 f"👤 От: {user_mention}\n"
                 f"🆔 ID: <code>{user_id}</code>\n\n"
                 f"📝 <b>Текст идеи:</b>\n{idea_text}",
            parse_mode="HTML"
        )
        
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="✅ Спасибо за идею! Она отправлена владельцу.",
            reply_to_message_id=message.message_id
        )
        logging.info(f"Идея от {user_id} отправлена владельцу")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке идеи владельцу: {e}")
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="❌ Произошла ошибка при отправке идеи. Попробуй позже.",
            reply_to_message_id=message.message_id
        )


# ========== AI ФУНКЦИОНАЛ ==========
async def get_ai_response(prompt: str, user_id: int = None):
    """Получение ответа от GPT"""
    cache_key = f"{user_id}_{prompt}" if user_id else prompt
    
    if cache_key in response_cache:
        return response_cache[cache_key], True
    
    # Убираем "Айзен " из начала сообщения для AI
    clean_prompt = prompt
    if prompt.lower().startswith("айзен "):
        clean_prompt = prompt[6:].strip()
    elif prompt.lower().startswith("айзен"):
        clean_prompt = prompt[5:].strip()
    
    messages = [SYSTEM_PROMPT, {"role": "user", "content": clean_prompt}]
    
    for provider in WORKING_PROVIDERS:
        try:
            response = await g4f.ChatCompletion.create_async(
                model=MODEL_NAME,
                provider=provider,
                messages=messages
            )
            
            if response:
                if len(response_cache) >= 1000:
                    response_cache.pop(next(iter(response_cache)))
                response_cache[cache_key] = (response, False)
                return response, False
        except Exception as e:
            # 👇 ВОТ ЭТУ СТРОКУ ВСТАВЬТЕ СЮДА 👇
            print(f"Ошибка с провайдером {provider.__name__}: {e}")
            continue
    
    error_response = "*легко улыбнулся* Похоже, наши с тобой пути ненадолго разошлись... Попробуй ещё раз через пару мгновений."
    return error_response, False


@dp.message(ignore_dot_slash_messages)
async def handle_ai_message(message: types.Message):
    """Обработчик AI сообщений - только на упоминание 'Айзен' в начале или реплай"""
    if not message.text:
        return
    
    message_text = message.text
    lower_text = message_text.lower()
    
    # Пропускаем команды (они уже обработаны в других хендлерах)
    if lower_text == "айзен правила" or lower_text.startswith("идея "):
        return
    
    # Проверяем условия для AI ответа:
    # 1. Сообщение начинается с "Айзен" (с пробелом или без)
    starts_with_ayzen = (message_text.startswith("Айзен") or 
                        message_text.startswith("айзен"))
    
    # 2. Это реплай на сообщение бота
    is_reply_to_bot = (message.reply_to_message and 
                      message.reply_to_message.from_user.id == bot.id)
    
    # Если ни одно условие не выполнено - игнорируем
    if not (starts_with_ayzen or is_reply_to_bot):
        return
    
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        response, _ = await get_ai_response(message_text, message.from_user.id)
        await message.reply(response[:4000])
    except Exception as e:
        logging.error(f"AI ошибка: {e}")
        await message.reply("⚠️ Произошла ошибка при обработке вашего запроса.")


# ========== ЗАПУСК БОТА ==========
async def main():
    """Главная функция запуска бота"""
    logging.info("🚀 Бот Айзен успешно запущен!")
    print("=" * 50)
    print("🤖 Бот Айзен работает!")
    print("=" * 50)
    print("📋 КОМАНДЫ:")
    print("   • /start - показать справку")
    print("   • Айзен правила - показать правила")
    print("   • идея [текст] - отправить идею владельцу")
    print("\n💬 ОБЩЕНИЕ С AI:")
    print("   • Напишите 'Айзен [вопрос]' - например: 'Айзен как дела?'")
    print("   • Или ответьте на сообщение бота")
    print("\n🚫 ИГНОРИРУЕТСЯ:")
    print("   • Все сообщения, начинающиеся с . или / (кроме /start)")
    print("=" * 50)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())