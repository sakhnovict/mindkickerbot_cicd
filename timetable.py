# telegram libs
import telebot
from telebot import types
# other libs
import calendar
import datetime
import random
import json
import numpy
# config
import config
from config import bot
from config import databaseHelper
import database

def messageTimetableMenu(message):
    """
    Выводит календарь.

    Parameters
    ----------
    message
        Объект message.
    """
    prevID = config.IDmainMenu
    chatId = message.chat.id

    databaseHelper.save(chatId, 'prevMenuId', prevID)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    buttonTimetableBack = telebot.types.KeyboardButton('Назад')
    markup.add(buttonTimetableBack)
    bot.send_message(chatId, '.', reply_markup=markup)
    markup = createCalendar()
    bot.send_message(chatId, config.selectDate, reply_markup=markup)

def calendarCallback(call):
    """
    Колбеки для всего модуля timetable.

    Parameters
    ----------
    call
        Объект call.
    """
    chatId = call.message.chat.id
    messageId = call.message.message_id

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttonTimetableBack = telebot.types.KeyboardButton('Назад')
    markup.add(buttonTimetableBack)
    data = separateCallbackData(call.data)

    if call.data == 'new':
        prevID = config.IDshowTimetableMenu
        status = 3

        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'status', status)

        bot.send_message(chatId, config.enterTimeSubject, reply_markup=None)

    elif call.data == 'add':
        prevID = config.IDshowTimetableMenu
        status = 4

        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'status', status)

        bot.send_message(chatId, config.enterTimeSubject, reply_markup=None)

    elif call.data == 'edit':
        # изменение выбранного элемента расписания
        prevID = config.IDshowTimetableMenu
        status = 5
        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'status', status)

        bot.send_message(chatId, 'Введите:', reply_markup = None)

    elif call.data == 'del':
        # удаление всей строчки расписания
        timetables = databaseHelper.get(chatId, 'timetable')
        date = databaseHelper.get(chatId, 'date')
        whence = databaseHelper.get(chatId, 'el').split(";")[0]
        el = databaseHelper.get(chatId, 'el').split(";")[1]

        timetable = ishas(timetables, date)
        timetables.remove(timetable)

        index = 0
        if(whence == 'time'):
            index = timetable[1].index(el)
        if(whence == 'subject'):
            index = timetable[2].index(el)

        timetable[1].pop(index)
        timetable[2].pop(index)
        if(len(timetable[1]) != 0):
            timetables.append(timetable)
            showTimetable(chatId, messageId, timetables, date)
        else:
            showEmptyTimetable(chatId, messageId, date)

        databaseHelper.save(chatId, 'timetable', timetables)

    elif call.data == 'pattern':
        #Вывод всех шаблонов
        prevID = 5
        patterns = databaseHelper.get(chatId, 'patterns')

        if len(patterns) == 0:
            showEmptyPattern(chatId, messageId)
        else:
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)

            for i in range(len(patterns)):
                row = []
                name = patterns[i][0]
                row.append(telebot.types.InlineKeyboardButton(name, callback_data=createCallbackData('thisPattern', el=name)))
                markup.add(*row)
            markup.row(telebot.types.InlineKeyboardButton('Добавить', callback_data='addPattern'))
            bot.edit_message_text(chat_id=chatId, message_id=messageId, text='Шаблоны', reply_markup=markup)

    elif call.data == 'addPattern':
        #добавление шаблона
        prevID = 5
        status = 6

        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'status', status)

        bot.send_message(chat_id=chatId, text='Введите название шаблона', reply_markup=None)

    elif data[0] == 'thisPattern':
        #работа с выбранным шаблонам
        prevID = config.IDshowTimetableMenu
        databaseHelper.save(chatId, 'el', data[4])
        
        delButton = types.InlineKeyboardButton('Удалить шаблон', callback_data='delPattern')
        editButton = types.InlineKeyboardButton('Изменить название', callback_data='editPattern')
        applyButton = types.InlineKeyboardButton('Применить', callback_data='applyPattern')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*getListPattern(data[4], chatId))
        markup.row(delButton,editButton,applyButton)
        bot.edit_message_text(chat_id=chatId, message_id=messageId, text='Шаблоны', reply_markup=markup)

    elif call.data == 'delPattern':
        #Удаление шаблона
        prevID = config.IDshowTimetableMenu
        patterns = databaseHelper.get(chatId, 'patterns')
        el = databaseHelper.get(chatId, 'el')

        for i in range(0,len(patterns)):
            if patterns[i][0] == el:
                patterns.pop(i)
                break
                pass
            pass
        
        if(len(patterns) != 0):
            showPatterns(patterns, chatId, messageId)
        else:
            showEmptyPattern(chatId, messageId)

        databaseHelper.save(chatId, 'patterns', patterns)

    elif call.data == 'editPattern':
        #Изменение названия шаблона
        prevID = config.IDshowTimetableMenu
        status = 8

        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'status', status)

        bot.send_message(chatId, 'Введите новое название', reply_markup = None)

    elif call.data == 'applyPattern':
        #Применение шаблона
        date = databaseHelper.get(chatId, 'date')
        timetable = []
        timetables = databaseHelper.get(chatId, 'timetable')
        patterns = databaseHelper.get(chatId, 'patterns')
        el = databaseHelper.get(chatId, 'el')
        index = 0
        for i in range(0,len(patterns)):
            if patterns[i][0] == el:
                index = i
                break
                pass
            pass
        
        fullSub = ' '
        fullTime = ' '
       
        timetable = [date,patterns[index][1],patterns[index][2]]
        
        timetables.append(timetable)

        databaseHelper.save(chatId, 'timetable', timetables)
        bot.send_message(chatId, 'Шаблон применен', reply_markup=None)
        showTimetable(chatId, chatId, timetables, date, variant = 1)

    elif data[0] == 'patternItem':
        #работа с теккущим элементом шаблона
        prevID = config.IDshowTimetableMenu
        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'el', data[4] + ';' + data[5])

        markup = types.InlineKeyboardMarkup(row_width = 2)
        delButton = types.InlineKeyboardButton('Удалить', callback_data='delItem')
        editButton = types.InlineKeyboardButton('Изменить', callback_data='editItem')

        markup.add(delButton, editButton)
        bot.edit_message_text(chat_id=chatId, message_id=messageId, text='Ваши действия', reply_markup=markup)

    elif call.data == 'delItem':
        #удаление элемента шаблона
        patterns = databaseHelper.get(chatId, 'patterns')
        el = databaseHelper.get(chatId, 'el')
        name = el.split(';')[1]
        time = el.split(';')[0]

        patterns = databaseHelper.get(chatId, 'patterns')
        pattern = ''
        for i in range(0,len(patterns)):
                if patterns[i][0] == name:
                    pattern = patterns[i]
                    patterns.pop(i)
                    break
       
        for i in range(0, len(pattern[1])):
            if pattern[1][i] == time:
                pattern[1].pop(i)
                pattern[2].pop(i)
                patterns.append(pattern)
                break

        databaseHelper.save(chatId, 'patterns', patterns)

        showPatterns(patterns, chatId, messageId)

    elif call.data == 'editItem':
        # изменение выбранного элемента расписания
        prevID = config.IDshowTimetableMenu
        status = 9
        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'status', status)

        bot.send_message(chatId, 'Введите:', reply_markup = None)
        pass

    elif data[0] == 'time' or data[0] == 'subject':
        prevID = config.IDshowTimetableMenu
        databaseHelper.save(chatId, 'prevMenuId', prevID)
        databaseHelper.save(chatId, 'el', data[0] + ";" + data[4])

        delButton = types.InlineKeyboardButton(config.delete, callback_data='del')
        editButton = types.InlineKeyboardButton(config.change, callback_data='edit')
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(delButton, editButton)
        bot.edit_message_text(chat_id=chatId, message_id=messageId, text=config.whatToDo, reply_markup=markup)

    elif data[0] == 'DAY':
        prevID = config.IDshowTimetableMenu
        databaseHelper.save(chatId, 'prevMenuId', prevID)

        date = data[1] + '.' + data[2] + '.' + data[3]

        timetables = databaseHelper.get(chatId, 'timetable')

        if ishas(timetables, date) != False:
            showTimetable(chatId, messageId, timetables, date)
        else:
            showEmptyTimetable(chatId, messageId, date)

    elif data[0] == 'PREV-MONTH':
        if( int(data[2]) == 1):
            markup = createCalendar(int(data[1]) - 1, 12)
        else:
            markup = createCalendar(int(data[1]), int(data[2]) - 1)

        bot.edit_message_text(chat_id=chatId, message_id=messageId,text="Пожалуйста, выберите дату", reply_markup=markup)

    elif data[0] == 'NEXT-MONTH':
        if( int(data[2]) == 12):
            markup = createCalendar(int(data[1]) + 1, 1)
        else:
            markup = createCalendar(int(data[1]), int(data[2]) + 1)

        bot.edit_message_text(chat_id=chatId, message_id=messageId,text="Пожалуйста, выберите дату", reply_markup=markup)

