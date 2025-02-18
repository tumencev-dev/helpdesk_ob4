import asyncio
import logging
import sys
from database import Database as db
from datetime import datetime, timedelta, date

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



TOKEN = '7994013311:AAFdbCZ5FWYfYV8WO7G4NEh5H522QOjOfAQ'
new_task_data = []
edit_task_list = []
delete_task_choice_id = 0
ready_task_choice_id = 0

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


class NewTicket(StatesGroup):
    input_description_ticket = State()
    input_deadlinedate_ticket = State()

class DelTicket(StatesGroup):
    delete_ticket_id = State()
    delete_ticket_confirmation = State()

class ReadyTicket(StatesGroup):
    ready_ticket_id = State()
    ready_ticket_confirmation = State()


builder = InlineKeyboardBuilder()
builder.add(InlineKeyboardButton(text="Добавить новую задачу 📄", callback_data="set_task"))
builder.add(InlineKeyboardButton(text="Задачи на сегодня, завтра 🗂", callback_data="get_task"))
builder.add(InlineKeyboardButton(text="Удалить задачу 🗑", callback_data="del_task")),
builder.add(InlineKeyboardButton(text="Пометить как выполненное ✅", callback_data="ready_task"))
builder.adjust(1)


button_yes = KeyboardButton(text='Да')
button_no = KeyboardButton(text='Нет')
choice_kb = ReplyKeyboardMarkup(keyboard=[[button_yes], [button_no]], resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Приветствую, {html.bold(message.from_user.full_name)} 🙋", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "set_task")
async def new_task(callback_query: CallbackQuery, state: FSMContext) -> None:
    global new_task_data
    new_task_data = []
    await callback_query.message.answer("📝 Введите заголовок вашей проблемы:")
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
    await message.answer('📆 Введите дату крайнего срока в формате ГГГГ-ММ-ДД:', reply_markup=days_kb)
    await state.set_state(NewTicket.input_deadlinedate_ticket)

@dp.message(NewTicket.input_deadlinedate_ticket)
async def new_task_deadlinedate(message: Message, state: FSMContext):
    global new_task_data
    deadline_text = message.text
    if is_valid_date(deadline_text):
        new_task_data.append(message.text)
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
    else:
        await message.answer('❌ Неверный формат даты')
        await message.answer('Введите дату крайнего срока в формате: ГГГГ-ММ-ДД (с сегодняшнего дня, до 31 января 2030 года)')
        await state.set_state(NewTicket.input_deadlinedate_ticket)


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
            output_list.append((num, task[1], task[4], task[8], task[9]))
            edit_task_list.append((num, task[0], task[1]))
            num += 1
    await callback_query.message.answer('<b>ЗАДАЧИ НА СЕГОДНЯ, ЗАВТРА:</b>')
    for element in output_list:
        if element[3] == True:
            await callback_query.message.answer(f"<b>{element[0]}</b> - <i>{element[1]}</i> \n({element[2]}) \n⏰ Напоминание - {element[4]}")
        else:
            await callback_query.message.answer(f"<b>{element[0]}</b> - <i>{element[1]}</i> \n({element[2]})")
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
            delete_task_choice_id = element[1]
            await message.answer(f"Вы действительно хотите удалить задачу: \n{element[2]}", reply_markup=choice_kb)
            await state.set_state(DelTicket.delete_ticket_confirmation)

@dp.message(DelTicket.delete_ticket_confirmation)
async def delete_task_sucess(message: Message, state: FSMContext):
    global delete_task_choice_id
    if message.text == 'Да':
        db.delete_task(delete_task_choice_id)
        await message.answer('Данная задача удалена ✅', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())
    if message.text == 'Нет':
        await message.answer('Действие отменено 🛑', reply_markup=ReplyKeyboardRemove())
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
            ready_task_choice_id = element[1]
            await message.answer(f"Вы действительно хотите завершить задачу: \n{element[2]}", reply_markup=choice_kb)
            await state.set_state(ReadyTicket.ready_ticket_confirmation)

@dp.message(ReadyTicket.ready_ticket_confirmation)
async def ready_task_sucess(message: Message, state: FSMContext):
    global ready_task_choice_id
    if message.text == 'Да':
        db.set_status_ready(ready_task_choice_id)
        await message.answer('Задача выполнена ✅', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())
    if message.text == 'Нет':
        await message.answer('Действие отменено 🛑', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await message.answer('Выберите действие для дальнейшей работы с ботом:', reply_markup=builder.as_markup())


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
