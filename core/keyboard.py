from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

reg_button = KeyboardButton("Зарегистрироваться")
reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
reg_keyboard.add(reg_button)

cancel_button = KeyboardButton("Отмена")
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add(cancel_button)

reg_callback = CallbackData("reg", "status", "chat_id", "full_name")


def inline(chat_id, full_name):
    confirm = InlineKeyboardButton(
        text="✅",
        callback_data=reg_callback.new(
            status="1", chat_id=chat_id, full_name=full_name
        ),
    )
    cancel = InlineKeyboardButton(
        text="❌",
        callback_data=reg_callback.new(
            status="0", chat_id=chat_id, full_name="-"
        ),
    )
    conf_inline = InlineKeyboardMarkup()
    conf_inline.insert(confirm).insert(cancel)
    return conf_inline
