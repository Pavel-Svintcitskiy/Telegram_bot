from aiogram.fsm.state import State, StatesGroup


class PositionCalc(StatesGroup):
    account_size = State()
    risk_percent = State()
    entry_price = State()
    stop_loss = State()
    take_profit = State()
