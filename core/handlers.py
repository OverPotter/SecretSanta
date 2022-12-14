import json
import re

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ContentTypes, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from core.dispatcher import dp, bot
from config import users, admin_id, admin_chat_id
import core.keyboard as kb
from core.FSM_state import RegistrationStage


@dp.message_handler(commands=["start", "go"])
async def welcome(message: Message):
    await bot.send_message(
        message.chat.id,
        f"<b>Добро пожаловать, {message.from_user.username}!</b>\n\n"
        f"Чтобы пройти регистрацию, нажмите на кнопку <b>Зарегистрироваться</b>.",
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
        f"Пример: Айзек Азимов",
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
    await bot.send_message(
        message.chat.id,
        "✅ Запись о <u><b>ФИО</b></u> успешно внесена!\n",
        reply_markup=kb.cancel_keyboard
    )
    await RegistrationStage.next()


@dp.message_handler(state=RegistrationStage.registration_end, content_types=ContentTypes.TEXT)
async def confirmation(message: Message, state: FSMContext):
    await bot.send_message(
        message.chat.id,
        "✅ Запись!\n",
        reply_markup=kb.cancel_keyboard
    )

    path_to_user_json = "Temp\\" + str(message.chat.id) + ".json"
    data = await state.get_data()

    with open(path_to_user_json, "w") as user_json:
        json.dump(data, user_json)

    await bot.send_message(message.chat.id, "✅ Анкета успешно заполнена, после проверки вы получите ответ.")
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
    print(call.message.message_id, "decl")
    await bot.edit_message_text(
        "Заявка отклонена.", admin_chat_id, call.message.message_id
    )
    await bot.send_message(int(callback_data.get("chat_id")), "Отказано.")


@dp.callback_query_handler(kb.reg_callback.filter(status="1"))
async def accept(call: CallbackQuery, callback_data: dict):
    path_to_user_json = "Temp\\" + str(callback_data.get("chat_id")) + ".json"
    await call.answer()
    print(call.message.message_id, "conf")
    await bot.edit_message_text(
        "Заявка одобрена.", admin_chat_id, call.message.message_id
    )
    await bot.send_message(
        int(callback_data.get("chat_id")), "Добро пожаловать в команду."
    )

    # os.remove(path_to_user_json)


@dp.message_handler(Command('sendall'))
async def send_all(message: Message):
    if message.chat.id == admin_id:
        await message.answer('Start')
        for i in users:
            await bot.send_message(i, message.text[message.text.find(' '):])

        await message.answer('Done')

    else:
        await message.answer('Error')


@dp.message_handler(Command('sendallwp'))
async def send_all(message: Message):
    if message.chat.id == admin_id:
        await message.answer('Start')
        for i in users:
            await bot.send_photo(i, open('../img/Santa.jpg', 'rb'), message.text[message.text.find(' '):])

        await message.answer('Done')

    else:
        await message.answer('You are not a God!')
