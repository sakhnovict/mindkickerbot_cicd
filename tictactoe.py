import random
import telebot
from telebot import types

import config
from config import bot
from config import databaseHelper

#Обработка нажатия кнопок
def new_game(message):
    field = []
    listCol = []
    for row in range(3):
        for col in range(3):
            listCol.append('⬜️')
        field.append(listCol)
        listCol = [] 
    databaseHelper.save(message.chat.id, 'game_run', True)
    databaseHelper.save(message.chat.id, 'cross_count', 0)
    databaseHelper.save(message.chat.id, 'field', field)
    return field

def click(row, col, chat_id,message_id):
    field = databaseHelper.get(chat_id, 'field')
    game_run = databaseHelper.get(chat_id, 'game_run')
    if game_run and field[row][col] == '⬜️':
        field[row][col] = '❌'
        databaseHelper.save(chat_id, 'field', field)

        cross_count = databaseHelper.get(chat_id, 'cross_count')
        cross_count += 1
        databaseHelper.save(chat_id, 'cross_count', cross_count)

        check_win('❌', chat_id)
        game_run = databaseHelper.get(chat_id, 'game_run')
        if game_run and cross_count < 5:
            computer_move(chat_id, field)
            check_win('⭕️', chat_id)
        if cross_count >= 5:
            bot.send_message(chat_id=chat_id, text='Ничья '+  '\nНажми на кнопку "Новая игра", если ночешь сыкрать еще раз\nИли на кнопку "Назад", если хочешь вернутся в гланое меню', reply_markup=None)
            

    databaseHelper.save(chat_id, 'field', field)       
    showField(chat_id,message_id)
    
            
#Проверка победы
def check_win(smb, chat_id):
    field = databaseHelper.get(chat_id, 'field')
    for n in range(3):
        check_line(field[n][0], field[n][1], field[n][2], smb, chat_id)
        check_line(field[0][n], field[1][n], field[2][n], smb, chat_id)
    check_line(field[0][0], field[1][1], field[2][2], smb, chat_id)
    check_line(field[2][0], field[1][1], field[0][2], smb, chat_id)

def check_line(a1, a2, a3, smb, chat_id):
    if a1 == smb and a2 == smb and a3 == smb:
        game_run = databaseHelper.get(chat_id, 'game_run')
        game_run = False
        databaseHelper.save(chat_id, 'game_run', game_run)
        bot.send_message(chat_id=chat_id, text='Победил '+ smb + '\nНажми на кнопку "Новая игра", если ночешь сыкрать еще раз\nИли на кнопку "Назад", если хочешь вернутся в гланое меню', reply_markup=None)

def showField(chat_id,message_id=0, var = 0):
    field = databaseHelper.get(chat_id, 'field')
    markup = types.InlineKeyboardMarkup(row_width=3)
    row = []
    for i in range(3):
        for j in range(3):
            row.append(telebot.types.InlineKeyboardButton(field[i][j], callback_data='btn_click'+ ';' + str(i) + ';' + str(j)+ ';' + field[i][j]))
        markup.row(*row)
        row = []
    if var == 0 :
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Ваш ход', reply_markup=markup)
    elif var == 1:
        bot.send_message(chat_id=chat_id, text='Ваш ход', reply_markup=markup)
        

#действия компьютера
def can_win(field, smb, chat_id, col=[0,1,2], row=[0,1,2]):
    res = False
    if field[col[0]][row[0]] == smb and field[col[1]][row[1]] == smb and field[col[2]][row[2]] == ' ':
        field[col[2]][row[2]] = '⭕️'
        databaseHelper.save(chat_id, 'field', field)   
        res = True
    if field[col[0]][row[0]] == smb and field[col[1]][row[1]] == ' ' and field[col[2]][row[2]] == smb:
        field[col[1]][row[1]] = '⭕️'
        databaseHelper.save(chat_id, 'field', field) 
        res = True
    if field[col[0]][row[0]] == ' ' and field[col[1]][row[1]] == smb and field[col[2]][row[2]] == smb:
        field[col[0]][row[0]] = '⭕️'
        databaseHelper.save(chat_id, 'field', field)
        res = True
    return res

def computer_move(chat_id, field):
    for n in range(3):
        if can_win(field, '⭕️',chat_id, col=[n,n,n]):
            return 
        if can_win(field, '⭕️', chat_id, row=[n,n,n]):
            return 
    if can_win(field, '⭕️', chat_id):
        return 
    if can_win(field, '⭕️', chat_id,col=[2,1,0], row=[0,1,2]):
        return
    for n in range(3):
        if can_win(field, '❌',chat_id, col=[n,n,n]):
            return 
        if can_win(field, '❌', chat_id, row=[n,n,n]):
            return
    if can_win(field, '❌', chat_id):
        return
    if can_win(field, '❌', chat_id, col=[2,1,0], row=[0,1,2]):
        return
    while True:
        row = random.randint(0, 2)
        col = random.randint(0, 2)
        if field[row][col] == '⬜️':
            field[row][col] = '⭕️'
            databaseHelper.save(chat_id, 'field', field)
            break


def startTTT(message):
    status = 12
    databaseHelper.save(message.chat.id, 'status', status)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttonNewGame = telebot.types.KeyboardButton('Новая игра')
    goMainMenu = telebot.types.KeyboardButton(config.goMainMenu)
    markup.add(buttonNewGame, goMainMenu)
    bot.send_message(chat_id=message.chat.id, text='Добро пожаловать в игру "крестики-нолики"\nПравила просты:\n1.Ты - ❌, соперник - ⭕️\n2.Соберешь три-в-ряд и ты победил\nНажми на кнопку "Новая игра" и играй', reply_markup=markup)


def start_new_game(message):
    chat_id = message.chat.id
    message_id = message.message_id
    status = databaseHelper.get(chat_id, 'status')
    if status == 12:

        field = new_game(message)
        showField(chat_id, message_id, var=1)
    return True
    
    

def callback_game(call):
    data = call.data.split(';')
    if data[0] == 'btn_click':
        try:
            click(int(data[1]), int(data[2]), call.message.chat.id,call.message.message_id)
        except:
            print('Мне было лень отлавливать ошибки')
    return True


