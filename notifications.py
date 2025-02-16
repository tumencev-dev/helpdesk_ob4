from database import Database as db
import requests
import datetime
from time import sleep


def send_notification(message):
    TOKEN = '7994013311:AAFdbCZ5FWYfYV8WO7G4NEh5H522QOjOfAQ'
    chat_id = '453987381'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json()


def cheking_notifications():
    output_list = []
    chek_in_list = 0
    cheking_list = db.get_tasks(False, "id")
    for element in cheking_list:
        if element[8] == True:
            for notification in output_list:
                if element[0] == notification[0]:
                    chek_in_list = 1
            if chek_in_list == 0:
                    output_list.append([element[0], element[1], element[9]])
            else:
                chek_in_list = 0
    return output_list

message = 0


while True:
    message_num = len(cheking_notifications())
    notification_list = cheking_notifications()
    timestamp = datetime.datetime.now()
    if message != message_num:
        print(f'{timestamp.strftime("%Y-%m-%d %H:%M")} - В работе {len(notification_list)} напоминания(й)')
        message = len(notification_list)
    for element in notification_list:
        if element[2].strftime("%Y-%m-%d %H:%M") == timestamp.strftime("%Y-%m-%d %H:%M"):
            send_notification(f'⚠️ Напоминание в {element[2].strftime("%H:%M")} ⚠️\nТекст сообщения: {element[1]}')
    sleep(60)
