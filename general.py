# telegram libs
import telebot
from telebot import types
# other libs
import random
# config
import config
from config import bot
from config import databaseHelper
from tasks import showTasks
from events import showEvents
from timetable import *
def showMainMenu(message):
    """
    Функция показа главного меню.
    Отображает стикер и приветственное сообщение.
    Устанавливает в базу необходимые значения.

    Parameters
    ----------
    message
        Объект message
    """
    # working with json
    currentChatId = message.chat.id
    databaseHelper.save(currentChatId, 'prevMenuId', 0)
    databaseHelper.save(currentChatId, 'status', 0)

    remindsStatus = databaseHelper.get(currentChatId, 'reminds')

    # keyboard
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    tasksListButton = types.KeyboardButton(config.tasksListLabel)
    timeTableButton = types.KeyboardButton(config.timeTableLabel)
    eventsButton = types.KeyboardButton(config.eventsLabel)
    game = types.KeyboardButton("Крестики-нолики")
    
    turnRemindsBtn = types.KeyboardButton(f"{config.remindsLabel} {remindsStatus}")
    markup.add(tasksListButton, timeTableButton, eventsButton, turnRemindsBtn,game )
    # sending
    sticker = open(random.choice(config.stickers), 'rb')
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, config.mainMenuMessage, reply_markup=markup)


def showHelp(message):
    """
    Функция вывода сообщения для команды /help

    Parameters
    ----------
    message
        Объект message
    """
    botMessage = f"<b>{message.from_user.first_name}</b>, {config.helpMessage}"
    bot.send_message(message.chat.id, botMessage, reply_markup=None, parse_mode='html')
    helpSticker = open('static/img/nobodycares.tgs', 'rb')
    bot.send_sticker(message.chat.id, helpSticker)
    # working with json
    currentChatId = message.chat.id
    databaseHelper.save(currentChatId, 'prevMenuId', 0)
    databaseHelper.save(currentChatId, 'status', 0)

def goMainMenu(message):
    """
    Функция возврата в главное меню

    Parameters
    ----------
    message
        Объект message
    """
    # working with json
    currentChatId = message.chat.id
    databaseHelper.save(currentChatId, 'prevMenuId', 0)
    databaseHelper.save(currentChatId, 'status', 0)
    # call mm
    showMainMenu(message)

def goBack(message):
    """
    Функция возврата в предыдущее состояние
    На один пункт

    Parameters
    ----------
    message
        Объект message
    """
    # working with json
    currentChatId = message.chat.id
    databaseHelper.save(currentChatId, 'status', 0)
    # gobacking
    prevID = databaseHelper.get(currentChatId, 'prevMenuId')

    if prevID == config.IDmainMenu:
        showMainMenu(message)
    elif prevID == config.IDshowTasksMenu:
        showTasks(message)
    elif prevID == config.IDshowEventMenu:
        showMainMenu(message)
    elif prevID == config.IDaddEvent:
        showEvents(message)
    elif prevID == config.IDshowTimetableMenu:
        messageTimetableMenu(message)
    elif prevID == config.IDaddEvent:
        showEvents(message)
    else:
        pass
