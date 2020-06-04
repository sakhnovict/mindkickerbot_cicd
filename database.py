from operator import itemgetter
import pymongo
from pymongo import MongoClient

class DatabasesHelper:
    def __init__(self):
        self.encoding = 'utf-8'
        self.mongoUrl = "mongodb+srv://vic:1234@cluster0-l0zc3.mongodb.net/test?retryWrites=true&w=majority"
        self.client = MongoClient(self.mongoUrl)
        self.db = self.client.users


    def find_document(self, collection, elements, multiple=False):
        """ Function to retrieve single or multiple documents from a provided
        Collection using a dictionary containing a document's elements.
        """
        if multiple:
            results = collection.find(elements)
            return [r for r in results]
        else:
            return collection.find_one(elements)

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
        chatId = str(chatId)

        collectionsList = self.db.list_collection_names()

        if chatId not in collectionsList:
            default = {
                '_id': chatId,
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
            newCollection = self.db[chatId]
            newCollection.insert_one(default)

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
            self.createUserDatabase(chatId)
            data = self.find_document(self.db[chatId], {"_id": chatId})

            
            data[whatSave] = newValue
            data["tasks"].sort(key=itemgetter('taskPrior'))
            self.db[chatId].update_one({"_id": chatId}, {'$set': {whatSave: newValue}})

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
        chatId = str(chatId)
        self.createUserDatabase(chatId)
        data = {}

        try:
            data = self.find_document(self.db[chatId], {"_id": chatId})
        except Exception:
            print(Exception)
        
        if whatGet == 'all':
                return data
        else:
            return data[whatGet]