def showEmptyTimetable(chatId, messageId, date):
    """
    Просмотр пустого расписание.

    Parameters
    ----------
    chatId
        id чата.
    messageId
        id сообщения.
    date
        дата дд.мм.гггг
    """
    databaseHelper.save(chatId, 'date', date)

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttonTimetableCreator = telebot.types.InlineKeyboardButton('Создать расписание', callback_data='new')
    buttonPattern = telebot.types.InlineKeyboardButton('Применить шаблон', callback_data='pattern')
    markup.row(buttonTimetableCreator)
    markup.row(buttonPattern)
    bot.edit_message_text(chat_id=chatId, message_id=messageId, text='Расписание отсутствует', reply_markup=markup)

def showEmptyPattern(chatId, messageId):
    """
    Просмотр пустого шаблона.

    Parameters
    ----------
    chatId
        id чата.
    messageId
        id сообщения.
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttonPatternCreator = telebot.types.InlineKeyboardButton('Создать шаблон', callback_data='addPattern')
    markup.row(buttonPatternCreator)
    bot.edit_message_text(chat_id=chatId, message_id=messageId, text='Шаблоны отсутствуют', reply_markup=markup)

def showTimetable(chatId, messageId, timetables, date, variant = 0):
    """
    Просмотр расписание.

    Parameters
    ----------
    chatId
        id чата.
    messageId
        id сообщения.
    date
        дата дд.мм.гггг
    timetables
        Объект timetable
    variant
        Вариант работы функции
    """
    timetable = ishas(timetables, date)

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    for i in range(len(timetable[1])):
        row = []
        time = timetable[1][i]
        subject = str(timetable[2][i])
        row.append(telebot.types.InlineKeyboardButton(time, callback_data=createCallbackData('time', el=time)))
        row.append(telebot.types.InlineKeyboardButton(subject, callback_data=createCallbackData('subject', el=subject)))
        markup.add(*row)

    markup.row(telebot.types.InlineKeyboardButton('Добавить', callback_data='add'))

    if variant == 0:
        bot.edit_message_text(chat_id=chatId, message_id=messageId, text=date, reply_markup=markup)
    elif variant == 1:
        bot.send_message(chat_id=chatId, text=date, reply_markup=markup)

    databaseHelper.save(chatId, 'date', date)

def addTimetables(message):
    """
    Добавления расписания.

    Parameters
    ----------
    message
        Объект message.
    """
    prevID = config.IDshowTasksMenu
    chatId = message.chat.id
    status = 3

    databaseHelper.save(chatId, 'prevMenuId', prevID)
    databaseHelper.save(chatId, 'status', status)

    bot.send_message(chatId, 'Введите: время(16 00) и предмет(Программная инженерия)', reply_markup=None)

def addTimetableDone(message):
    """
    Функция для работы с созданием, добавление, изменение, удаление расписание.

    Parameters
    ----------
    message
        Объект message.
    """
    currentChatId = message.chat.id
    status = databaseHelper.get(currentChatId, 'status')
    if status == 3:
        #Создание расписания
        addTimetableItem(currentChatId, message,var=1)
    elif status == 4:
        #Добавление нового элемента к расписанию
        addTimetableItem(currentChatId, message)
    elif status == 5:
        #Изменение предмета\время
        timetables = databaseHelper.get(currentChatId, 'timetable')
        date = databaseHelper.get(currentChatId, 'date')
        whence = databaseHelper.get(currentChatId, 'el').split(";")[0] #переменная от которой зависит, что будет изменено
        el = databaseHelper.get(currentChatId, 'el').split(";")[1]

        timetable = ishas(timetables, date)
        timetables.remove(timetable)

        index = 0
        if(whence == 'time'):
            index = timetable[1].index(el)
            text = message.text.split(" ")
            if valid(text, 0, message.chat.id): return True
            fullTime = text[0] + ':' + text[1]
            if valid(timetable[1], 2, message.chat.id, tmpif=fullTime,): return True
            timetable[1][index] = fullTime

        if(whence == 'subject'):
            index = timetable[2].index(el)
            timetable[2][index] = message.text

        index = getIndexForSorting(timetable[1])
        timetable[1] = sorting(timetable,index,how = 0)
        timetable[2] = sorting(timetable,index,how = 1)
        timetables.append(timetable)
        databaseHelper.save(currentChatId, 'timetable', timetables)

        timetable = ishas(timetables, date)

        showTimetable(currentChatId, message.chat.id, timetables, date, variant = 1)
        return True
    elif status == 10:
        #Обработка вариантов дублирования
        if not(message.text.isnumeric()) or int(message.text) < 0 or int(message.text) > 3:
            bot.send_message(message.chat.id, 'Выбранного варианта не существует', reply_markup=None)
            return True
        
        date = databaseHelper.get(currentChatId, 'date')
        msg = databaseHelper.get(currentChatId, 'el')
        timetables = databaseHelper.get(currentChatId, 'timetable')

        var = int(message.text)
        if var == 0:
            showTimetable(currentChatId, message.chat.id, timetables, date, variant = 1)
            return True
        elif var == 1:
            duplication(date,msg ,var,currentChatId)
            showTimetable(currentChatId, message.chat.id, timetables, date, variant = 1)
            return True
        elif var == 2:
            duplication(date,msg ,var,currentChatId)
            showTimetable(currentChatId, message.chat.id, timetables, date, variant = 1)
            return True
        elif var == 3:
            duplication(date,msg ,var,currentChatId)
            showTimetable(currentChatId, message.chat.id, timetables, date, variant = 1)
            return True

        return True

def addTimetableItem(chatId, message, var = 0, vardup = 0):
    """
    Добавление элемента расписание

    Parameters
    ----------
    chatId
        id чата.
    message
        Объект message.
    var
        Вариант работы функции
    vardup
        Вариант работы функции
    """
    date = databaseHelper.get(chatId, 'date')
    timetable = ishas(databaseHelper.get(chatId, 'timetable'), date)
    timetables = databaseHelper.get(chatId, 'timetable')

    if(var == 0): timetables.remove(timetable)
    if(vardup == 0):
        text = message.text.split(" ")
    else:
        text = message.split(" ")


    if valid(text, 0, chatId): return True
          
    fullTime = text[0] + ':' + text[1]
    if var == 0 and valid(timetable[1], 2, chatId, tmpif=fullTime): return True

    if(var == 0): timetable[1].append(fullTime.strip())
        
    fullSub = ' '
    for i in range(2, len(text)):
        fullSub += text[i] + ' '

    if valid(fullSub, 1, chatId): return True

    if(var == 0):
        timetable[2].append(fullSub)
        index = getIndexForSorting(timetable[1])
        timetable[1] = sorting(timetable,index, how = 0)
        timetable[2] = sorting(timetable,index, how = 1)
        timetables.append(timetable)
    elif(var == 1):
        time = []
        time.append(fullTime.strip())
        sub = []
        sub.append(fullSub)
        timetables.append([date, time, sub])

    databaseHelper.save(chatId, 'timetable', timetables)

    if vardup == 0:
        status = 10
        databaseHelper.save(chatId, 'el', message.text)
        databaseHelper.save(chatId, 'status', status)
        bot.send_message(chatId, 'Дублирование:\n0 - нет\n 1 - на следующую неделю\n 2 - через неделю\n 3 - на 4 недели вперед', reply_markup=None)
    
    return True

def duplication(date,message,var,chatId):
    """
    Дублирование элементов расписание.

    Parameters
    ----------
    date
        дата дд.мм.гггг
    message
        Объект message.
    var
        Вариант работы функции
    chatId
        id чата.
    """
    listDate = date.split('.')
    listNumDate = []
    for i in listDate:
        listNumDate.append(int(i))
        pass
    date = datetime.date(listNumDate[0], listNumDate[1], listNumDate[2])
    
    if var == 1:
        nextDate = getNextDate(chatId, date, 7)
        if ishas(databaseHelper.get(chatId, 'timetable'), nextDate) == False:
            addTimetableItem(chatId, message, var = 1, vardup = 1)
        else:
            addTimetableItem(chatId, message, var = 0, vardup = 1)
    elif var == 2:
        nextDate = getNextDate(chatId, date, 14)
        if ishas(databaseHelper.get(chatId, 'timetable'), nextDate) == False:
            addTimetableItem(chatId, message, var = 1, vardup = 1)
        else:
            addTimetableItem(chatId, message, var = 0, vardup = 1)
    elif var == 3:
        listDay = [7, 14, 21, 28]
        for i in listDay:
            nextDate = getNextDate(chatId, date, i)
            if ishas(databaseHelper.get(chatId, 'timetable'), nextDate) == False:
                addTimetableItem(chatId, message, var = 1, vardup = 1)
            else:
                addTimetableItem(chatId, message, var = 0, vardup = 1)
    return True

def getNextDate(chatId, date, day):
    """
    Функция для получения следующей даты.

    Parameters
    ----------
    date
        дата дд.мм.гггг
    day
        Номер шага
    chatId
        id чата.
    """
    nextDate = date + datetime.timedelta(days=day)
    nextDate = str(nextDate).split('-')
    for i in range(0,len(nextDate)):
        nextDate[i] = str(int(nextDate[i]))
        
    nextDate = '.'.join(nextDate)
    databaseHelper.save(chatId, 'date', nextDate)
    return nextDate

def showPatterns(patterns, chatId, messageId, variant = 0):
    """
    Функция для просмотра шаблонов

    Parameters
    ----------
    patterns
        шаблоны
    messageId
        id сообщения.
    variant
        Вариант работы функции
    chatId
        id чата.
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    for i in range(len(patterns)):
        row = []
        name = patterns[i][0]
        row.append(telebot.types.InlineKeyboardButton(name, callback_data=createCallbackData('thisPattern', el=name)))
        markup.add(*row)
    markup.row(telebot.types.InlineKeyboardButton('Добавить', callback_data='addPattern'))

    if variant == 0:
        bot.edit_message_text(chat_id=chatId, message_id=messageId, text='Шаблоны', reply_markup=markup)
    elif variant == 1:
        bot.send_message(chat_id=chatId, text='Шаблоны', reply_markup=markup)

