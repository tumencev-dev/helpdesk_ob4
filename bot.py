import asyncio
import logging
import sys
from database import Database as db
from datetime import datetime, timedelta, date

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



TOKEN = '7994013311:AAFdbCZ5FWYfYV8WO7G4NEh5H522QOjOfAQ'
new_task_data = []
edit_task_list = []
delete_task_choice_id = 0
ready_task_choice_id = 0
add_comment_task_id = 0
open_task = 0

dp = Dispatcher()


def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        today = datetime.today()
        yesterday = today + timedelta(days=-1)
        deadline_date = datetime.strptime(date_text, '%Y-%m-%d')
        valid_date_range = yesterday <= deadline_date <= datetime(2030, 12, 31, 23, 59, 59)
        return valid_date_range
    except ValueError:
        return False

def task_card(element):
    task_card = (
                f"📌 <b>ЗАДАЧА №{element[0]}</b>\n\n"
                f"<b>{element[1]}</b>\n\n"
                "──────────────────────────────\n"
                f"⏳ <b>Срок выполнения:</b> {element[4].strftime("%d.%m.%Y")}\n"
                f"👤 <b>Автор:</b> {element[2]}\n"
                f"🚪 <b>Кабинет:</b> {element[3]}\n"
                f"🔔 <b>Напоминание:</b> {element[6].strftime("%d.%m.%Y %H:%M") if element[6] else 'Нет'}\n\n"
                f"💬 <b>Комментарии:</b>\n<blockquote>{element[5] or 'Пока нет комментариев'}</blockquote>"
            )
    return task_card


class NewTicket(StatesGroup):
    input_description_ticket = State()
    input_deadlinedate_ticket = State()
    input_reminder_ticket = State()
    input_reminder_date_ticket = State()

class DelTicket(StatesGroup):
    delete_ticket_id = State()
    delete_ticket_confirmation = State()

class ReadyTicket(StatesGroup):
    ready_ticket_id = State()
    ready_ticket_confirmation = State()

class OpenTicket(StatesGroup):
    open_ticket_id = State()
    
class AddCommentTicket(StatesGroup):
    add_comment_ticket = State()


builder = InlineKeyboardBuilder()
builder.add(InlineKeyboardButton(text="Новая задача 📄", callback_data="set_task"))
builder.add(InlineKeyboardButton(text="Получить список 🗂", callback_data="get_task"))
builder.add(InlineKeyboardButton(text="Открыть задачу 📋", callback_data="open_task"))
builder.add(InlineKeyboardButton(text="Удалить задачу 🗑", callback_data="del_task")),
builder.add(InlineKeyboardButton(text="Пометить как выполненное ✅", callback_data="ready_task"))
builder.adjust(2)


