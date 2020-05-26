import telebot
from database import DatabasesHelper

# Системные настройки
token = "1099791052:AAGY096bFEz11Xf-VACxfBCCGCdOA8Vv_BU"
# Объекты
bot = telebot.TeleBot(token, threaded=False)
databaseHelper = DatabasesHelper()

# Универсальные кнопки
goBack = "Назад"
goMainMenu = "В главное меню"
# Кнопки для главного меню
tasksListLabel = "Список дел"
eventsLabel = "Мероприятия"
timeTableLabel = "Расписание"

# Кнопки для меню Список дел
addTaskLabel = "Добавить задачу"
doneLabel = 'Выполнено ✅'

# Кнопки для меню Расписания
addTimetable = 'Создать расписание'

remindsLabel = 'Напоминания /'

# Другие кнопки
addEventLabel = "Добавить мероприятие"

# Стандартные сообщения
mainMenuMessage = "Чем займемся?"
deleteTaskMessage = 'Кликни на задачу, чтобы удалить!'
nothingForDelete = 'Удалять больше нечего'
helpMessage = "тебе серьезно нужна помощь, чтобы осилить бота? F."
whatDoYouWantAdd = "Что добавим в список дел?"
isAddedTask = 'Задача добавлена!'
emptyQuery = "Не пиши ерунды :)"

schedule = "Ваше расписание"
selectDate = "Пожалуйста, выберите дату"
enterTimeSubject ='Введите: время(16:00) и предмет(Программная инженерия)'
delete = 'Удалить'
change = "Изменить"
whatToDo = 'Что cделать?'


# Стикеры
stickers = ['static/img/frogita_1.tgs', 'static/img/frogita_2.tgs',
            'static/img/frogita_3.tgs', 'static/img/frogita_4.tgs',
            'static/img/frogita_5.tgs', 'static/img/frogita_6.tgs']
# ID разделов меню
IDmainMenu = 0
IDshowTasksMenu = 1
IDaddTask = 2
IDshowEventMenu = 3
IDaddEvent = 4
IDshowTimetableMenu = 5
IDaddSubject = 6
