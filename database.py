import json
import os.path
from operator import itemgetter
class DatabasesHelper:
    def __init__(self):
        self.encoding = 'utf-8'
        self.dirPath = 'databases/'
        self.tailPath = '.json'

    def createUserDatabase(self, chatId):
        """
        Функция проверяет, создана ли база для пользователя:
        Если база есть, возвращает False, т.е. база есть и не создана,
        Иначе создается база для пользователя,
        Устанавливаются первоначальные значения, и возвращается True - база создана.

        Parameters
        ----------
        chatId
            id чата.
        
        """
        filePath = self.dirPath + str(chatId) + self.tailPath
        if not os.path.isfile(filePath):
            with open(filePath, "w", encoding=self.encoding) as file:
                default = {
                    'prevMenuId': 0,
                    'status': 0,
                    'tasks': [],
                    'reminds': 'OFF',
                    'events': [],
                    'timetable':[],
                    'date':'',
                    'el':'',
                    'patterns':[],
                    'game_run': True,
                    'field': [],
                    'cross_count': 0
                }
                json.dump(default, file)
            return True
        else:
            return False

    def save(self, chatId, whatSave, newValue):
        """
        Функция сохранения новых данных в базу данных пользователя.
        Проверяется наличие базы, затем после считывания объекта,
        Данные обновляются на новые, и снова записываются в базу.
        True - если все прошло удачно и данные записаны,
        False - если произошла какая-то ошибка.

        Parameters
        ----------
        chatId
            id чата.
        whatSave
            Куда сохранить
        newValue
            Новое значение
        """
        chatId = str(chatId)
        try:
            data = {}
            filePath = self.dirPath + chatId + self.tailPath
            self.createUserDatabase(chatId)

            with open(filePath, 'r', encoding=self.encoding) as file:
                data = json.load(file)

            if whatSave == 'all':
                data = newValue
            else:
                data[whatSave] = newValue
            data["tasks"].sort(key=itemgetter('taskPrior'))
            with open(filePath, "w", encoding=self.encoding) as file:
                json.dump(data, file)
            return True
        except Exception as e:
            error = [e, "Open file error"]
            print(error)
            return False

    def get(self, chatId, whatGet):
        """
        Функция возвращает из базы данных
        Запрашиваемые значения.

        Parameters
        ----------
        chatId
            id чата.
        whatGet
            Что вернуть
        """
        self.createUserDatabase(chatId)
        filePath = self.dirPath + str(chatId) + self.tailPath
        data = {}
        try:
            with open(filePath, 'r', encoding=self.encoding) as file:
                data = json.load(file)
        except Exception:
            print(Exception)

        if whatGet == 'all':
                return data
        else:
            return data[whatGet]
