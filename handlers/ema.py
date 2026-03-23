from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.calculations import get_data, calc_ema

router = Router()


@router.callback_query(F.data == "ema")
async def ema_start(callback: CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="EMA(20)", callback_data='ema_20')],
            [InlineKeyboardButton(text="EMA(50)", callback_data='ema_50')],
            [InlineKeyboardButton(text="EMA(200)", callback_data='ema_200')],
        ]
    )
    await callback.message.edit_text("Выберите период EMA:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("ema_"))
async def ema_period_handler(callback: CallbackQuery):
    await callback.answer("Загрузка...")
    print(callback.data)
    period = int(callback.data.split("_")[1])
    print(period)
    df = get_data("BTCUSDT")
    ema = calc_ema(df, period).iloc[-1]
    price = df['close'].iloc[-1]
    if price > ema:
        trend = "ЦЕНА ВЫШЕ EMA (Бычий тренд)"
    else:
        trend = "ЦЕНА НИЖЕ EMA (Медвежий тренд)"

    distance_percent = abs(price - ema) / ema * 100

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
    )
    await callback.message.edit_text(
        f"BTC/USDT\n"
        f"Цена: ${price:,.2f}\n"
        f"EMA({period}): ${ema:,.2f}\n"
        f"Расстояние: {distance_percent:.2f}%\n\n"
        f"{trend}",
        reply_markup=keyboard
    )