button_yes = KeyboardButton(text='Да')
button_no = KeyboardButton(text='Нет')
choice_kb = ReplyKeyboardMarkup(keyboard=[[button_yes], [button_no]], resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print(message.chat.id)
    welcome_text = (
        f"✨ <b>Добро пожаловать, {html.quote(message.from_user.full_name)}!</b> ✨\n"
        "──────────────────────────────\n"
        "Я ваш персональный помощник по управлению задачами!\n\n"
        "Выберите действие:"
    )
    await message.answer(welcome_text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "set_task")
async def new_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    global new_task_data
    new_task_data = []
    await callback_query.message.answer(
        "<b>Шаг 1/3</b>\n"
        "──────────────────────────────\n"
        "✏️ Введите описание вашей проблемы:")
    await state.set_state(NewTicket.input_description_ticket)

@dp.message(NewTicket.input_description_ticket)
async def new_task_description(message: Message, state: FSMContext):
    global new_task_data
    today = str(date.today())
    tomorrow = str(date.today() + timedelta(days=1))
    button_today = KeyboardButton(text=today)
    button_tomorrow = KeyboardButton(text=tomorrow)
    days_kb = ReplyKeyboardMarkup(keyboard=[[button_today], [button_tomorrow]], resize_keyboard=True)
    new_task_data.append(message.text)
    await message.answer(
        "<b>Шаг 2/3</b>\n"
        "──────────────────────────────\n"
        "📆 Введите дату крайнего срока в соответствии с форматом - ГГГГ-ММ-ДД:", reply_markup=days_kb)
    await state.set_state(NewTicket.input_deadlinedate_ticket)

@dp.message(NewTicket.input_deadlinedate_ticket)
async def new_task_deadlinedate(message: Message, state: FSMContext):
    global new_task_data
    deadline_text = message.text
    if is_valid_date(deadline_text):
        new_task_data.append(message.text)
        await message.answer(
            "<b>Шаг 3/3</b>\n"
            "──────────────────────────────\n"
            "🔔 Хотите добавить напоминание для этой задачи?", reply_markup=choice_kb)
        await state.set_state(NewTicket.input_reminder_ticket)
    else:
        await message.answer(
            '❌ Неверный формат даты\n'
            "──────────────────────────────\n"
            '📆 Введите дату крайнего срока в формате: ГГГГ-ММ-ДД\n'
            '(с сегодняшнего дня, до 31 января 2030 года)')
        await state.set_state(NewTicket.input_deadlinedate_ticket)

@dp.message(NewTicket.input_reminder_ticket)
async def new_task_reminder(message: Message, state: FSMContext):
    global new_task_data
    if message.text == 'Да':
        await message.answer(
            '⏳ Введите время для напоминания в формате ЧЧ-ММ:', reply_markup=ReplyKeyboardRemove())
        await state.set_state(NewTicket.input_reminder_date_ticket)
    elif message.text == 'Нет':
        db.set_task([
                        new_task_data[0],
                        'Telegram Bot',
                        '',
                        new_task_data[1],
                        '',
                        False,
                        None
                        ])
        await message.answer('Новая задача добавлена ✅', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())

@dp.message(NewTicket.input_reminder_date_ticket)
async def new_task_reminder_date(message: Message, state: FSMContext):
    global new_task_data
    time = message.text
    date_time = str(new_task_data[1]) + time
    reminder_datetime = datetime.strptime(date_time, "%Y-%m-%d%H-%M")
    new_task_data.append(reminder_datetime)
    db.set_task([
                    new_task_data[0],
                    'Telegram Bot',
                    '',
                    new_task_data[1],
                    '',
                    True,
                    new_task_data[2]
                ])
    await message.answer(f'Установлено напоминание - {reminder_datetime.strftime("%d.%m.%Y %H:%M")}')
    await message.answer('✅ Новая задача добавлена')
    await state.clear()
    await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())


@dp.callback_query(F.data == "get_task")
async def get_task_list(callback_query: CallbackQuery) -> None:
    global edit_task_list
    today = date.today()
    tomorrow = today + timedelta(days=1)
    output_list = []
    edit_task_list = []
    num = 1
    task_list = db.get_tasks(False, "date")
    for task in task_list:
        if task[4] <= tomorrow:
            output_list.append([num, task[1], task[4], task[8], task[9]])
            edit_task_list.append([num, task[1], task[2], task[3], task[4], task[5], task[9], task[0]])
            num += 1
    await callback_query.message.answer('<b>ЗАДАЧИ НА СЕГОДНЯ, ЗАВТРА:</b>')
    for element in output_list:
        status_icon = "⏰" if element[4] else ' ─'
        task_text = (
            f"📌  <b>Задача №{element[0]}</b>                                                    {status_icon}\n"
            f"<blockquote>{element[1]}</blockquote>\n"
            f"📅  <i>Срок:</i> {element[2].strftime("%d.%m.%Y")}"
        )
        await callback_query.message.answer(task_text)
    await callback_query.message.answer('Это все задачи на сегодня 🫣', reply_markup=builder.as_markup())


@dp.callback_query(F.data == "del_task")
async def delete_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer("Введите номер задачи для удаления:")
    await state.set_state(DelTicket.delete_ticket_id)

@dp.message(DelTicket.delete_ticket_id)
async def delete_task_id(message: Message, state: FSMContext):
    global delete_task_choice_id
    global edit_task_list
    num_task = int(message.text)
    for element in edit_task_list:
        if num_task == element[0]:
            delete_task_choice_id = element[7]
            await message.answer(f"⚠️ Вы действительно хотите удалить задачу?\n<b>{element[1]}</b>", reply_markup=choice_kb)
            await state.set_state(DelTicket.delete_ticket_confirmation)

