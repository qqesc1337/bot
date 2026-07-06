import asyncio
import os
import random
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Извлечение токена из переменных окружения Railway
TOKEN = os.getenv("BOT_TOKEN")

# Жесткая проверка: если токен забыли указать в Railway, бот сразу сообщит об этом в логи
if not TOKEN:
    print("ЭРРОР: Переменная окружения BOT_TOKEN не задана в настройках Railway!", file=sys.stderr)
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 11 криптовалютных пар для генерации сигналов
CRYPTO_PAIRS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
    "ADA/USDT", "DOT/USDT", "LINK/USDT", "AVAX/USDT", "MATIC/USDT", "TON/USDT"
]

def generate_signals_text() -> str:
    """Генерирует актуальные торговые сигналы для всех пар."""
    text = "📊 <b>Актуальные торговые сигналы:</b>\n\n"
    for pair in CRYPTO_PAIRS:
        position = random.choice(["🟢 LONG (Покупка)", "🔴 SHORT (Продажа)"])
        entry_price = round(random.uniform(0.5, 95000), 4)
        
        # Логичный расчет TP/SL в зависимости от направления сделки
        if "LONG" in position:
            tp = round(entry_price * 1.05, 4)
            sl = round(entry_price * 0.98, 4)
        else:
            tp = round(entry_price * 0.95, 4)
            sl = round(entry_price * 1.02, 4)
        
        text += (
            f"🔹 <b>{pair}</b>\n"
            f"Направление: {position}\n"
            f"Вход: <code>{entry_price}</code>\n"
            f"Take Profit: <code>{tp}</code>\n"
            f"Stop Loss: <code>{sl}</code>\n"
            f"-------------------------\n"
        )
    return text

def get_refresh_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой обновления."""
    buttons = [[InlineKeyboardButton(text="🔄 Обновить сигналы", callback_data="refresh_signals")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обрабатывает команду /start и отправляет первое сообщение с сигналами."""
    await message.answer(
        text=generate_signals_text(),
        parse_mode="HTML",
        reply_markup=get_refresh_keyboard()
    )

@dp.callback_query(lambda c: c.data == "refresh_signals")
async def process_refresh(callback_query: CallbackQuery):
    """Обновляет сигналы прямо в существующем сообщении без отправки нового."""
    await callback_query.message.edit_text(
        text=generate_signals_text(),
        parse_mode="HTML",
        reply_markup=get_refresh_keyboard()
    )
    # Обязательный ответ на callback, чтобы кнопка не «зависала» в режиме загрузки
    await callback_query.answer()

async def main():
    print("Бот успешно запущен и готов к работе...")
    # Предотвращает обработку старых сообщений, отправленных пока бот был оффлайн
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
