import requests
import base64
import os
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import set_env


def upload_image_to_imgur(image_path, client_id):
    """
    Загружает изображение на Imgur и возвращает ссылки на оригинал и превью.
    
    :param image_path: Путь к файлу изображения
    :param client_id: Client-ID для Imgur API
    :return: Словарь с ссылками на оригинал и превью
    """
    # Проверка существования файла
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File {image_path} not found")

    # Чтение и кодирование изображения
    with open(image_path, "rb") as image_file:
        b64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Настройка заголовков и данных запроса
    headers = {"Authorization": f"Client-ID {client_id}"}
    payload = {
        "image": b64_image,
        "type": "base64"
    }

    # Отправка запроса
    response = requests.post(
        "https://api.imgur.com/3/upload",
        headers=headers,
        data=payload
    )

    # Обработка ошибок
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.text}")

    try:
        response_data = response.json()
        img_data = response_data["data"]
        original_url = img_data["link"]
        
        # Формирование URL превью
        filename = original_url.split("/")[-1]
        name, ext = os.path.splitext(filename)
        preview_url = original_url.replace(filename, f"{name}s{ext}")

        return {
            "original": original_url,
            "preview": preview_url
        }

    except KeyError as e:
        raise Exception(f"Unexpected API response: {response.text}") from e
    except requests.exceptions.JSONDecodeError as e:
        raise Exception("Invalid JSON response") from e


def main():
    set_env(title="Image Uploader to Imgur")
    CLIENT_ID = "b4e2aec568a501e"  # Замените на свой Client-ID
    
    put_markdown("## 🖼️ Загрузчик изображений на Imgur")
    put_html("<hr>")
    
    while True:
        file = file_upload("Выберите изображение:", accept="image/*", required=True)
        
        temp_file = f"temp_{file['filename']}"
        with open(temp_file, "wb") as f:
            f.write(file['content'])
        
        try:
            put_loading(color='primary')
            result = upload_image_to_imgur(temp_file, CLIENT_ID)
            
            clear()
            put_success("✅ Изображение успешно загружено!")
            
            # Отображаем превью
            put_markdown(f"### Превью изображения:")
            put_image(result['preview']).style("cursor: pointer; border: 2px solid #ddd; padding: 5px;")
            
            # Кнопка для открытия оригинала
            put_markdown("Нажмите кнопку ниже, чтобы открыть оригинал:")
            put_button("Открыть оригинал", onclick=lambda: popup("Оригинал изображения", [
                put_image(result['original']),
                put_button("Закрыть", onclick=close_popup)
            ], size='large'))
            
            # Ссылки для копирования
            put_markdown("### Ссылки:")
            put_table([
                ['Прямая ссылка:', put_link('Открыть', result['original'], new_window=True)],
                ['Ссылка на превью:', put_link('Открыть', result['preview'], new_window=True)],
            ])
            
            put_markdown("""
            **Инструкция:**
            1. Нажмите кнопку "Открыть оригинал" для просмотра оригинала
            2. Используйте правую кнопку мыши для копирования ссылок
            """)
            
        except Exception as e:
            clear()
            put_error(f"Ошибка: {str(e)}")
            put_button("Попробовать снова", onclick=lambda: None)
        
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        if not actions('Продолжить?', ['Загрузить еще', 'Выход']):
            break

if __name__ == "__main__":
    start_server(
        main,
        port=8080,
        debug=True,
        host='localhost',
        allowed_origins='*'
    )
    print("Сервер запущен: http://localhost:8080")