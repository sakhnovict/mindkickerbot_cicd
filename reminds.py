import config
from config import bot, databaseHelper
from general import showMainMenu
import os
from tasks import generateDeadline
import datetime as dt

def set_reminds_status(message):
    """
    Функция включения/выключения напоминаний
    
    Parameters
    ----------
    message
        Объект message
    
    """
    current_chat_id = message.chat.id
    remind_status = databaseHelper.get(current_chat_id, 'reminds')

    new_status = "ON" if remind_status == "OFF" else "OFF"
    databaseHelper.save(current_chat_id, 'reminds', new_status)

    showMainMenu(message)


def get_user_id_list():
    """
    Функция получения листа с id пользователей
    
    Parameters
    ----------
    
    
    """
    user_list = os.listdir('databases/')
    normal_user_list = []
    for user in user_list:
        new_user = int(user.split('.')[0])
        normal_user_list.append(new_user)
    print(normal_user_list)
    return normal_user_list

def get_days_task(task):
    """
    Функция получения дедлайна задания
    
    Parameters
    ----------
    task
        задание
    
    """
    warning = ""
    if task["date"] != "no date" and task["date"] != "":
        date = task["date"]
        # print("yo")
        # date = dt.datetime.strptime(date, '%Y-%m-%d').date()
        try:
            dateDays = date.split("-")[2]
            dateYear = date.split("-")[0]
            dateMonth = date.split("-")[1]
        except Exception:
            print("Date Error.")
            return None

        date = dt.datetime(year=int(dateYear), month=int(dateMonth), day=int(dateDays))
        now = dt.datetime.now()
        delta = date - now
        # print(delta)
        return delta.days
    else:
        return None

def check_tasks(current_chat_id):
    """
    Функция вывода напоминания
    
    Parameters
    ----------
    current_chat_id
        id текущего пользователя
    
    """
    tasks = databaseHelper.get(current_chat_id, 'tasks')
    tasksMessage = ""
    if len(tasks) > 0:

        for number, task in enumerate(tasks, 1):
            task_days = get_days_task(task)
            if task_days is not None and task_days <= 1:
                tasksMessage += "<b><i>%s.</i></b> %s\n" % (number, task["description"])

        tasksMessage += "🥵 Напоминание! До дедлайна этих задач осталось меньше дня!"

        bot.send_message(current_chat_id, tasksMessage, reply_markup=None, parse_mode='html')


if __name__ == '__main__':
    user_id_list = get_user_id_list()
    for user_id in user_id_list:
        remind_status = databaseHelper.get(user_id, 'reminds')
        print(remind_status)
        if remind_status == "ON":
            check_tasks(user_id)
        else:
            pass
