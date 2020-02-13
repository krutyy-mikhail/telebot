from collections import defaultdict
import re

from telebot import apihelper, TeleBot
import requests

import storage
import keyboards

PLACES = defaultdict(dict)

def get_place(user_id):
    return PLACES[user_id]


def update_place(user_id, key, value):
    PLACES[user_id][key] = value

# Initializing bot

TOKEN = '870497401:AAHKxkNYPf-xwWqT6kyTJ7yPaL2AO1SHNqo'
PROXIES = {'https': 'socks5://110.49.101.58:1080'}

bot = TeleBot(TOKEN)
apihelper.proxy = PROXIES

# Handling command 'start'

@bot.message_handler(commands=['start'])
def handle_start(message):
    text = ('Привет!\n'
            'Я сохраню все Ваши любимые места.'
            'Я Вам понравлюсь')
    bot.send_message(chat_id=message.chat.id, text=text)

# Handling command 'help'

@bot.message_handler(commands=['help'])
def handle_help(message):
    text = ('Вот что я умею:\n\n'
            '/help - получить помощь;\n'
            '/add - сохранить свое любимое место;\n'
            '/list - отобразить все свои любимые места;\n'
            '/reset - очистить список своих любимых мест.\n\n'
            'Ну что начнем!')
    bot.send_message(chat_id=message.chat.id, text=text)

# Handling command 'add'

@bot.message_handler(commands=['add'])
def handle_adding(message):
    keyboard = keyboards.create_cancel_keyboard()

    bot.send_message(chat_id=message.chat.id,
                     text='Нажмите на кнопку "Отмена", если передумали добавлять место.')
    bot.send_message(chat_id=message.chat.id,
                     text='Введите название места.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_name_place)


def handle_name_place(message):
    keyboard = keyboards.create_cancel_keyboard()

    if message.content_type != 'text':
        bot.send_message(chat_id=message.chat.id,
                         text='Необходимо указать текст',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_name_place)
        return
    update_place(message.chat.id, 'name_place', message.text)
    bot.send_message(chat_id=message.chat.id,
                     text='Укажите место на карте.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_location)


def handle_location(message):
    keyboard = keyboards.create_cancel_keyboard()

    if message.content_type != 'location':
        bot.send_message(chat_id=message.chat.id,
                         text='Необходимо указать место на карте',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_location)
        return
    update_place(message.chat.id, 'location', message.location)
    bot.send_message(chat_id=message.chat.id,
                     text='Прикрепите фото.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_photo)


def handle_photo(message):
    if message.content_type != 'photo':
        bot.send_message(chat_id=message.chat.id,
                         text='Необходимо прикрепить фото',)
        bot.register_next_step_handler(message, handle_photo)
        return

    if message.media_group_id:
        bot.send_message(chat_id=message.chat.id,
                         text='Необходимо прикрепить только одно фото.')
        bot.register_next_step_handler(message, handle_photo)
        return

    update_place(message.chat.id, 'photo', message.photo[0].file_id)
    keyboard = keyboards.create_confirmation_keyboard('add')
    place = get_place(message.chat.id)
    text = 'Вы действительно хотите сохранить место "{}"?'
    name_place = place['name_place']
    bot.send_message(chat_id=message.chat.id,
                     text=text.format(name_place),
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in {'add_y', 'add_n'})
def handle_confirmation(call):
    message = call.message
    if call.data == 'add_y':
        text = 'Место успешно сохранено!'
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
        bot.send_message(chat_id=message.chat.id,
                         text='Ожидайте, идет процесс сохранения...')

        place = get_place(message.chat.id)
        if not storage.get_user(message.chat.id):
            storage.insert_user((message.chat.id,))

        photo_id = place['photo']
        photo_path = bot.get_file(photo_id).file_path
        url_file = 'https://api.telegram.org/file/bot{0}/{1}'

        try:
            photo = requests.get(url_file.format(TOKEN, photo_path),
                                 proxies=PROXIES)
        except:
            text = 'Что то пошло не так, начните процесс ввода места заново.'
        else:
            storage.insert_place((place['name_place'], photo.content,
                                 place['location'].latitude,
                                 place['location'].longitude,
                                 message.chat.id))
    elif call.data == 'add_n':
        text = 'Добавление нового места было отменено!'
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
    bot.send_message(chat_id=message.chat.id, text=text)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_adding(call):
    message = call.message
    bot.delete_message(chat_id=message.chat.id,
                       message_id=message.message_id)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.send_message(chat_id=message.chat.id,
                     text='Добавление места отменено!')

# Handling command 'list'

@bot.message_handler(commands=['list'])
def show_places(message):
    places = storage.get_places_for_user(message.chat.id)

    if places:
        count_places = len(places)
        keyboard = keyboards.create_pagination_keyboard(count_places)

        _, name, photo, latitude, longitude = places[0]

        bot.send_location(chat_id=message.chat.id,
                          latitude=latitude, longitude=longitude,
                          reply_markup=keyboard)
    else:
        text = 'У Вас нет сохраненных мест.'
        bot.send_message(chat_id=message.chat.id, text=text)

@bot.callback_query_handler(func=lambda call: call.data in {str(index) for index in range(1, 31)})
def show_next_place(call):
    is_image = False
    message = call.message
    places = storage.get_places_for_user(message.chat.id)
    count_places = len(places)
    pages = {index + 1: places[index] for index in range(count_places)}

    call.data = int(call.data)

    if call.data - count_places > 0 and call.data <= count_places * 2:
        call.data = call.data - count_places
        is_image = True

    if call.data - count_places > 0 and call.data <= count_places * 3:
        call.data = call.data - count_places * 2
        place_id = pages[call.data][0]
        storage.delete_place(place_id)
        places = storage.get_places_for_user(message.chat.id)
        count_places = len(places)
        pages = {index + 1: places[index] for index in range(count_places)}
        call.data = 1

    if pages:
        keyboard = keyboards.create_pagination_keyboard(count_places, call.data, is_image)
        place = pages[call.data]
        _, name, photo, latitude, longitude = place
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        if is_image:
            bot.send_photo(chat_id=message.chat.id, photo=photo,
                           reply_markup=keyboard, caption=name)
        else:
            bot.send_location(chat_id=message.chat.id,
                              latitude=latitude, longitude=longitude,
                              reply_markup=keyboard)
    else:
        text = 'У Вас нет сохраненных мест.'
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(chat_id=message.chat.id, text=text)

# Handling command 'reset'

@bot.message_handler(commands=['reset'])
def coinfirm_reset_places(message):
    keyboard = keyboards.create_confirmation_keyboard('reset')
    text = 'Вы действительно хотите удалить все свои места?'
    if storage.get_places_for_user(message.chat.id):
        bot.send_message(chat_id=message.chat.id,
                         text=text,
                         reply_markup=keyboard)
    else:
        text = 'У Вас нет сохраненных мест.'
        bot.send_message(chat_id=message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: call.data in {'reset_y', 'reset_n'})
def reset_places(call):    
    message = call.message
    if call.data == 'reset_y':
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)
        storage.delete_places_for_user(message.chat.id)
        text = 'Все места успешно удалены.'

    elif call.data == 'reset_n':
        text = 'Удаление всех мест отменено.'
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message.message_id)

    bot.send_message(chat_id=message.chat.id, text=text)

def handle_unsupported_command(messages):
    allowed_commands = ['/start', '/help', '/add', '/reset', '/list']
    for message in messages:
        if message.text not in allowed_commands:
            bot.send_message(chat_id=message.chat.id,
                             text='Данная команда не поддерживается.')

bot.set_update_listener(handle_unsupported_command)