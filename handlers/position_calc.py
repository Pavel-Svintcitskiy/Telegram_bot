from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from states.position_calculator import  PositionCalc


router = Router()


@router.callback_query(F.data == "calculator")
async def calculator_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        " Position Calculator\n\n"
        "Введите размер вашего счета (в USD):\n"
        "Например: 10000"
    )
    await state.set_state(PositionCalc.account_size)


@router.message(PositionCalc.account_size)
async def process_account_size(message: Message, state: FSMContext):
    try:
        account_size = float(message.text)
        if account_size <= 0:
            await message.answer("Размер счета должен быть больше 0. Попробуйте еще раз:")
            return

        await state.update_data(account_size=account_size)
        await message.answer(
            f"Размер счета: ${account_size:,.2f}\n\n"
            "Введите риск на сделку (в %):\n"
            "Например: 2"
        )
        await state.set_state(PositionCalc.risk_percent)
    except ValueError:
        await message.answer("Неверный формат. Введите число, например: 10000")


@router.message(PositionCalc.risk_percent)
async def process_risk_percent(message: Message, state: FSMContext):
    try:
        risk_percent = float(message.text)
        if risk_percent <= 0 or risk_percent > 100:
            await message.answer("Риск должен быть от 0 до 100%. Попробуйте еще раз:")
            return

        await state.update_data(risk_percent=risk_percent)
        data = await state.get_data()
        risk_amount = data['account_size'] * (risk_percent / 100)

        await message.answer(
            f"Риск: {risk_percent}% (${risk_amount:,.2f})\n\n"
            "Введите цену входа:\n"
            "Например: 50000"
        )
        await state.set_state(PositionCalc.entry_price)
    except ValueError:
        await message.answer("Неверный формат. Введите число, например: 2")


@router.message(PositionCalc.entry_price)
async def process_entry_price(message: Message, state: FSMContext):
    try:
        entry_price = float(message.text)
        if entry_price <= 0:
            await message.answer("Цена должна быть больше 0. Попробуйте еще раз:")
            return

        await state.update_data(entry_price=entry_price)
        await message.answer(
            f"Цена входа: ${entry_price:,.2f}\n\n"
            "Введите стоп-лосс:\n"
            "Например: 48000"
        )
        await state.set_state(PositionCalc.stop_loss)
    except ValueError:
        await message.answer("Неверный формат. Введите число, например: 50000")


@router.message(PositionCalc.stop_loss)
async def process_stop_loss(message: Message, state: FSMContext):
    try:
        stop_loss = float(message.text)
        if stop_loss <= 0:
            await message.answer("Стоп-лосс должен быть больше 0. Попробуйте еще раз:")
            return

        await state.update_data(stop_loss=stop_loss)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_tp")],
            ]
        )

        await message.answer(
            f"Стоп-лосс: ${stop_loss:,.2f}\n\n"
            "Введите тейк-профит (или нажмите 'Пропустить'):\n"
            "Например: 55000",
            reply_markup=keyboard
        )
        await state.set_state(PositionCalc.take_profit)
    except ValueError:
        await message.answer("Неверный формат. Введите число, например: 48000")


@router.callback_query(F.data == "skip_tp", PositionCalc.take_profit)
async def skip_take_profit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await calculate_and_show(callback.message, state, take_profit=0)


@router.message(PositionCalc.take_profit)
async def process_take_profit(message: Message, state: FSMContext):
    try:
        take_profit = float(message.text)
        if take_profit < 0:
            await message.answer("Тейк-профит не может быть отрицательным. Попробуйте еще раз:")
            return

        await calculate_and_show(message, state, take_profit)
    except ValueError:
        await message.answer("Неверный формат. Введите число, например: 55000")


async def calculate_and_show(message: Message, state: FSMContext, take_profit: float):
    data = await state.get_data()

    account_size = data['account_size']
    risk_percent = data['risk_percent']
    entry_price = data['entry_price']
    stop_loss = data['stop_loss']

    # Расчеты
    risk_amount = account_size * (risk_percent / 100)
    distance = abs(entry_price - stop_loss)
    distance_percent = (distance / entry_price) * 100

    position_size = risk_amount / (distance_percent / 100)
    quantity = position_size / entry_price

    result = f"""
        РЕЗУЛЬТАТ:
        - Размер позиции: ${position_size:,.2f}
        - Количество: {quantity:.6f}
        - Макс. убыток: ${risk_amount:,.2f}
            """

    if take_profit > 0:
        profit = quantity * abs(take_profit - entry_price)
        rr_ratio = profit / risk_amount

        result += f"""
        ЦЕЛЬ:
        - Тейк-профит: ${take_profit:,.2f}
        - Прибыль: ${profit:,.2f}
        - Risk/Reward: 1:{rr_ratio:.2f}
        """

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Новый расчет", callback_data="calculator")],
            [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")],
        ]
    )

    await message.answer(result, reply_markup=keyboard)
    await state.clear()
