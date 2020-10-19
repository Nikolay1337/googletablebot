from _datetime import datetime
import collections
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
import telebot
from telebot import types

mybot = telebot.TeleBot('TOKEN_BOT')
global dateperiod1
global dateperiod2


@mybot.message_handler(commands=['start'])
def messages(message):
    mybot.send_message(message.chat.id, 'Привет, ' + message.chat.first_name + '.', reply_markup=buttons())


def buttons():
    button1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1.row('Задать период', 'Сортировка')
    return button1


def inlinekeyboard():
    butt = types.InlineKeyboardMarkup()
    butt.row(types.InlineKeyboardButton('Новые', callback_data='Новых'),
             types.InlineKeyboardButton('Старые', callback_data='Старых'))
    return butt


@mybot.callback_query_handler(func=lambda call: True)
def feedbackstart(call):
    sp = list()
    peoplelist = list()
    p = ''
    date1 = datetime(int(dateperiod1.split('.')[2]), int(dateperiod1.split('.')[1]), int(dateperiod1.split('.')[0]))
    date2 = datetime(int(dateperiod2.split('.')[2]), int(dateperiod2.split('.')[1]), int(dateperiod2.split('.')[0]))
    for i in parsing():
        if len(i) == 4:
            if date1 <= datetime(int(i[3].split('.')[2]), int(i[3].split('.')[1]), int(i[3].split('.')[0])) <= date2:
                peoplelist.append(i)
        else:
            mybot.send_message(call.message.chat.id, 'Кривая строка ' + str(i) + '. \nНачинайте всё сначала. /start')
    if call.data == 'Новых':
        k = sorted([i for i in peoplelist if i.count('новая') > 0], key=lambda x: x[0])
        for i in k:
            sp.append(i[0])
        for i in collections.Counter(sp).most_common():
            p += str(i[0]) + ' ' + str(i[1]) + '\n'
        mybot.send_message(call.message.chat.id, 'Новых: \n' + str(len(k)) + '\n' + 'Из них:\n' + p)
    elif call.data == 'Старых':
        k = sorted([i for i in peoplelist if i.count('старая') > 0], key=lambda x: x[0])
        for i in k:
            sp.append(i[0])
        for i in collections.Counter(sp).most_common():
            p += str(i[0]) + ' ' + str(i[1]) + '\n'
        mybot.send_message(call.message.chat.id, 'Старых: \n' + str(len(k)) + '\n' + 'Из них:\n' + p)


@mybot.message_handler(content_types=['text'])
def mess(message):
    if message.text == 'Задать период':
        mybot.send_message(message.chat.id, 'Период задаётся в формате: 01.02.2020-31.04.2020')
    elif message.text == 'Сортировка':
        mybot.send_message(message.chat.id, 'По клиентам:', reply_markup=inlinekeyboard())
    else:
        mybot.send_message(message.chat.id, 'Период задан. \nВыберите пункт "Сортировка"', reply_markup=buttons())
        periodmonth(message.text)


def parsing():
    CREDENTIALS_FILE = 'ProjectGoogleTable-6fb0a8a106c1.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    spreadsheet_id = '1eK_rP6bd8XH1mlE4BrVyFGvNnO693_EuTzQ4cNdljcA'
    values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='A1:D')
    response = values.execute()
    table = list(response.values())[2][1:]
    return table


def periodmonth(text):
    datalist = text.split('-')
    global dateperiod1
    dateperiod1 = datalist[0]
    global dateperiod2
    dateperiod2 = datalist[1]


mybot.polling(none_stop=True, interval=0)
