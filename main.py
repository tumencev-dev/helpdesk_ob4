from database import Database as db
from pywebio.input import actions, input, input_group, textarea, checkbox, DATE, DATETIME, TEXT
from pywebio.output import put_text, put_markdown, put_table, put_grid, put_column, put_row, put_button, put_buttons, put_html, put_collapse, popup, close_popup, use_scope, scroll_to, toast, clear
from pywebio.platform import start_server
from pywebio import config
from pywebio.session import run_js, hold
import datetime


print(db.create_db())
print(db.create_table())


config(title="Helpdesk Tasks")


status_message = 0


def show_task_description(task_number, description):
    clear()
    with use_scope('output-2'):
        put_html('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">')
        # Стили для контейнеров
        container_style = '''
            background: white; 
            border-radius: 15px; 
            padding: 30px; 
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        '''
        
        # Шапка с номером задачи
        put_html(f'''
            <div style="{container_style}">
                <div style="display: flex; align-items: center; margin-bottom: 25px;">
                    <svg style="width: 32px; height: 32px; margin-right: 15px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                    </svg>
                    <h2 style="margin: 0; color: #2c3e50;">Задача #{task_number}</h2>
                </div>
        ''')

        # Основное содержание
        put_grid([
            [put_markdown(f'**{description[1]}**').style('font-size: 18px; margin: 0 0 50px 0;')],
            [
                put_row([
                    # Первый столбец
                    put_column([
                        put_column([
                            put_html('<i class="fas fa-user" style="margin-right: 8px;"></i>'),
                            put_text(f'От кого: {description[2]}')
                        ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;'),
                        
                        put_column([
                            put_html('<i class="fas fa-door-open" style="margin-right: 8px;"></i>'),
                            put_text(f'Кабинет: {description[3]}')
                        ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;')
                    ]).style('margin-right: 300px;'),  # Отступ между колонками
                    
                    # Второй столбец
                    put_column([
                        put_column([
                            put_html('<i class="fas fa-calendar" style="margin-right: 8px;"></i>'),
                            put_text(f'Срок: {description[4].strftime("%d.%m.%Y")}')
                        ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;'),

                        put_column([
                            put_html('<i class="fas fa-bell" style="margin-right: 8px;"></i>'),
                            put_text(f'Напоминание: {description[9].strftime("%d.%m.%Y %H:%M") if description[8] else "Нет"}')
                        ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;')
                    ])
                ]).style('display: flex; gap: 30px;')  # Общий контейнер с отступами
            ],
            [put_markdown('**Комментарий:**').style('margin-top: 20px;')],
            [put_text(description[5]).style(
                'background: #f8f9fa;'
                'padding: 15px;'
                'border-radius: 8px;'
                'margin: 10px 0;'
                'color: #495057;'
            )],
            [
                put_buttons([
                    {'label': '✅ Отметить выполнение', 'value': 'complete', 'color': 'success'},
                    {'label': '✏️ Редактировать', 'value': 'edit', 'color': 'warning'},
                    {'label': '🗑️ Удалить', 'value': 'delete', 'color': 'danger'},
                    {'label': '✖️ Закрыть', 'value': 'close', 'color': 'secondary'}
                ], onclick=[
                    lambda: confirm_set_status(task_number, description),
                    lambda: edit_task(task_number, description),
                    lambda: confirm_delete(task_number, description),
                    lambda: run_js("location.reload()")
                ]).style('margin-top: 25px; display: flex; gap: 10px; flex-wrap: wrap;')
            ]
        ], cell_widths='100%').style('padding: 20px 0;')
        
        put_html('</div>')  # Закрываем основной контейнер
        scroll_to(position='top')


def confirm_delete(numer, task):
    with popup("Удаление задачи"):
        put_text("Вы точно хотите удалить эту задачу?")
        put_html('<br>')
        put_buttons(
            [
                {'label': 'Да', 'value': True, "color": 'success'},
                {'label': 'Нет', 'value': False, "color": 'danger'}
            ],
            onclick=lambda choice: (
                delete_task(task) if choice else (
                    close_popup(),  # Закрываем окно подтверждения
                   show_task_description(numer, task)  # Открываем окно с описанием
            ))
        )

def delete_task(task):
    global status_message
    id = task[0]
    db.delete_task(id)
    run_js("location.reload()")
    status_message = 1


def confirm_set_status(numer, task):
    with popup("Отметка исполнения"):
        put_text("Вы точно хотите пометить эту задачу как выполненную?")
        put_html('<br>')
        put_buttons(
            [
                {'label': 'Да', 'value': True, "color": 'success'},
                {'label': 'Нет', 'value': False, "color": 'danger'}
            ],
            onclick=lambda choice: (
                set_status(task) if choice else (
                    close_popup(),  # Закрываем окно подтверждения
                   show_task_description(numer, task)  # Открываем окно с описанием
            ))
        )

def set_status(task):
    global status_message
    id = task[0]
    db.set_status_ready(id)
    run_js("location.reload()")
    status_message = 2


def edit_task(numer, task):
        global status_message
        data = task
        clear()
        edit_task = input_group('Добавить задачу', [
            textarea('Текст задания:', name='description', value=data[1]),
            input('Кто обратился?', type=TEXT, name='responsible', value=data[2]),
            input('Какой кабинет?', type=TEXT, name='cabinet', value=data[3]),
            input('Укажите крайний срок выполнения', type=DATE, name='date', value=data[4].strftime("%Y-%m-%d")),
            input('Комментарий к заданию', type=TEXT, name='comment', value=data[5]),
            checkbox('', ['Установить напоминание'], name='reminder')
        ], cancelable=True)
                
        if edit_task != None:
            if edit_task['reminder'] != []:
                reminder = True
                if data[9] == None:
                    reminder_datetime = input('Укажите дату и время для напоминания', type=DATETIME)
                else:
                    reminder_datetime = input('Укажите дату и время для напоминания', type=DATETIME, value=data[9].strftime("%Y-%m-%d %H:%M"))
            else:
                reminder = False
                reminder_datetime = 'NULL'

            data_list = [
                data[0],
                edit_task['description'],
                edit_task['responsible'],
                edit_task['cabinet'],
                edit_task['date'],
                edit_task['comment'],
                reminder,
                reminder_datetime
                ]

            if reminder_datetime != '':
                db.update_task(data_list)
                run_js("location.reload()")
                status_message = 3
        else:
            run_js("location.reload()")
            

def set_task():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    clear()
    scroll_to(position='top')
    put_html('<br>')
    new_task = input_group('Добавить задачу', [
        textarea('Текст задания:', name='description'),
        input('Кто обратился?', type=TEXT, name='responsible'),
        input('Какой кабинет?', type=TEXT, name='cabinet'),
        input('Укажите крайний срок выполнения', type=DATE, name='date', value=str(today)),
        input('Комментарий к заданию', type=TEXT, name='comment'),
        checkbox('', ['Установить напоминание'], name='reminder')
    ], cancelable=True)

    if new_task != None:
        global status_message
        if new_task['reminder'] != []:
            reminder = True
            reminder_datetime = input('Укажите дату и время для напоминания', type=DATETIME)
        else:
            reminder = False
            reminder_datetime = None
        db.set_task([
            new_task['description'],
            new_task['responsible'],
            new_task['cabinet'],
            new_task["date"],
            new_task['comment'],
            reminder,
            reminder_datetime
            ])
        run_js("location.reload()")
        status_message = 4
    else:
        run_js("location.reload()")
        

def get_ready_tasks():
    output_list = []
    task_ready_list = db.get_tasks(True, "completed")
    task_ready_list.reverse()
    number = 1
    for task in task_ready_list:
        output_list.append((number, task[1], task[2], task[3], task[5], task[7].strftime("%d.%m.%Y")))
        number += 1
    clear()
    with use_scope('output'):
        put_table(output_list, header=[
            "№",
            "Задача",
            "От кого поступила",
            "№ кабинета",
            "Комментарий",
            "Дата выполнения"
            ])
        scroll_to(position='top')
    actions(buttons=["Закрыть"])
    run_js("location.reload()")


def get_date_style(task_date):
    today = datetime.date.today()
    if task_date == today:
        return 'color: #c53030; font-weight: 500;'
    elif task_date == today + datetime.timedelta(days=1):
        return 'color: #2f855a; font-weight: 500;'
    elif task_date < today:
        return 'color: #c53030; text-decoration: line-through;'
    return ''


def get_task_group(task_date):
    today = datetime.date.today()
    if task_date == today:
        return '🔥 Сегодня'
    if task_date == today + datetime.timedelta(days=1):
        return '⏳ Завтра'
    if task_date < today:
        return '⚠️ Просрочено'
    return '📅 Остальные'



def helpdesk():
    global status_message
    while True:
        # Обработка системных уведомлений
        toast_config = {
            1: ('Задача удалена', 'red'),
            2: ('Задача выполнена', 'green'),
            3: ('Задача отредактирована', 'blue'),
            4: ('Новая задача добавлена', 'teal')
        }
        if status_message in toast_config:
            msg, color = toast_config[status_message]
            toast(msg, color=color)
            status_message = 0

        with use_scope('output', clear=True):
            put_html('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">')
            # Заголовок страницы
            put_row([
                put_html('<h2 style="margin: 0; color: #2d3748;">🎯 Helpdesk Tasks</h2>'),
                put_buttons([
                    {'label': '➕ Новая задача', 'value': 'add', 'color': 'primary'},
                    {'label': '✅ Выполненные', 'value': 'completed', 'color': 'success'}
                ], onclick=[lambda: set_task(), lambda: get_ready_tasks()]).style('margin-left: auto;')
            ]).style('align-items: center; margin-bottom: 30px;')

            # Генерация списков задач
            task_groups = {
                '⚠️ Просрочено': [],
                '🔥 Сегодня': [],
                '⏳ Завтра': [],
                '📅 Остальные': []
            }

            number = 1
            for task in db.get_tasks(False, "date"):
                task_id = task[0]
                task_data = task
                btn_style = 'success' if task[8] else 'primary'

                # Создаем элементы отдельно
                with use_scope(f'task-{task_id}', clear=True):
                    # Кнопка номера задачи
                    num_btn = put_button(
                        label=str(number),
                        color=btn_style,
                        outline=True,
                        onclick=lambda n=number, t=task_data: show_task_description(n, t)
                    ).style('margin-right: 15px;')
                    number += 1

                    # Блок с информацией
                    info_block = put_column([
                        put_markdown(f"**{task[1]}**"),
                        put_row([
                            put_column([
                                put_html(f'<i class="fas fa-user"></i> {task[2]}').style('color: #718096;'),
                                put_html(f'<i class="fas fa-door-open"></i> {task[3]}').style('color: #718096;')
                            ]),
                            put_column([
                                put_html(
                                    f'<div style="display: flex; align-items: center; gap: 8px; {get_date_style(task[4])}">'
                                    f'<i class="fas fa-calendar-day"></i>'
                                    f'<span>{task[4].strftime("%d.%m.%Y")}</span>'
                                    '</div>'
                                ).style('margin-left: auto; height: 50px;')
                            ]).style('margin-left: auto;')
                        ]).style('height: min-content;')
                    ]).style('grid-template-rows: auto auto;')

                    # Собираем карточку
                    card = put_row([
                        num_btn,
                        info_block
                    ], size='10% 90%').style(
                        'background: white;'
                        'border-radius: 12px;'
                        'padding: 20px;'
                        'margin: 10px 0;'
                        'box-shadow: 0 2px 8px rgba(0,0,0,0.1);'
                        'align-items: flex-start;'
                        'width: 100%;'
                    )

                # Добавляем в группу
                task_groups[get_task_group(task[4])].append(card)

            # Вывод сгруппированных задач
            for group_name, tasks in task_groups.items():
                if tasks:
                    put_collapse(
                        title=group_name,
                        content=tasks,
                        open=group_name in ['🔥 Сегодня', '⚠️ Просрочено']
                    ).style('margin: 20px 0;')

            scroll_to(position='top')
            hold()


            
start_server(helpdesk, port=8000, remote_access=True, auto_open_webbrowser=True, debug=True)
