# config
from config import bot
import config
# mylibs
from tasks import *
from general import *
from timetable import *
from events import *
from reminds import *
from tictactoe import *

import time

@bot.message_handler(commands=['start'])
def start(message):
    """
    Старт бота

    Parameters
    ----------
    message
        Объект message
    """
    showMainMenu(message)


@bot.message_handler(commands=['help'])
def help(message):
    """
    Вывод сообщение-справки

    Parameters
    ----------
    message
        Объект message
    """
    showHelp(message)

@bot.message_handler(content_types=['text'])
def textHandler(message):
    """
    Функция обработки письменных команд

    Parameters
    ----------
    message
        Объект message
    """
    if message.text == config.tasksListLabel:
        showTasks(message)
    elif message.text == config.goMainMenu:
        goMainMenu(message)
    elif message.text == config.goBack:
        goBack(message)
    elif message.text == config.addTaskLabel:
        addTask(message)
    elif message.text == config.timeTableLabel:
        messageTimetableMenu(message)
    elif message.text == config.eventsLabel:
        showEvents(message)
    elif message.text == config.addEventLabel:
        addEvent(message)
    elif message.text == config.addTimetable:
        addTimetables(message)
    elif message.text == "Крестики-нолики":
        startTTT(message)
    elif message.text == "Новая игра":
        start_new_game(message)
    elif config.remindsLabel in message.text:
        set_reminds_status(message)
    else:
        if not addTaskDone(message) and not addEventDone(message) and not addTimetableDone(
                message) and not addPatternDone(message):
            bot.send_message(message.chat.id, config.emptyQuery)


@bot.callback_query_handler(func=lambda call: True)
def callbackHandler(call):
    """
    Функция обработки колбеков
    Parameters
    ----------
    call
        Объект call
    """
    if call.message:
        tasksCallback(call)
        calendarCallback(call)
        eventsCallback(call)
        callback_game(call)


def main():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(3)

if __name__ == '__main__':
    main()