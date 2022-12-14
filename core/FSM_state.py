from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationStage(StatesGroup):
    waiting_user_fullname = State()
    registration_end = State()
