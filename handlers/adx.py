from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from utils.calculations import get_data, calc_adx
router = Router()


@router.callback_query(F.data == "adx")
async def adx_handler(callback: CallbackQuery):
    await callback.answer()
    keyword = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ADX(14)", callback_data="adx_14")],
            [InlineKeyboardButton(text="ADX(21)", callback_data="adx_21")],
            [InlineKeyboardButton(text="ADX(30)", callback_data="adx_30")],
        ]
    )
    await callback.message.edit_text("Выберите период ADX:", reply_markup=keyword)


@router.callback_query(F.data.startswith("adx_"))
async def adx_period_handler(callback: CallbackQuery):
    await callback.answer("Загрузка...")
    period = int(callback.data.split("_")[1])

    df = get_data("BTCUSDT")
    adx, plus_di, minus_di = calc_adx(df, period)

    adx_value = adx.iloc[-1]
    price = df[4].astype(float).iloc[-1]

    if adx_value < 20:
        trend_strength = "СЛАБЫЙ ТРЕНД"
        description = "Рынок в боковике, нет четкого направления"
    elif adx_value < 25:
        trend_strength = "РАЗВИВАЮЩИЙСЯ ТРЕНД"
        description = "Тренд начинает формироваться"
    elif adx_value < 50:
        trend_strength = "СИЛЬНЫЙ ТРЕНД"
        description = "Четкое трендовое движение"
    else:
        trend_strength = "ОЧЕНЬ СИЛЬНЫЙ ТРЕНД"
        description = "Экстремально сильный тренд, возможна коррекция"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
    )

    await callback.message.edit_text(
        f"BTC/USDT - Сила тренда (ADX)\n\n"
        f"Цена: ${price:,.2f}\n\n"
        f"ADX({period}): {adx_value:.2f}\n"
        f"{trend_strength}\n"
        f"{description}\n\n"
        f"Интерпретация:\n"
        f"ADX < 20 = Слабый тренд\n"
        f"ADX 20-25 = Развивающийся\n"
        f"ADX 25-50 = Сильный тренд\n",
        reply_markup=keyboard
    )