def getListPattern(el, chatId):
    """
    Функция для получения элементов шаблона

    Parameters
    ----------
    el
        шаблон
    chatId
        id чата.
    """
    listPattern = []
    patterns = databaseHelper.get(chatId, 'patterns')
    pattern = ''
    for i in range(0,len(patterns)):
            if patterns[i][0] == el:
                pattern = patterns[i]
                break
    
    for i in pattern[1]:
        listPattern.append(types.InlineKeyboardButton(i, callback_data=createCallbackData('patternItem', el=(str(i) +';'+str(el)))))

    return listPattern

def addPatternDone(message):
    """
    Функция для работы с созданием, добавление, изменение, удаление шаблонов.

    Parameters
    ----------
    message
        Объект message.
    """
    сhatId = message.chat.id
    messageId = message.chat.id
    status = databaseHelper.get(сhatId, 'status')
    if status == 6:
        #создание шаблона
        patterns = databaseHelper.get(сhatId, 'patterns')
        if valid(message.text, 1, message.chat.id): return True
        patterns.append([message.text])
        databaseHelper.save(сhatId, 'patterns', patterns)
        bot.send_message(chat_id=сhatId, text='Отличное название.\nДавайте теперь его заполнил)\nПример ввода:8 00 9 00 10 00 11 00 ...\nВведите время', reply_markup=None)
        status = 7
        databaseHelper.save(сhatId, 'status', status)
        return True
    if status == 7:
        #заполнение шаблона
        patterns = databaseHelper.get(сhatId, 'patterns')
        allTime = message.text.split(" ")
        time = []
        sub = []
        listFullTime = []
        for i in range(0,len(allTime),2):
            if len(allTime)%2 != 0:
                bot.send_message(сhatId, 'Некорректное время\nВведите еще раз)', reply_markup=None)
                return True
            if valid([allTime[i], allTime[i+1]], 0, message.chat.id): return True
        for i in range(0,len(allTime),2):
            listFullTime.append(allTime[i]+':'+allTime[i+1])

        for i in range(0,len(listFullTime)):
            for j in range(i+1,len(listFullTime)):
                if listFullTime[i]== listFullTime[j]:
                    bot.send_message(сhatId, 'Время повторяется\nВведите еще раз)', reply_markup=None)
                    return True

        for i in range(0,len(allTime),2):
            if len(allTime)%2 != 0:
                bot.send_message(сhatId, 'Некорректное время\nВведите еще раз)', reply_markup=None)
                return True
            if valid([allTime[i], allTime[i+1]], 0, message.chat.id): return True
      
            time.append(allTime[i]+':'+allTime[i+1])
            
            if i == len(allTime)-2:
                break

        for i in time:
            sub.append(' ')

        index = getIndexForSorting(time)
        patterns[len(patterns)-1].append(sorting(time,index,how = 2))
        patterns[len(patterns)-1].append(sub)
        databaseHelper.save(сhatId, 'patterns', patterns)
        bot.send_message(chat_id=сhatId, text='Шаблон создан', reply_markup=None)
        showPatterns(patterns, сhatId, messageId, variant = 1)
        return True
    if status == 8:
        #изменение названия шаблона
        patterns = databaseHelper.get(сhatId, 'patterns')
        el = databaseHelper.get(сhatId, 'el')

        for i in range(0,len(patterns)):
            if patterns[i][0] == el:
                patterns[i][0] = message.text   
                break
        databaseHelper.save(сhatId, 'patterns', patterns)
        showPatterns(patterns, сhatId, messageId, variant = 1)
        return True
    if status == 9:
        # изменение элемента шаблона
        patterns = databaseHelper.get(сhatId, 'patterns')
        el = databaseHelper.get(сhatId, 'el')
        name = el.split(';')[1]
        time = el.split(';')[0]
        allTime = message.text.split(" ")
        for i in range(0,len(allTime),2):
            if len(allTime)%2 != 0:
                bot.send_message(сhatId, 'Некорректное время\nВведите еще раз)', reply_markup=None)
                return True
            if valid([allTime[i], allTime[i+1]], 0, message.chat.id): return True
        if valid( [message.text.split(" ")[0],message.text.split(" ")[1]], 0, message.chat.id): return True
        newTime = message.text.split(" ")[0] + ':' + message.text.split(" ")[1]
        
        patterns = databaseHelper.get(сhatId, 'patterns')
        
        pattern = ''
        for i in range(0,len(patterns)):
                if patterns[i][0] == name:
                    pattern = patterns[i]
                    for j in range(0, len(pattern[1])):
                        if pattern[1][j] == time:
                            pattern[1][j] = newTime
                            index = getIndexForSorting(pattern[1])
                            pattern[1] = sorting(pattern,index, how = 0)
                            break
                    break

        databaseHelper.save(сhatId, 'patterns', patterns)
        showPatterns(patterns, сhatId, messageId, variant = 1)
        return True
    return True

