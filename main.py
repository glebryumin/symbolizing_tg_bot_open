from PIL import Image, ImageDraw, ImageFont
import telebot
from os import remove as os_remove
import telegraph
import sqlite3


def check_user(message):
    with sqlite3.connect('databases/settings.db') as con:
        if not con.cursor().execute(f'''SELECT id FROM users WHERE id = {message.chat.id}''').fetchall():
            con.cursor().execute(f'''INSERT INTO users(id) VALUES({message.chat.id})''')
        con.commit()


def get_data(message):
    with sqlite3.connect(database_path) as con:
        result = con.execute(f'''SELECT size, gradient, format 
           FROM users 
           WHERE id = {message.chat.id}''').fetchall()[0]
        if result:
            size = result[0]
            gradient = result[1]
            format_file = result[2]
        return size, gradient, format_file


def settings_markup(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Размер картинки', callback_data='size'))
    markup.add(telebot.types.InlineKeyboardButton('Градиент', callback_data='gradient'))
    markup.add(telebot.types.InlineKeyboardButton('Формат возвращаемой картинки', callback_data='format'))
    markup.add(telebot.types.InlineKeyboardButton('Выйти из настроек', callback_data='leave'))
    bot.edit_message_text('Выберите настройку:', reply_markup=markup, message_id=message.id,
                          chat_id=message.chat.id)


bot = telebot.TeleBot('6483574316:AAHvoiRFMXQIAF4_W-QGpJuKpmLdktCiOLI')
graph = telegraph.Telegraph()
database_path = 'databases/settings.db'
gradients = {'standard': " `.'_~:!/r?(l1Zё4h9W8$@", 'standard-invert': '@$8W9h4ёZ1l(r/!:. ',
             'huge': ''' .'^,:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$''',
             'huge-invert': '''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,^`. '''}
temp_size = 70
temp_gradient = 'standard'
temp_format = 'telegraph'
print('Successfully started!')


@bot.message_handler(commands=['start'])
def start_message(message):
    print(f'Sent start message to {message.from_user.username}')
    bot.reply_to(message, 'Привет! Я - бот, который переделывает картинки в текстовые файли и пасты. '
                          'У меня есть различные форматы и виды символов. Для помощи - /help.')
    check_user(message)


@bot.message_handler(commands=['help'])
def help_message(message):
    print(f'Sent help message to {message.from_user.username}')
    bot.reply_to(message, '/start - краткая инфа о боте.\n'
                          '/settings - настройки бота, сохраняются после выхода из, собственно, настроек.\n'
                          'Просто любое сообщение без картинки - <strike>направление в дурку</strike>'
                          ' совет отправить картинку.\n'
                          'Картинка - картинка из символов по заданным настройкам.\n'
                          '---------------------------------\n'
                          'Важное уточнение: Паста 16:30 выглядит плохо, как фиксить не знаю. '
                          'Вопрос по формату 1:1 - делать пиксель:символ или размер:размер? '
                          'При втором варианте теряется качество, при первом - слишком большая картинка.'
                          'Картинки выского разрешения тоже выглядят не очень.', parse_mode='html')
    check_user(message)


@bot.message_handler(commands=['settings'])
def settings_message(message):
    check_user(message)
    global temp_size
    global temp_gradient
    global temp_format
    result = get_data(message)
    temp_size = result[0]
    temp_gradient = list(gradients.keys())[list(gradients.values()).index(result[1])]
    temp_format = result[2]
    print(f'Sent settings message to {message.from_user.username}')
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Размер картинки', callback_data='size'))
    markup.add(telebot.types.InlineKeyboardButton('Градиент', callback_data='gradient'))
    markup.add(telebot.types.InlineKeyboardButton('Формат возвращаемой картинки', callback_data='format'))
    markup.add(telebot.types.InlineKeyboardButton('Выйти из настроек', callback_data='leave'))
    bot.reply_to(message, 'Текущие настройки:\n'
                          f'Размер: {temp_size}\n'
                          f'Градиент: {temp_gradient}\n'
                          f'Формат: {temp_format}\n'
                          'Выберите настройку:', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global temp_size
    global temp_gradient
    global temp_format
    markup = telebot.types.InlineKeyboardMarkup()
    sett = callback.data.split('_')
    if sett[0] == 'size':
        if sett[-1] == '70':
            temp_size = 70
            callback.data = 'return'
        elif sett[-1] == '210':
            temp_size = 210
            callback.data = 'return'
        elif sett[-1] == '1':
            temp_size = 1
            callback.data = 'return'
        elif sett[-1] == 'paste':
            temp_size = 16
            callback.data = 'return'
        elif sett[-1] == 'custom':
            temp_size = 70
            callback.data = 'return'
        else:
            markup.add(telebot.types.InlineKeyboardButton('Стандартный (Ширина = 70, Высота уменьшена пропорционально)',
                                                          callback_data='size_70'))
            markup.add(telebot.types.InlineKeyboardButton('Увеличенный в 3 раза относительно стандартного',
                                                          callback_data='size_210'))
            markup.add(telebot.types.InlineKeyboardButton('1:1', callback_data='size_1'))
            markup.add(telebot.types.InlineKeyboardButton('Паста (16 x 30)', callback_data='size_paste'))
            markup.add(telebot.types.InlineKeyboardButton('Свой (WIP🛠️)', callback_data='size_custom'))
            markup.add(telebot.types.InlineKeyboardButton('Вернуться', callback_data='return'))
            bot.edit_message_text('Выберите размер:', reply_markup=markup, message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)

    if sett[0] == 'gradient':
        if sett[-1] == 'standard':
            temp_gradient = 'standard'
            callback.data = 'return'
        elif sett[-1] == 'standard-invert':
            temp_gradient = 'standard-invert'
            callback.data = 'return'
        elif sett[-1] == 'huge':
            temp_gradient = 'huge'
            callback.data = 'return'
        elif sett[-1] == 'huge-invert':
            temp_gradient = 'huge-invert'
            callback.data = 'return'
        elif sett[-1] == 'custom':
            temp_gradient = 'standard'
            callback.data = 'return'
        else:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton('Стандартный', callback_data='gradient_standard'))
            markup.add(telebot.types.InlineKeyboardButton('Стандартный инвертированный',
                                                          callback_data='gradient_standard-invert'))
            markup.add(telebot.types.InlineKeyboardButton('Увеличенный', callback_data='gradient_huge'))
            markup.add(telebot.types.InlineKeyboardButton('Увеличенный инвертированный',
                                                          callback_data='gradient_huge-invert'))
            markup.add(telebot.types.InlineKeyboardButton('Свой (WIP🛠️)', callback_data='gradient_custom'))
            markup.add(telebot.types.InlineKeyboardButton('Вернуться', callback_data='return'))
            bot.edit_message_text('Выберите градиент:', reply_markup=markup, message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)

    if sett[0] == 'format':
        if sett[-1] == 'txt':
            temp_format = 'txt'
            callback.data = 'return'
        elif sett[-1] == 'telegraph':
            temp_format = 'telegraph'
            callback.data = 'return'
        elif sett[-1] == 'png':
            temp_format = 'png'
            callback.data = 'return'
        else:
            markup.add(telebot.types.InlineKeyboardButton('Текстовик', callback_data='format_txt'))
            markup.add(telebot.types.InlineKeyboardButton('Телеграф', callback_data='format_telegraph'))
            markup.add(telebot.types.InlineKeyboardButton('Картинка .png', callback_data='format_png'))
            markup.add(telebot.types.InlineKeyboardButton('Вернуться', callback_data='return'))
            bot.edit_message_text('Выберите формат:', reply_markup=markup, message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)

    if callback.data == 'return':
        settings_markup(callback.message)

    if callback.data == 'leave':
        if temp_size and temp_gradient and temp_format:
            with sqlite3.connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = {temp_size},
                gradient = "{gradients[temp_gradient]}",
                format = "{temp_format}" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            print(f'Changed settings for {callback.message.chat.username}')
            bot.edit_message_text('Натройки сохранены.', message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)
        else:
            bot.edit_message_text('Натройки НЕ сохранены. Настройка была прервана, начните заново.',
                                  message_id=callback.message.id, chat_id=callback.message.chat.id)


@bot.message_handler()
def await_message(message):
    check_user(message)
    print(f'Sent await message to {message.from_user.username} with text: {message.text}')
    bot.reply_to(message, 'Отправь фото для преобразования, /start для получения краткой инфы.')


@bot.message_handler(content_types=['photo'])
def symbolize(message):
    result = get_data(message)
    size = result[0]
    gradient = result[1]
    format_file = result[2]
    raw = message.photo[2].file_id
    path = raw + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f'photos/{path}', 'wb+') as new_file:
        new_file.write(downloaded_file)
    with open(f'photos/{raw}.txt', encoding='utf-8', mode='w+') as f:
        im = Image.open(f'photos/{path}')
        im = im.quantize(len(gradient))
        full_list_ = list()
        if size != 1:
            k = im.size[0] / size
            im = im.resize((size, int(im.size[1] // (k * 2))) if size != 16 else (16, 30))
            pixels = im.load()
            for y in range(im.size[1]):
                row_list_ = list()
                for x in range(im.size[0]):
                    row_list_.append(gradient[pixels[x, y]])
                full_list_.append(''.join(row_list_))
            krt = '\n'.join(full_list_)
            f.write(krt)
        else:
            pixels = im.load()
            for y in range(0, im.size[1] - 9, 9):
                row_list_ = list()
                for x in range(0, im.size[0] - 3, 3):
                    s = [pixels[x + i, y + j] for i in range(3) for j in range(9)]
                    row_list_.append(gradient[int(sum(s) / len(s))])
                full_list_.append(''.join(row_list_))
            krt = '\n'.join(full_list_)
            f.write(krt)
    if format_file == 'telegraph':
        graph.create_account(short_name='kog')
        response = graph.create_page('Картиночка (символьная)',
                                     html_content='<pre>' + krt.replace('\n', '<br>') + '</pre>')
        bot.reply_to(message=message, text=response['url'])
        print(f'Sent image to {message.from_user.username} with result: {response["url"]}')
    elif format_file == 'txt':
        with open(f'photos/{raw}.txt', 'rb') as f:
            bot.send_document(message.chat.id, document=f)
        print(f'Sent image to {message.from_user.username} with result on .txt')
    elif format_file == 'png':
        img = Image.new('RGB', (len(krt.split('\n')[0]) * 3, len(krt.split('\n')) * 9), color=(255, 255, 255))
        ImageDraw.Draw(img).text((0, 0), krt, fill=(0, 0, 0), font=ImageFont.truetype('DejaVuSansMono.ttf', size=5))
        img.save(f'photos/{raw}.png')
        with open(f'photos/{raw}.png', 'rb') as f:
            bot.send_photo(chat_id=message.chat.id, photo=f)
        os_remove(f'photos/{raw}.png')
        print(f'Sent image to {message.from_user.username} with result on .png')

    os_remove(f'photos/{path}')
    os_remove(f'photos/{raw}.txt')


@bot.message_handler(content_types=["audio", "document", "sticker", "video", "video_note", "voice", "location",
                                    "contact"])
def wrong_content_message(message):
    check_user(message)
    print(f'Sent wrong content message to {message.from_user.username} with text: {message.text}')
    bot.reply_to(message, 'Вы отправили не тот формат файла. Пожалуйста отправьте фото (не файлом, просто выбрать '
                          'из галереии).')


bot.infinity_polling()
