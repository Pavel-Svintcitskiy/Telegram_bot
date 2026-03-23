
from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from utils.calculations import get_data, calc_rsi

router = Router()


@router.callback_query(F.data == "rsi")
async def rsi_handler(callback: CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="RSI(14)", callback_data="rsi_14")],
            [InlineKeyboardButton(text="RSI(21)", callback_data="rsi_21")],
            [InlineKeyboardButton(text="RSI(30)", callback_data="rsi_30")],
        ]
    )
    await callback.message.edit_text("Выберите период RSI:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rsi_"))
async def rsi_period_handler(callback: CallbackQuery):
    await callback.answer("Секунду...")
    period = int(callback.data.split("_")[1])
    df = get_data("BTCUSDT")
    rsi = calc_rsi(df, period).iloc[-1]
    price = df['close'].iloc[-1]
    signal = "ПЕРЕКУПЛЕННОСТЬ" if rsi >= 70 else "ПЕРЕПРОДАННОСТЬ" if rsi <= 30 else "НЕЙТРАЛЬНО"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
    )

    await callback.message.edit_text(
        f"BTC/USDT\n ${price:,.2f}\n RSI({period}): {rsi:.2f}\n\n{signal}",
        reply_markup=keyboard
    )
