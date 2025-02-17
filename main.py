from database import Database as db
from pywebio.input import actions, input, input_group, textarea, checkbox, DATE, DATETIME, TEXT, NUMBER
from pywebio.output import put_text, put_table, put_button, put_html, popup, close_popup, use_scope, clear_scope, toast
from pywebio.platform import start_server
from pywebio import config
from pywebio.session import run_js
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


config(title="HelpDesk", css_style=css)


print(db.create_db())
print(db.create_table())


def show_task_description(task_number, description):
    with popup(task_number):
        put_text(description[1])
        put_html('<br>')
        put_button('Закрыть', onclick=close_popup)
        put_button('Удалить задачу', color='danger', onclick=lambda t=description: delete_task(t), outline=True)


def delete_task(task):
    id = task[0]
    db.delete_task(id)
    close_popup()
    run_js("location.reload()")
    toast('Задача удалена', color='red')
    

def helpdesk():
    while True:
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        clear_scope('output')
        output_list_today, output_list, interaction_list = [], [], []
        task_list = db.get_tasks(False, "date")
        number = 1
        for task in task_list:
            if task[8] == True:
                # Номер задачи с напоминанием выделяется зеленым
                num = put_button(number, color='success', onclick=lambda n=number, t=task: show_task_description(f'Задача №{n}', t), outline=True)
            else:
                num = put_button(number, color='primary', onclick=lambda n=number, t=task: show_task_description(f'Задача №{n}', t), outline=True)
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
            
        menu = actions(buttons=[
            {'label': 'Добавить задачу', 'value': 'set_task'},
            {'label': 'Редактировать задачу', 'value': 'edit_task'},
            {'label': 'Поставить отметку исполнения', 'value': 'mark_execution', 'color': 'success'},
            {'label': 'Показать выполненные задачи', 'value': 'get_ready_tasks', 'color': 'info'},
        ])


        if menu == 'set_task':
            clear_scope('output')
            new_task = input_group('Добавить задачу', [
                textarea('Текст задания:', name='description'),
                input('Кто обратился?', type=TEXT, name='responsible'),
                input('Какой кабинет?', type=TEXT, name='cabinet'),
                input('Укажите крайний срок выполнения', type=DATE, name='date', value=str(today)),
                input('Комментарий к заданию', type=TEXT, name='comment'),
                checkbox('', ['Установить напоминание'], name='reminder')
            ], cancelable=True)

            if new_task != None:
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
                toast('Новая задача добавлена')
            

        elif menu == 'mark_execution':
            num = input('Введите номер задачи чтобы пометить её как завершенное:', type=NUMBER)
            if num != None:
                for element in interaction_list:
                    if element[0] == num:
                        id = element[1]
                db.set_status_ready(id)
                toast('Задача выполнена', color='green')


        elif menu == 'get_ready_tasks':
            output_list = []
            task_ready_list = db.get_tasks(True, "completed")
            task_ready_list.reverse()
            number = 1
            for task in task_ready_list:
                output_list.append((number, task[1], task[2], task[3], task[5], task[7].strftime("%d.%m.%Y")))
                number += 1
            clear_scope('output')
            with use_scope('output'):
                put_table(output_list, header=[
                    "№",
                    "Задача",
                    "От кого поступила",
                    "№ кабинета",
                    "Комментарий",
                    "Дата выполнения"
                    ])
            actions(buttons=["Назад"])


        elif menu == 'edit_task':
            num = input('Введите номер задачи, которую нужно отредактировать:', type=NUMBER)
            
            if num != None:
                for element in interaction_list:
                    if element[0] == num:
                        id = element[1]
                data_task = db.get_tasks(False, "date")
                for task in data_task:
                    if task[0] == id:
                        data = task
                clear_scope('output')
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
                        toast('Задача отредактирована')


start_server(helpdesk, port=8000, remote_access=True, auto_open_webbrowser=True, debug=True)