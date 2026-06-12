import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== КОНФИГУРАЦИЯ ==========
TOKEN = "8722271550:AAEmZc6ONpmBAbMoDS1DU17TNL61X7vUu3c"
RULES_URL = "https://t.me/analchik_1488_69/7"
OWNER_ID = 7564741700

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = Bot(token=TOKEN)
dp = Dispatcher()


# ========== КЛАВИАТУРЫ ==========
def get_rules_keyboard() -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру с правилами и ссылкой на владельца"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📜 Правила", url=RULES_URL),
            InlineKeyboardButton(text="👤 Владелец", url=f"tg://user?id={OWNER_ID}")
        ]
    ])


# ========== ОБРАБОТЧИКИ СООБЩЕНИЙ ==========
@dp.message(lambda message: message.text and message.text.lower().startswith("айзен правила"))
async def show_rules(message: types.Message):
    """Отправляет пользователю правила и ссылку на владельца"""
    user_name = message.from_user.first_name or "Айзен"
    
    await message.answer(
        text=f"Даров, {user_name}! 👋\nДержи правила:",
        reply_markup=get_rules_keyboard()
    )


# ========== ЗАПУСК БОТА ==========
async def main():
    """Главная функция запуска бота"""
    logging.info("Бот успешно запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())