# telegram libs
import telebot
from telebot import types
# other libs
import random
# config
import config
from config import bot
from config import databaseHelper

import calendar
import datetime as dt
from timetable import separateCallbackData, createCallbackData
#from operator import itemgetter

def generateDeadline(task):
    """
    Функция генерации дедлайна
    
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
            return "\n"

        date = dt.datetime(year=int(dateYear), month=int(dateMonth), day=int(dateDays))
        now = dt.datetime.now()
        delta = date - now
        # print(delta)
        if delta.days < 7:
            warning = ""
            if delta.days == 7:
                warning = "| 7️⃣ дней до дедлайна 🔥\n"
            elif delta.days == 6:
                warning = "| 6️⃣ дней до дедлайна 🔥\n"
            elif delta.days == 5:
                warning = "| 5️⃣ дней до дедлайна 🔥\n"
            elif delta.days == 4:
                warning = "| 4️⃣ дня до дедлайна 🔥\n"
            elif delta.days == 3:
                warning = "| 3️⃣ дня до дедлайна 🔥\n"
            elif delta.days == 2:
                warning = "| 2️⃣ дня до дедлайна 🔥\n"
            elif delta.days == 1:
                warning = "| 1️⃣ день до дедлайна 🔥\n"
            else:
                warning = "| 0️⃣ дедлайн просрочен 🔥\n"
            return warning
        else:
            return "\n"
    else:
        warning += "\n"
        return warning


def showTasks(message):
    """
    Функция для показа списка дел, и клавиатуры,
    С возможностью добавления задач, а также инлайн-клавиатуры
    Для возможности удаления задач.

    Parameters
    ----------
    message
        Объект message
    """
    # keyboard
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    addTaskButton = types.KeyboardButton(config.addTaskLabel)
    goMainMenuButton = types.KeyboardButton(config.goMainMenu)
    markup.add(addTaskButton, goMainMenuButton)
    # working with json
    currentChatId = message.chat.id
    databaseHelper.save(currentChatId, 'prevMenuId', 0)
    databaseHelper.save(currentChatId, 'status', 0)
    # sending
    tasks = databaseHelper.get(currentChatId, 'tasks')
    botMessage = ""
    if len(tasks) <= 0:
        botMessage = "<b>Вот твой список дел 📋😎:</b>\n\n"
        botMessage += "<i>Ты тоже заметил, что он пуст?</i>"
    elif len(tasks) <= 5:
        botMessage = "<b>Вот твой список дел 📋😎:</b>\n"
    else:
        botMessage = "<b>Вот твой список дел 📋😥:</b>\n"
    bot.send_message(message.chat.id, botMessage, reply_markup=markup, parse_mode='html')

    # tasks.sort(key=itemgetter('taskPrior'))
    # print(tasks)
    if len(tasks) > 0:
        tasksMessage = ""
        for number, task in enumerate(tasks, 1):
            tasksMessage += "<b><i>%s.</i></b> %s" % (number, task["description"])
            # print(task)
            # print(generateDeadline(task))
            tasksMessage += generateDeadline(task)

        inlineMarkup = types.InlineKeyboardMarkup(row_width=1)
        crumbButton = types.InlineKeyboardButton('☰', callback_data='editTasks')
        inlineMarkup.add(crumbButton)
        bot.send_message(message.chat.id, tasksMessage, reply_markup=inlineMarkup, parse_mode='html')
    else:
        pass


def tasksCallback(call):
    """
    Функция-обработчик инлайн событий
    Для задач: вывод задач и иконки,
    Удаление задач и возвращение назад к списку.

    Parameters
    ----------
    call
        Объект call
    """
    # working with json
    currentChatId = call.message.chat.id
    tasks = databaseHelper.get(currentChatId, 'tasks')

    checkData = ""
    try:
        checkData = separateCallbackData(call.data)
    except Exception:
        checkData = "error"
        print("Error separating...")

    if checkData[0] == "XDAY":
        taskDate = checkData[3] + '.' + '0' + checkData[2] + '.' + checkData[1]
        id = checkData[4]
        # print(id)
        taskDate = str(dt.datetime.strptime(taskDate, '%d.%m.%Y').date())
        newTasks = tasks
        task = tasks[int(id) - 1]

        newTask = {
                    "description": task["description"],
                    "date": taskDate,
                    "taskPrior": task["taskPrior"]
                }
        newTasks.pop(int(id) - 1)
        newTasks.insert(0, newTask)
        databaseHelper.save(currentChatId, 'tasks', newTasks)
        createTasksDoneMarkup(call, newTasks)

    elif (checkData[0] == 'XPREV-MONTH'):
        if(int(checkData[2]) == 1):
            markup = createCalendar(int(checkData[1]) - 1, 12, id = checkData[4])
        else:
            markup = createCalendar(int(checkData[1]), int(checkData[2]) - 1, id = checkData[4])

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пожалуйста, выберите дату", reply_markup=markup)

    elif (checkData[0] == 'XNEXT-MONTH'):
        if(int(checkData[2]) == 12):
            markup = createCalendar(int(checkData[1]) + 1, 1, id = checkData[4])
        else:
            markup = createCalendar(int(checkData[1]), int(checkData[2]) + 1, id = checkData[4])

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пожалуйста, выберите дату", reply_markup=markup)

    elif call.data == 'editTasks':
        # sending
        createTasksDoneMarkup(call, tasks)

    elif call.data == 'tasksEditDone':
        # tasks.sort(key=itemgetter('taskPrior'))
        if len(tasks) > 0:
            tasksMessage = ""
            for number, task in enumerate(tasks, 1):
                tasksMessage += f"<b><i>{number}.</i></b> {task['description']}"

                tasksMessage += generateDeadline(task)

            inlineMarkup = types.InlineKeyboardMarkup(row_width=1)
            crumbButton = types.InlineKeyboardButton('☰', callback_data='editTasks')
            inlineMarkup.add(crumbButton)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=tasksMessage,
                                reply_markup=inlineMarkup,
                                parse_mode='html')
        else:
            botMessage = "<i>Ты тоже заметил, что он пуст?</i>"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id = call.message.message_id,
                                text=botMessage,
                                reply_markup=None,
                                parse_mode='html')
    elif call.data.find('EditTaskID=') != -1:
        newTasks = tasks
        for number, task in enumerate(tasks, 1):
            EditTaskId = "EditTaskID=" + str(number)
            delTaskId = ""
            setDeadLineId = ""
            setPriorId = ""
            if call.data == EditTaskId:
                delTaskId = "DelTaskID=" + str(number)
                setDeadLineId = "DeadLineTaskID=" + str(number)
                setPriorId = "PriorTaskID=" + str(number)

                setDeadlineButton = types.InlineKeyboardButton("Установить дедлайн", callback_data=setDeadLineId)
                setPriorButton = types.InlineKeyboardButton("Поставить приоритет", callback_data=setPriorId)
                deleteButton = types.InlineKeyboardButton("Удалить задачу", callback_data=delTaskId)
                doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data='editTasks')

                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(setDeadlineButton, setPriorButton, deleteButton)
                markup.row(doneButton)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                                message_id = call.message.message_id,
                                                text="Настрой задачу под себя!",
                                                reply_markup=markup)
                break
    elif call.data.find('DeadLineTaskID=') != -1:
        newTasks = tasks
        for number, task in enumerate(tasks, 1):
            deadlineTaskId = "DeadLineTaskID=" + str(number)
            EditTaskId = "EditTaskID=" + str(number)
            if call.data == deadlineTaskId:
                markup = createCalendar(id=str(number))
                doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data=EditTaskId)
                clearDeadline = types.InlineKeyboardButton("Убрать дедлайн", callback_data=f'CleadDeadLineID={number}')
                markup.row(clearDeadline)
                markup.row(doneButton)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id = call.message.message_id, text=config.selectDate, reply_markup=markup)

                break
    elif call.data.find('CleadDeadLineID=') != -1:
        newTasks = tasks
        for number, task in enumerate(tasks, 1):
            cleardeadlineTaskId = "CleadDeadLineID=" + str(number)
            EditTaskId = "EditTaskID=" + str(number)
            if call.data == cleardeadlineTaskId:
                task = newTasks[int(number) - 1]
                newTask = {
                            "description": task["description"],
                            "date": "no date",
                            "taskPrior": task["taskPrior"]
                        }
                newTasks.pop(int(number) - 1)
                newTasks.insert(0, newTask)
                databaseHelper.save(currentChatId, 'tasks', newTasks)
                createTasksDoneMarkup(call, newTasks)
                break

    elif call.data.find('PriorTaskID=') != -1:
        newTasks = tasks
        for number, task in enumerate(tasks, 1):
            priorTaskId = "PriorTaskID=" + str(number)
            EditTaskId = "EditTaskID=" + str(number)
            if call.data == priorTaskId:
                doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data=EditTaskId)
                markup = types.InlineKeyboardMarkup(row_width=3)
                oneBtn = types.InlineKeyboardButton("1", callback_data=f'setPriorID={number}=1')
                twoBtn = types.InlineKeyboardButton("2", callback_data=f'setPriorID={number}=2')
                threeBtn = types.InlineKeyboardButton("3", callback_data=f'setPriorID={number}=3')
                markup.add(oneBtn, twoBtn, threeBtn)
                markup.row(doneButton)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                                message_id = call.message.message_id,
                                                text="1 - Очень важно, 2 - важно, 3 - наименее важно",
                                                reply_markup=markup)
                break
    elif call.data.find('setPriorID=') != -1:
        newTasks = tasks
        for number, task in enumerate(tasks, 1):
            priorTaskId = "setPriorID=" + str(number)
            if call.data[:-2] == priorTaskId:
                prior = call.data[len(call.data) - 1]

                task = newTasks[number - 1]
                newTask = {
                    "description": task["description"],
                    "date": task["date"],
                    "taskPrior": int(prior)
                }
                newTasks.pop(number - 1)
                newTasks.insert(0, newTask)
                databaseHelper.save(currentChatId, 'tasks', newTasks)
                createTasksDoneMarkup(call, newTasks)
                break
    elif call.data.find('DelTaskID=') != -1:
        newTasks = tasks
        for number, task in enumerate(tasks, 1):
            delTaskId = "DelTaskID=" + str(number)
            if call.data == delTaskId:
                # delete task
                newTasks.pop(number - 1)
                databaseHelper.save(currentChatId, 'tasks', newTasks)
                # sending
                tasks = databaseHelper.get(currentChatId, 'tasks')
                if len(tasks) > 0:
                    createTasksDoneMarkup(call, tasks)
                else:
                    doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data='tasksEditDone')
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    markup.add(doneButton)
                    bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id = call.message.message_id,
                                        text=config.nothingForDelete,
                                        reply_markup=markup)
                break
    else:
        pass

def createTasksDoneMarkup(call, tasks):
    """
    Функция для генерации инлайн клавиатуры с
    Кнопками задач и кнопкой выполнено!

    Parameters
    ----------
    call
        Объект call
    tasks
        задания
    """
    tasksItems = []
    #tasks.sort(key=itemgetter('taskPrior'))
    for number, task in enumerate(tasks, 1):
        item = types.InlineKeyboardButton(f"{number}. {task['description']}", callback_data=f"EditTaskID={number}")
        tasksItems.append(item)
    doneButton = types.InlineKeyboardButton(config.doneLabel, callback_data='tasksEditDone')
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*tasksItems)
    markup.row(doneButton)
    bot.edit_message_text(chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=config.deleteTaskMessage,
                        reply_markup=markup)

def addTask(message):
    """
    Задает статус для добавления задачи
    В базу данных, а также создает клавиатуру.

    Parameters
    ----------
    message
        Объект message
    
    """
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    goBackButton = types.KeyboardButton(config.goBack)
    markup.add(goBackButton)
    bot.send_message(message.chat.id, config.whatDoYouWantAdd, reply_markup=markup)
    # working with json
    currentChatId = message.chat.id
    prevID = config.IDshowTasksMenu
    status = 1
    databaseHelper.save(currentChatId, 'prevMenuId', prevID)
    databaseHelper.save(currentChatId, 'status', status)


def createCalendar(year=None, month=None, id=None):
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

    now = dt.datetime.now()
    if year == None:
        year = now.year
    if month == None:
        month = now.month
    if id == None:
        id = "X"
    data_ignore = createCallbackData("IGNORE", year, month, 0)

    markup.row(telebot.types.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore))

    row = []

    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append(telebot.types.InlineKeyboardButton(
            day, callback_data=data_ignore))
    markup.add(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if(day == 0):
                row.append(telebot.types.InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(telebot.types.InlineKeyboardButton(str(day), callback_data=createCallbackData("XDAY", year, month, day, id)))
        markup.add(*row)

    row = []
    markup.row(*[telebot.types.InlineKeyboardButton("<", callback_data=createCallbackData("XPREV-MONTH", year, month, day, id)),
                telebot.types.InlineKeyboardButton(" ",callback_data=data_ignore),
                telebot.types.InlineKeyboardButton(">",callback_data=createCallbackData("XNEXT-MONTH", year, month, day, id))])

    return markup

def addTaskDone(message):
    """
    Добавляет задачу в список дел пользователя
    Если активен статус добавления, т.е. status == 1

    
    Parameters
    ----------
    message
        Объект message
    """
    # working with json
    currentChatId = message.chat.id
    status = databaseHelper.get(currentChatId, 'status')
    if status == 1:
        tasks = databaseHelper.get(currentChatId, 'tasks')
        task = message.text
        # if task.find("*") != -1:
        #     taskDescription = task.split("*")[0]
        #     taskDate = task.split("*")[1]
        #     try:
        #         taskDate = str(dt.datetime.strptime(taskDate, '%d.%m.%Y').date())
        #     except Exception:
        #         print("Date error.")
        # else:
        #     taskDate = "no date"
        # if task.find("[") != -1:
        #     taskPrior = int(task.split("[")[1][:-1])
        # else:
        #     taskPrior = 3

        # taskDescription = task.split("*")[0].split("[")[0]

        newTask = {
            "description": task,
            "date": "no date",
            "taskPrior": 3
        }

        tasks.insert(0, newTask)
        databaseHelper.save(currentChatId, 'tasks', tasks)
        bot.send_message(message.chat.id, config.isAddedTask, reply_markup=None)
        showTasks(message)
        return True
    else:
        return False
