from database import Database as db
from pywebio.input import actions, input, input_group, textarea, checkbox, DATE, DATETIME, TEXT
from pywebio.output import put_text, put_markdown, put_table, put_grid, put_column, put_row, put_button, put_buttons, put_html, popup, close_popup, use_scope, scroll_to, toast, clear
from pywebio.platform import start_server
from pywebio import config
from pywebio.session import run_js, hold
import datetime


css = """
#output-container {
    margin: 0 auto;
    max-width: 1200px;
}
#input-cards {
    max-width: 1200px;
}
#input-container.fixed {
    padding: 10px 0;
}
table {
   width: 100%;
}
td:first-child {
   width: 10px;
}
tr td:nth-child(2) {
   width: 450px;
}
tr td:nth-child(3) {
   width: 180px;
}
tr td:nth-child(4) {
   width: 180px;
}
tr td:nth-child(5) {
   width: 135px;
}

"""


config(title="Helpdesk Tasks", css_style=css)


print(db.create_db())
print(db.create_table())


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
            [put_markdown(f'**{description[1]}**').style('font-size: 18px; margin: 15px 0;')],
            [
                put_column([
                    put_html('<i class="fas fa-user" style="margin-right: 8px;"></i>'),
                    put_text(f'От кого: {description[2]}')
                ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;'),
                
                put_column([
                    put_html('<i class="fas fa-door-open" style="margin-right: 8px;"></i>'),
                    put_text(f'Кабинет: {description[3]}')
                ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;'),
                
                put_column([
                    put_html('<i class="fas fa-calendar-alt" style="margin-right: 8px;"></i>'),
                    put_text(f'Срок: {description[4].strftime("%d.%m.%Y")}')
                ]).style('display: flex; align-items: center; color: #34495e; margin: 10px 0;')
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



def helpdesk():
    global status_message
    while True:
        if status_message == 1:
            toast('Задача удалена', color='red')
            status_message = 0
        elif status_message == 2:
            toast('Задача выполнена', color='green')
            status_message = 0
        elif status_message == 3:
            toast('Задача отредактирована')
            status_message = 0
        elif status_message == 4:
            toast('Новая задача добавлена')
            status_message = 0
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        clear()
        output_list_today, output_list, interaction_list = [], [], []
        task_list = db.get_tasks(False, "date")
        number = 1
        for task in task_list:
            if task[8] == True:
                # Номер задачи с напоминанием выделяется зеленым
                num = put_button(number, color='success', onclick=lambda n=number, t=task: show_task_description(n, t), outline=True, small=True)
            else:
                num = put_button(number, color='primary', onclick=lambda n=number, t=task: show_task_description(n, t), outline=True, small=True)
            if task[4] == today:
                date = put_text(task[4].strftime("%d.%m.%Y")).style('color: red')
                output_list_today.append((num, task[1], task[2], task[3], date, task[5]))
            elif task[4] == tomorrow:
                date = put_text(task[4].strftime("%d.%m.%Y")).style('color: green; font-weight: bold;')
                output_list_today.append((num, task[1], task[2], task[3], date, task[5]))
            elif task[4] < today:
                date = put_text(task[4].strftime("%d.%m.%Y")).style('color: red; text-decoration: line-through;')
                output_list_today.append((num, task[1], task[2], task[3], date, task[5]))
            else:
                date = task[4].strftime("%d.%m.%Y")
                output_list.append((num, task[1], task[2], task[3], date, task[5]))
            interaction_list.append((number, task[0]))
            number += 1
        with use_scope('output'):
            # Заголовок страницы
            put_row([
                put_html('<h2 style="margin: 0; color: #2d3748;">🎯 Helpdesk Tasks</h2>'),
                put_buttons([
                    {'label': '➕ Новая задача', 'value': 'add', 'color': 'primary'},
                    {'label': '✅ Выполненные', 'value': 'completed', 'color': 'success'}
                ], onclick=[lambda: set_task(), lambda: get_ready_tasks()]).style('margin-left: auto;')
            ]).style('align-items: center; margin-bottom: 30px;')

            put_text('Задачи на сегодня, завтра:').style('font-weight: bold;')
            put_table(output_list_today, header=[
                "№",
                "Задача",
                "От кого поступила",
                "№ кабинета",
                "Крайний срок",
                "Комментарий"
                ],).style('width: 100 %; th {width: 20%;}')
            put_text('Прочие задачи:').style('font-weight: bold;')
            put_table(output_list, header=[
                "№",
                "Задача",
                "От кого поступила",
                "№ кабинета",
                "Крайний срок",
                "Комментарий"
                ]).style('width: 100%;')
            
            hold()


            
start_server(helpdesk, port=8000, remote_access=True, auto_open_webbrowser=True, debug=True)
