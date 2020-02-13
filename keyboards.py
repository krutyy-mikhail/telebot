from telebot import types

def create_cancel_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key_cancel = types.InlineKeyboardButton(text='Отмена',
                                            callback_data='cancel')
    keyboard.add(key_cancel)

    return keyboard


def create_confirmation_keyboard(operation):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да',
                                         callback_data=operation + '_y')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет',
                                        callback_data=operation + '_n')
    keyboard.add(key_no)

    return keyboard


def create_pagination_keyboard(count_pages, active_index=1, is_image=False):
    keyboard = types.InlineKeyboardMarkup(row_width=count_pages)
    if is_image:
        text_photo = '<Фото>'
        text_location = 'Место'
    else:
        text_photo = 'Фото'
        text_location = '<Место>'

    key_location = types.InlineKeyboardButton(text=text_location,
                                              callback_data=active_index)
    key_photo = types.InlineKeyboardButton(text=text_photo,
                                           callback_data=active_index + count_pages)

    keyboard.add(key_location, key_photo)

    key_delete = types.InlineKeyboardButton(text='Удалить',
                                            callback_data=active_index + count_pages * 2)
    keyboard.add(key_delete)
    keys = []
    for index in range(1, count_pages + 1):
        if active_index == index:
            text = '{}{}{}'.format('<', index, '>')
        else:
            text = index
        key = types.InlineKeyboardButton(text=text,
                                         callback_data=index)
        keys.append(key)
    keyboard.add(*keys)

    return keyboard
