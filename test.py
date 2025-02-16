from pywebio import start_server
from pywebio.output import *
from pywebio.session import *

def delete_item(item_id):
    # Здесь выполняется логика удаления элемента
    # Например, удаление из списка или базы данных
    toast(f"Элемент {item_id} удален!", color='error')
    # Обновляем интерфейс после удаления
    clear('items_list')
    with use_scope('items_list'):
        for item in items:
            put_row([
                put_text(f"Элемент {item}"),
                put_button("Удалить", onclick=lambda i=item: confirm_delete(i))
            ])

def confirm_delete(item_id):
    with popup(f"Удаление элемента {item_id}"):
        put_text(f"Вы точно хотите удалить элемент {item_id}?")
        
        # Создаем кнопки подтверждения
        put_buttons(
            [
                {'label': 'Да', 'value': 'yes'},
                {'label': 'Нет', 'value': 'no'}
            ],
            onclick=lambda choice: (
                close_popup(),
                delete_item(item_id) if choice == 'yes' else None
            )
        )

def main():
    put_markdown("## Список элементов")
    put_scope('items_list')  # Создаем область для списка элементов
    
    global items
    items = [1, 2, 3, 4, 5]  # Пример данных
    
    with use_scope('items_list'):
        for item in items:
            put_row([
                put_text(f"Элемент {item}"),
                put_button("Удалить", onclick=lambda i=item: confirm_delete(i))
            ])

if __name__ == '__main__':
    start_server(main, port=8080)