from pywebio import start_server
from pywebio.output import *
from pywebio.session import *
from pywebio import config

css = '''
        .table {
            width: 80%;
            margin: 20px auto; 
        }
        td {
        padding: 12px !important;
        vertical-align: top; 
        }
        
    '''

config(css_style=css)

def main():
    # Пример данных задачи
    task = {
        'name': 'Завершить проект',
        'description': 'Необходимо завершить разработку проекта до конца месяца.',
        'assigner': 'Иванов И.И.',
        'office': 'Кабинет 305',
        'deadline': '31 декабря 2023 г.',
        'comment': 'Согласовать с отделом тестирования перед сдачей.',
        'reminder': True
    }

    # Стилизованный вывод
    put_markdown('# 🗂 Информация о задаче')
    
    put_table([
        [put_text('**Название задачи**'), put_text(task['name'])],
        [put_markdown('---')],  # Разделитель
        [put_text('**Описание**'), put_text(task['description'])],
        [put_markdown('---')],
        [put_text('**От кого поступила**'), put_text(task['assigner'])],
        [put_markdown('---')],
        [put_text('**Кабинет**'), put_text(task['office'])],
        [put_markdown('---')],
        [put_text('**Срок исполнения**'), put_text(task['deadline'])],
        [put_markdown('---')],
        [put_text('**Комментарий**'), put_text(task['comment'])],
        [put_markdown('---')],
        [put_text('**Напоминание**'), 
         put_text('✅ Да' if task['reminder'] else '❌ Нет')],
    ])

if __name__ == '__main__':
    start_server(main, port=8080, debug=True)