def createCallbackData(action, year=None, month=None, day=None, el=None):
    """
    Запечатывание колбека.

    Parameters
    ----------
    action
        Действие.
    """
    return ";".join([action, str(year), str(month), str(day), str(el)])

def separateCallbackData(data):
    """
    Распечатывание колбека.

    Parameters
    ----------
    data
        колбек.
    """
    return data.split(";")

def createCalendar(year=None, month=None):
    """
    Создание календаря.

    Parameters
    ----------
    year
        год.
    month
        месяц
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=7)

    now = datetime.datetime.now()
    if year == None:
        year = now.year
    if month == None:
        month = now.month
    data_ignore = createCallbackData("IGNORE", year, month, 0)

    markup.row(telebot.types.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore))

    row = []

    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append(telebot.types.InlineKeyboardButton(day, callback_data=data_ignore))
    markup.add(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if(day == 0):
                row.append(telebot.types.InlineKeyboardButton(
                    " ", 
                    callback_data=data_ignore))
            else:
                row.append(telebot.types.InlineKeyboardButton(
                    str(day),
                     callback_data=createCallbackData("DAY", year, month, day)))
        markup.add(*row)

    row = []
    markup.row(*[telebot.types.InlineKeyboardButton("<", callback_data=createCallbackData("PREV-MONTH", year, month, day)),
                 telebot.types.InlineKeyboardButton(" ", callback_data=data_ignore),
                 telebot.types.InlineKeyboardButton(">", callback_data=createCallbackData("NEXT-MONTH", year, month, day))])
    return markup

def sorting(timetable, index, how = 0):
    """
    Функция для сортировке по индексам

    Parameters
    ----------
    timetable
        объект массиво
    index
        индек сортировки.
    how
        Вариант работы функции
    """
    if how == 0:
        time = timetable[1]
        time = numpy.take_along_axis( numpy.asarray(time), index,axis=None)
        return time.tolist()
    elif how == 1:
        sub = timetable[2]
        sub = numpy.take_along_axis(numpy.asarray(sub), index,axis=None)
        return sub.tolist()
    elif how == 2:
        time = numpy.take_along_axis(numpy.asarray(timetable), index,axis=None)
        return time.tolist()

def getIndexForSorting(arr):
    """
    Функция для получения индекса сортировки

    Parameters
    ----------
    arr
        массив
    
    """
    tmpArr = []
    for i in arr:
        tmpArr.append(int(i.replace(":", "")))
    tmpArr = numpy.asarray(tmpArr)
    index = numpy.argsort(tmpArr)
    return index

def valid( condition, var, chatId, tmpif=None):
    """
    Функция для проверки корректности введенных данных.

    Parameters
    ----------
    condition
        данные для проверки
    var
        Вариант работы функции
    chatId
        id чата.
    """
    if var == 0:
        if len(condition) < 1 or not(condition[0].isnumeric()) or not(condition[1].isnumeric()) or int(condition[0]) < 0 or int(condition[0]) > 23 or int(condition[1]) < 0 or int(condition[1]) > 59:
            bot.send_message(chatId, 'Некорректное время\nВведите еще раз)', reply_markup=None)
            return True
        else:
            return False
    elif var == 1:
        if len(condition) >= 17:
            bot.send_message(chatId, 'Название больше 17 символов. Попробуйте сократить)', reply_markup=None)
            return True
        else:
            return False
    elif var == 2:
        for i in condition:
            if i == tmpif:
                bot.send_message(chatId, 'Данное время уже существует\nВведите еще раз)', reply_markup=None)
                return True
        return False

def ishas(timetables, date):
    """
    Функция для поиска раписание.

    Parameters
    ----------
    timetables
        Объект раписание
    date
        дата
    chatId
        id чата.
    """
    for i in timetables:
        if i[0] == date:
            return i
    return False