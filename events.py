
# telegram libs
import telebot
from telebot import types
import calendar
import datetime

# config
import config
from config import bot
from config import databaseHelper
#
#import dateutil.parser

def showEvents(message):
    """
    Функция для показа списка мероприятий, и клавиатуры,
    С возможностью добавления мероприятий, а также инлайн-клавиатуры
    Для возможности удаления мероприятий.
    
    Parameters
    ----------
    message
        Объект message.
    """
    # keyboard
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    addEventButton = types.KeyboardButton(config.addEventLabel)
    goMainMenuButton = types.KeyboardButton(config.goMainMenu)
    markup.add(addEventButton, goMainMenuButton)
    # working with json
    currentChatId = message.chat.id
    databaseHelper.save(currentChatId, 'prevMenuId', 0)
    databaseHelper.save(currentChatId, 'status', 0)
    # sending
    events = databaseHelper.get(currentChatId, 'events')
    botMessage = ""
    if len(events) <= 0:
        botMessage = "<b>Добро пожаловоть в мероприятия.</b>\n\n"
        botMessage += "<i>Здесь мы будем создавать события,</i>"
        botMessage += "<i>про которые мы не хотим забыть</i>"
        botMessage += "<i>(нажмите кнопку добавить мероприятие)</i>"
    elif len(events) <= 5:
        botMessage = "<b>Вот список твоих мероприятий:</b>\n"
        botMessage += "<i>(сегодняшние мероприятия помечены значком 💣)</i>"
    else:
        botMessage = "<b>Вот список твоих мероприятий:📋😥:</b>\n"
        botMessage += "<i>(сегодняшние мероприятия помечены значком 💣)</i>"
    bot.send_message(message.chat.id, botMessage, reply_markup=markup, parse_mode='html')

    if len(events) > 0:
        eventsMessage = ""
        for number, event in enumerate(events, 1):
            if event["date"]=="29.04.2020":
                eventsMessage += "💣<b><i>%s.</i></b> %s %s %s \n" % (number, event["date"], event["time"], event["eventsName"])
            else:
                eventsMessage += "<b><i>%s.</i></b> %s %s %s \n" % (number, event["date"], event["time"], event["eventsName"])
        inlineMarkup = types.InlineKeyboardMarkup(row_width=1)
        crumbButton = types.InlineKeyboardButton('☰', callback_data='editevents')
        inlineMarkup.add(crumbButton)
        bot.send_message(message.chat.id, eventsMessage, reply_markup=inlineMarkup, parse_mode='html')
    else:
        pass

def addEvent(message):
    """
    Функция для создания мероприятия.
    С возможностью выбора даты и добавления времени.

    Parameters
    ----------
    message
        Объект message.
    """

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    goBackButton = types.KeyboardButton(config.goBack)
    markup.add(goBackButton)
    botMessage = "<b>Как мы назовем это мероприятие?</b>\n\n"
    botMessage += "Формат ввода (hh.mm dd.mm.yy event name)"
    bot.send_message(message.chat.id, botMessage, reply_markup=markup, parse_mode='html')
    
    # working with json
    currentChatId = message.chat.id
    prevID = config.IDaddEvent
    status = 2
    databaseHelper.save(currentChatId, 'prevMenuId', prevID)
    databaseHelper.save(currentChatId, 'status', status)
    pass

def createEventsDoneMarkup(call, events):
    """
    Функция для генерации инлайн клавиатуры с
    Кнопками задач и кнопкой выполнено!

    Parameters
    ----------
    call
        Объект call.
    events
        Объект событий
    """
    eventsItems = []
    for number, event in enumerate(events, 1):
        item = types.InlineKeyboardButton(f"{number}. {event['eventsName']}", callback_data=f"DeleventID={number}")
        eventsItems.append(item)
    doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data='eventsEditDone')
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*eventsItems, doneButton)
    bot.edit_message_text(chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=config.deleteTaskMessage,
                        reply_markup=markup)

# def validate_iso( sval ):
    
#     try:
#         valid_datetime = dateutil.parser.parse(sval)
#         if valid_datetime==True:
#             return True
#     except ValueError:
#         return False

def addEventDone(message):
    """
    Добавляет задачу в список дел пользователя
    Если активен статус добавления, т.е. status == 2

    Parameters
    ----------
    message
        Объект message.
    """
    # working with json
    currentChatId = message.chat.id
    status = databaseHelper.get(currentChatId, 'status')
    if status == 2:
        
        events = databaseHelper.get(currentChatId, 'events')
        eventMessage = message.text
        eventMessageList = eventMessage.split()
        eventTime = eventMessageList[0]
        eventDate = eventMessageList[1]
        eventsName= eventMessageList[2]
        newEvent = {
            "time": eventTime,
            "date": eventDate,
            "eventsName": eventsName
        }  
        events.append(newEvent)

        databaseHelper.save(currentChatId, 'events', events)
        bot.send_message(message.chat.id, "Мероприятие добавлено", reply_markup=None)
        # if validate_iso(eventTime) ==True or validate_iso(eventDate)==True:  
            
            
        # else:
        #     bot.send_message(message.chat.id, "Некоректный ввод", reply_markup=None) 
        #     pass
        
        return True
    else:
        return False



def eventsCallback(call):
    """
    Функция-обработчик инлайн событий
    Для задач: вывод задач и иконки,
    Удаление задач и возвращение назад к списку.

    Parameters
    ----------
    call
        Объект call.
    """
    # working with json
    currentChatId = call.message.chat.id
    events = databaseHelper.get(currentChatId, 'events')
    if call.data == 'editevents':
        # sending
        createEventsDoneMarkup(call, events)
    elif call.data == 'eventsEditDone':
        if len(events) > 0:
            eventsMessage = ""
            for number, event in enumerate(events, 1):
                eventsMessage += f"<b><i>{number}.</i></b> {event['eventsName']}"
                
            inlineMarkup = types.InlineKeyboardMarkup(row_width=1)
            crumbButton = types.InlineKeyboardButton('☰', callback_data='editevents')
            inlineMarkup.add(crumbButton)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=eventsMessage,
                                reply_markup=inlineMarkup,
                                parse_mode='html')
        else:
            botMessage = "<i>Ты тоже заметил, что он пуст?</i>"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id = call.message.message_id,
                                text=botMessage,
                                reply_markup=None,
                                parse_mode='html')
    elif call.data.find('DeleventID=') != -1:
        newevents = events
        for number, event in enumerate(events, 1):
            deleventId = "DeleventID=" + str(number)
            if call.data == deleventId:
                # delete event
                newevents.pop(number - 1)
                databaseHelper.save(currentChatId, 'events', newevents)
                # sending
                events = databaseHelper.get(currentChatId, 'events')
                if len(events) > 0:
                    createEventsDoneMarkup(call, events)
                else:
                    doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data='eventsEditDone')
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    markup.add(doneButton)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id = call.message.message_id,
                                        text=config.nothingForDelete,
                                        reply_markup=markup)
                break
    else:
        pass
