import datetime
import collections
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials
import telebot


mybot = telebot.TeleBot('1208352709:AAFlDEkHHonwjIkb32i9X9IvfK4jpqVBbsU')
global dateperiod1
global dateperiod2


@mybot.message_handler(commands=['start'])
def messages(message):
    mybot.send_message(message.chat.id, 'Привет, ' + message.chat.first_name + '.\n'
                                        'Введи период в формате: 01.01.2019-31.12.2020.\n'
                                        'Четвертый столбец должен быть заполнен dd/mm/yyyy,\n'
                                        'во втором столбце поиск строго по "старая/новая",\n'
                                        'иначе строки с неправильным форматом не будут учтены.',
                       reply_markup=buttons())


def buttons():
    button1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1.row('Выбрать тип клиентов')
    return button1


def inlinekeyboard():
    butt = telebot.types.InlineKeyboardMarkup()
    butt.row(telebot.types.InlineKeyboardButton('Новые', callback_data='Новых'),
             telebot.types.InlineKeyboardButton('Старые', callback_data='Старых'))
    return butt


@mybot.callback_query_handler(func=lambda call: True)
def feedbackstart(call):
    sp = list()
    peoplelist = list()
    p = ''
    if 'dateperiod1' in globals():
        date1 = datetime.datetime(int(dateperiod1.split('.')[2]), int(dateperiod1.split('.')[1]),
                                  int(dateperiod1.split('.')[0]))
        date2 = datetime.datetime(int(dateperiod2.split('.')[2]), int(dateperiod2.split('.')[1]),
                                  int(dateperiod2.split('.')[0]))
        for i in parsing():
            if len(i) == 4 and i[3].count('.') == 2 and len(i[3]) == 10:
                if date1 <= datetime.datetime(int(i[3].split('.')[2]), int(i[3].split('.')[1]),
                                              int(i[3].split('.')[0])) <= date2:
                    peoplelist.append(i)
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
    else:
        mybot.send_message(call.message.chat.id, 'Я тебя не понимаю :( \nПериод задаётся в формате: '
                                                 '01.02.2020-31.04.2020',
                           reply_markup=buttons())


@mybot.message_handler(content_types=['text'])
def mess(message):
    if message.text == 'Выбрать тип клиентов':
        mybot.send_message(message.chat.id, 'По клиентам:', reply_markup=inlinekeyboard())
    elif len(message.text) == 21 and message.text.count('.') == 4:
        mybot.send_message(message.chat.id, 'Период задан. \nНажми "Выбрать тип клиентов"', reply_markup=buttons())
        periodmonth(message.text)
    else:
        mybot.send_message(message.chat.id, 'Я тебя не понимаю :( \nПериод задаётся в формате: 01.02.2020-31.04.2020',
                           reply_markup=buttons())


def parsing():
    credentials_file = 'ProjectGoogleTable-6fb0a8a106c1.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpauth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpauth)

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