@dp.message(DelTicket.delete_ticket_confirmation)
async def delete_task_sucess(message: Message, state: FSMContext):
    global delete_task_choice_id
    if message.text == 'Да':
        db.delete_task(delete_task_choice_id)
        await message.answer('✅ Данная задача удалена', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())
    if message.text == 'Нет':
        await message.answer('🛑 Действие отменено', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())


@dp.callback_query(F.data == "ready_task")
async def ready_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer("Введите номер задачи которую нужно пометить как выполненную:")
    await state.set_state(ReadyTicket.ready_ticket_id)

@dp.message(ReadyTicket.ready_ticket_id)
async def ready_task_id(message: Message, state: FSMContext):
    global ready_task_choice_id
    global edit_task_list
    num_task = int(message.text)
    for element in edit_task_list:
        if num_task == element[0]:
            ready_task_choice_id = element[7]
            await message.answer(f"⚠️ Вы действительно хотите завершить задачу?\n<b>{element[1]}</b>", reply_markup=choice_kb)
            await state.set_state(ReadyTicket.ready_ticket_confirmation)

@dp.message(ReadyTicket.ready_ticket_confirmation)
async def ready_task_sucess(message: Message, state: FSMContext):
    global ready_task_choice_id
    if message.text == 'Да':
        db.set_status_ready(ready_task_choice_id)
        await message.answer('✅ Задача выполнена', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())
    if message.text == 'Нет':
        await message.answer('🛑 Действие отменено', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())


@dp.callback_query(F.data == "open_task")
async def open_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer("Введите номер задачи, которую вы хотите открыть:")
    await state.set_state(OpenTicket.open_ticket_id)

@dp.message(OpenTicket.open_ticket_id)
async def open_task_id(message: Message, state: FSMContext):
    global edit_task_list
    global add_comment_task_id
    global open_task
    num_task = int(message.text)
    open_task = num_task
    for element in edit_task_list:
        if num_task == element[0]:
            add_comment_task_id = element[7]
            # Создаем инлайн-кнопки
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="✏️ Добавить комментарий", callback_data="edit_task_comment"))
            builder.add(InlineKeyboardButton(text="❌ Закрыть", callback_data="close_task"))
            builder.adjust(1)
            # Отправляем сообщение с карточкой и кнопками
            await message.answer(task_card(element), parse_mode="HTML", reply_markup=builder.as_markup())
            await state.clear()

@dp.callback_query(F.data == "close_task")
async def close_task(callback_query: CallbackQuery) -> None:
    await callback_query.message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())

@dp.callback_query(F.data == "edit_task_comment")
async def add_comment_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer("Введите текст комментария для добавления:")
    await state.set_state(AddCommentTicket.add_comment_ticket)

@dp.message(AddCommentTicket.add_comment_ticket)
async def open_task_id(message: Message, state: FSMContext):
    global add_comment_task_id
    global edit_task_list #Нужно его обновить
    global open_task
    comment = db.get_task_to_id(add_comment_task_id)[0][5]
    if comment == '':
        edit_task_comment = comment + message.text
    else:
        edit_task_comment = comment + "\n" + message.text
    db.update_task_comment(add_comment_task_id, edit_task_comment)
    for element in edit_task_list:
        if add_comment_task_id == element[7]:
            element[5] = edit_task_comment
            # Создаем инлайн-кнопки
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="✏️ Добавить комментарий", callback_data="edit_task_comment"))
            builder.add(InlineKeyboardButton(text="✅ Закрыть", callback_data="close_task"))
            builder.adjust(1)
            # Отправляем сообщение с карточкой и кнопками
            await message.answer(task_card(element), parse_mode="HTML", reply_markup=builder.as_markup())
            await state.clear()


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        # Send a copy of the received message
        await message.answer('Такой комманды нет ❌')
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Я не понимаю о чём вы 🤷‍♂️")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
