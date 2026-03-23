import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import rsi, position_calc, ema, atr, adx
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(rsi.router)
dp.include_router(position_calc.router)
dp.include_router(ema.router)
dp.include_router(atr.router)
dp.include_router(adx.router)


@dp.message(CommandStart())
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="RSI", callback_data="rsi")],
            [InlineKeyboardButton(text="Position Calculator", callback_data="calculator")],
            [InlineKeyboardButton(text="EMA", callback_data="ema")],
            [InlineKeyboardButton(text="ATR", callback_data="atr")],
            [InlineKeyboardButton(text="ADX", callback_data="adx")]
        ]
    )
    await message.answer(
        "Выберите торговый показатель:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="RSI", callback_data="rsi")],
            [InlineKeyboardButton(text="Position Calculator", callback_data="calculator")],
            [InlineKeyboardButton(text="EMA", callback_data="ema")],
            [InlineKeyboardButton(text="ATR", callback_data="atr")],
            [InlineKeyboardButton(text="ADX", callback_data="adx")]
        ]
    )
    await callback.message.edit_text("Выберите торговый показатель:", reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

