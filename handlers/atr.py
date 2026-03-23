from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from utils.calculations import get_data, calc_atr

router = Router()


@router.callback_query(F.data == "atr")
async def atr(callback: CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ATR(14)", callback_data="atr_14")],
            [InlineKeyboardButton(text="ATR(21)", callback_data="atr_21")],
            [InlineKeyboardButton(text="ATR(30)", callback_data="atr_30")],
        ]
    )
    await callback.message.edit_text("Вывберите период ATR:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("atr_"))
async def atr_period_handler(callback: CallbackQuery):
    await callback.answer("Загрузка...")
    period = int(callback.data.split("_")[1])

    df = get_data("BTCUSDT")
    atr_c = calc_atr(df, period)
    atr_value = float(atr_c.dropna().iloc[-1])
    price = df[4].astype(float).iloc[-1]

    volatility_percent = (atr_value / price) * 100

    if volatility_percent < 2:
        signal = "НИЗКАЯ ВОЛАТИЛЬНОСТЬ"
        description = "Рынок спокойный, малые движения цены"
    elif volatility_percent < 4:
        signal = "СРЕДНЯЯ ВОЛАТИЛЬНОСТЬ"
        description = "Нормальные рыночные условия"
    else:
        signal = "ВЫСОКАЯ ВОЛАТИЛЬНОСТЬ"
        description = "Рынок нестабильный, большие движения цены"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
    )

    await callback.message.edit_text(
        f"BTC/USDT - Волатильность\n\n"
        f"Цена: ${price:,.2f}\n"
        f"ATR({period}): ${atr_value:,.2f}\n"
        f"{signal}\n"
        f"{description}",
        reply_markup=keyboard
    )
