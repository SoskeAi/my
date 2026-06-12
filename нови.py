import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Твой токен
TOKEN = "8722271550:AAEmZc6ONpmBAbMoDS1DU17TNL61X7vUu3c"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Функция, которая возвращает клавиатуру с двумя кнопками
def get_rules_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📜 Правила", url="https://t.me/analchik_1488_69/7"),
            InlineKeyboardButton(text="👤 Владелец", url="tg://user?id=7564741700")
        ]
    ])

# Обработка текстовой команды «Айзен правила» (регистронезависимо)
@dp.message(lambda message: message.text and message.text.lower() == "айзен правила")
async def aizen_rules(message: types.Message):
    user_name = message.from_user.first_name or "Друг"
    await message.answer(
        f"Даров, {user_name}!\nДержи правила:",
        reply_markup=get_rules_button()
    )

# Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())