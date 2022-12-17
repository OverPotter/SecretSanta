import re

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ContentTypes, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from core.dispatcher import dp, bot
from config import admin_id, admin_chat_id, IMG_PATH
from core.FSM_state import RegistrationStage
from core.json_handler import JsonHandler
import core.keyboard as kb


Santa_support = JsonHandler()


@dp.message_handler(commands=["start", "go"])
async def welcome(message: Message):
    await bot.send_message(
        message.chat.id,
        f"<b>С наступающим Новым Годом, {message.from_user.username}!</b>\n\n"
        f"Чтобы принять участие в секретном Санте, нажмите на кнопку <b>Зарегистрироваться</b>.",
        reply_markup=kb.reg_keyboard,
    )


@dp.message_handler(Text(equals="Отмена"), state="*")
async def menu_button(message: Message, state: FSMContext):
    await state.finish()
    await bot.send_message(
        message.chat.id, "Регистрация отменена.", reply_markup=kb.reg_keyboard
    )


@dp.message_handler(Text(equals="Зарегистрироваться"), state="*")
async def registration_start(message: Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        f"Привет {message.from_user.first_name}, "
        f"пожалуйста ввидите ваше имя и фамилию.\n"
        f"Пример: Isaac Asimov",
        reply_markup=kb.cancel_keyboard
    )
    await RegistrationStage.waiting_user_fullname.set()


@dp.message_handler(state=RegistrationStage.waiting_user_fullname, content_types=ContentTypes.TEXT)
async def check_fullname(message: Message, state: FSMContext):
    error_symbols = re.findall(r"[^A-Za-z\sа-яА-ЯёЁ-]", message.text)
    full_name_length = len(message.text.split())
    if error_symbols or full_name_length < 2:
        await message.answer("❌ Пожалуйста, введите кооректные данные.")
        return

    await state.update_data(full_name=message.text.encode("utf-8").decode("utf-8"))
    await state.update_data(chat_id=message.chat.id)
    await confirmation(message, state)


async def confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    Santa_support.write_json(data)

    await bot.send_message(message.chat.id, "✅ Ваш запрос отправлен, после проверки вы получите ответ.")
    await bot.send_message(
        admin_chat_id,
        f"Поступила заявка от @{message.from_user.username}\n\n"
        f'Имя: {data.get("full_name")}\n',
        reply_markup=kb.inline(
            f"{message.chat.id}",
            f'{data.get("full_name")}',
        ),
    )
    await state.finish()


@dp.callback_query_handler(kb.reg_callback.filter(status="0"))
async def decline(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await bot.edit_message_text(
        "Заявка отклонена.", admin_chat_id, call.message.message_id
    )
    await bot.send_message(int(callback_data.get("chat_id")), "Отказано.")


@dp.callback_query_handler(kb.reg_callback.filter(status="1"))
async def accept(call: CallbackQuery, callback_data: dict):
    await call.answer()
    await bot.edit_message_text(
        "Заявка одобрена.",
        admin_chat_id, call.message.message_id
    )
    await bot.send_message(
        int(callback_data.get("chat_id")), "Ваша заявка на участие принята."
                                           "\nКак только собирутся все участники, "
                                           "вы узнаете кого вам предстоит осчастливить)"
    )


@dp.message_handler(Command('sendallwp'))
async def send_all(message: Message):
    if message.chat.id == admin_id:
        await message.answer('Start')
        Santa_support.users_list = Santa_support.get_users_list()
        for user in Santa_support.get_users_list():
            Santa_support.secret_Santa(user)
        for secret in Santa_support.secret_Santa_list:
            for user_id, secret_message in secret.items():
                await bot.send_photo(user_id, open(IMG_PATH, 'rb'), secret_message)

        await message.answer('Done')

    else:
        await message.answer('You are not a God!')


@dp.message_handler(Command('getusers'))
async def get_users(message: Message):
    if message.chat.id == admin_id:
        users = Santa_support.get_users_list()
        result = [user['full_name'] for user in users]
        await bot.send_message(admin_id, '\n'.join(result))
