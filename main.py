from database import Database as db
from pywebio.input import actions, input, input_group, textarea, DATE, TEXT, NUMBER
from pywebio.output import put_table, put_html, use_scope, clear_scope
from pywebio.platform import start_server
from pywebio import config
import datetime

config(css_style="#output-container{margin: 0 auto; max-width: 1200px;} #input-cards{max-width: 1200px;}")

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

def helpdesk():
    while True:
        db.create_db()
        clear_scope('output')
        output_list, interaction_list = [], []
        task_list = db.get_tasks(False)
        number = 1
        for task in task_list:
            if task[4] == today:
                date = put_html(f"""<b><p style="color: red;">{task[4].strftime("%d.%m.%Y")}</p></b>""")
            elif task[4] == tomorrow:
                date = put_html(f"""<b><p style="color: green;">{task[4].strftime("%d.%m.%Y")}</p></b>""")
            elif task[4] < today:
                date = put_html(f"""<del><p style="color: red;">{task[4].strftime("%d.%m.%Y")}</p></del>""")
            else:
                date = task[4].strftime("%d.%m.%Y")
            output_list.append((number, task[1], task[2], task[3], date, task[5]))
            interaction_list.append((number, task[0]))
            number += 1
        with use_scope('output'):
            put_table(output_list, header=[
                "№",
                "Задача",
                "От кого поступила",
                "№ кабинета",
                "Крайний срок выполнения",
                "Комментарий"
                ])
            
        menu = actions(buttons=[
            {'label': 'Добавить задачу', 'value': 'set_task'},
            {'label': 'Удалить задачу', 'value': 'delete_task', 'color': 'danger'},
            {'label': 'Поставить отметку исполнения', 'value': 'mark_execution', 'color': 'success'},
            {'label': 'Показать выполненные задачи', 'value': 'get_ready_tasks', 'color': 'success'},
        ])

        if menu == 'set_task':
            clear_scope('output')
            new_task = input_group('Добавить задачу', [
                textarea('Текст задания:', name='description'),
                input('Кто обратился?', type=TEXT, name='responsible'),
                input('Какой кабинет?', type=TEXT, name='cabinet'),
                input('Укажите крайний срок выполнения', type=DATE, name='date'),
                input('Комментарий к заданию', type=TEXT, name='comment')
            ])
            
            db.set_task([
                new_task['description'],
                new_task['responsible'],
                new_task['cabinet'],
                new_task["date"],
                new_task['comment']
                ])
            
        elif menu == 'delete_task':
            num = input('Введите номер задачи для удаления:', type=NUMBER)
            for element in interaction_list:
                if element[0] == num:
                    id = element[1]
            db.delete_task(id)
        
        elif menu == 'mark_execution':
            num = input('Введите номер задачи чтобы пометить её как завершенное:', type=NUMBER)
            for element in interaction_list:
                if element[0] == num:
                    id = element[1]
            db.set_status_ready(id)

        elif menu == 'get_ready_tasks':
            output_list = []
            task_ready_list = db.get_tasks(True)
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
            


start_server(helpdesk, port=8080, remote_access=True, auto_open_webbrowser=True, debug=True)