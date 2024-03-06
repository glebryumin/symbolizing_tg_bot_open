from os import remove as os_remove
from sqlite3 import connect
from PIL import Image, ImageDraw, ImageFont
from telebot import TeleBot, types
from telegraph import Telegraph
from dotenv import dotenv_values


def check_user(message):
    with connect('databases/settings.db') as con:
        if not con.cursor().execute(f'''SELECT id FROM users WHERE id = {message.chat.id}''').fetchall():
            con.cursor().execute(f'''INSERT INTO users(id) VALUES({message.chat.id})''')
        con.commit()


def get_data(message):
    with connect(database_path) as con:
        result = con.execute(f'''SELECT size, gradient, format 
           FROM users 
           WHERE id = {message.chat.id}''').fetchall()[0]
        if result:
            size = result[0]
            gradient = result[1]
            format_file = result[2]
        return size, gradient, format_file


def symbolize(size, gradient, format_file, raw, path):
    with open(f'photos/{raw}.txt', encoding='utf-8', mode='w+') as f:
        im = Image.open(f'photos/{path}')
        im = im.quantize(len(gradient))
        full_list_ = list()
        if format_file == 'telegraph':
            im = im.resize((70, im.size[1] // ((im.size[0] // 70) * 2)))
            pixels = im.load()
            for y in range(im.size[1]):
                row_list_ = list()
                for x in range(im.size[0]):
                    row_list_.append(gradient[pixels[x, y]])
                full_list_.append(''.join(row_list_))
            krt = '\n'.join(full_list_)
            f.write(krt)
            graph.create_account(short_name='kog')
            response = graph.create_page('Картиночка (символьная)',
                                         html_content='<pre>' + krt.replace('\n', '<br>') + '</pre>')
            return response
        else:
            im = im.resize(sizes[size]) if size != '1:1' else im
            pixels = im.load()
            for y in range(0, im.size[1] - 9, 9):
                row_list_ = list()
                for x in range(0, im.size[0] - 3, 3):
                    s = [pixels[x + i, y + j] for i in range(3) for j in range(9)]
                    row_list_.append(gradient[int(sum(s) / len(s))])
                full_list_.append(''.join(row_list_))
            krt = '\n'.join(full_list_)
            f.write(krt)
            return krt


def settings_markup(message):
    check_user(message)
    result = get_data(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Размер картинки', callback_data='size'))
    markup.add(types.InlineKeyboardButton('Градиент', callback_data='gradient'))
    markup.add(types.InlineKeyboardButton('Формат возвращаемой картинки', callback_data='format'))
    markup.add(types.InlineKeyboardButton('Выйти из настроек', callback_data='leave'))
    bot.edit_message_text('Настройки обновены.\n'
                          'Текущие настройки:\n'
                          f'Размер: {result[0]}\n'
                          f'Градиент: {list(gradients.keys())[list(gradients.values()).index(result[1])]}\n'
                          f'Формат: {result[2]}\n'
                          'Выберите настройку:', reply_markup=markup, message_id=message.id,
                          chat_id=message.chat.id)


environment = dotenv_values('enviroment.env')
bot = TeleBot(environment['BOT_TOKEN'])
database_path = environment['DATABASE_PATH']
graph = Telegraph()
gradients = {'standard': " `.'_~:!/r?(l1Zё4h9W8$@", 'standard-invert': '@$8W9h4ёZ1l(r/!:. ',
             'huge': ''' .'^,:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$''',
             'huge-invert': '''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,^`. '''}
sizes = {'5:4': (1280, 1024), '4:3': (1024, 768), '3:2': (720, 480), '8:5': (1440, 900), '5:3': (1280, 768),
         '16:9': (1920, 1080), '1:1': '1:1'}
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
                          'Бот ещё недоделан, планируется переделывание в видео,'
                          ' кастомные размеры и кастомные градиенты.', parse_mode='html')
    check_user(message)


@bot.message_handler(commands=['settings'])
def settings_message(message):
    check_user(message)
    result = get_data(message)
    print(f'Sent settings message to {message.from_user.username}')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Размер картинки', callback_data='size'))
    markup.add(types.InlineKeyboardButton('Градиент', callback_data='gradient'))
    markup.add(types.InlineKeyboardButton('Формат возвращаемой картинки', callback_data='format'))
    markup.add(types.InlineKeyboardButton('Выйти из настроек', callback_data='leave'))
    bot.reply_to(message, 'Текущие настройки:\n'
                          f'Размер: {result[0]}\n'
                          f'Градиент: {list(gradients.keys())[list(gradients.values()).index(result[1])]}\n'
                          f'Формат: {result[2]}\n'
                          'Выберите настройку:', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    markup = types.InlineKeyboardMarkup()
    sett = callback.data.split('_')
    if sett[0] == 'size':
        if sett[-1] == '5:4':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "5:4" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == '4:3':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "4:3" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == '3:2':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "3:2" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == '8:5':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "8:5"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == '5:3':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "5:3"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == '16:9':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "16:9"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == '1:1':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users 
                SET size = "1:1" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'size_custom':
            # custom
            callback.data = 'return'
        else:
            markup.add(types.InlineKeyboardButton('5:4 (1280 x 1024)',
                                                  callback_data='size_5:4'))
            markup.add(types.InlineKeyboardButton('4:3 (1024 x 768)',
                                                  callback_data='size_4:3'))
            markup.add(types.InlineKeyboardButton('3:2 (720 x 480)',
                                                  callback_data='size_3:2'))
            markup.add(types.InlineKeyboardButton('8:5 (1440 x 900)',
                                                  callback_data='size_8:5'))
            markup.add(types.InlineKeyboardButton('5:3 (1280 x 768)',
                                                  callback_data='size_5:3'))
            markup.add(types.InlineKeyboardButton('16:9 (1920 x 1080)',
                                                  callback_data='size_16:9'))
            markup.add(types.InlineKeyboardButton('1:1 (без изменений)', callback_data='size_1:1'))
            markup.add(types.InlineKeyboardButton('Свой (WIP🛠️)',
                                                  callback_data='size_custom'))
            markup.add(types.InlineKeyboardButton('Вернуться', callback_data='return'))
            bot.edit_message_text('Выберите размер для картинки:', reply_markup=markup, message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)

    if sett[0] == 'gradient':
        if sett[-1] == 'standard':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                gradient = "{gradients['standard']}"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'standard-invert':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                gradient = "{gradients['standard-invert']}"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'huge':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                gradient = "{gradients['huge']}"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'huge-invert':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                gradient = "{gradients['huge-invert']}"
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'custom':
            # custom
            callback.data = 'return'
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Стандартный', callback_data='gradient_standard'))
            markup.add(types.InlineKeyboardButton('Стандартный инвертированный',
                                                  callback_data='gradient_standard-invert'))
            markup.add(types.InlineKeyboardButton('Увеличенный', callback_data='gradient_huge'))
            markup.add(types.InlineKeyboardButton('Увеличенный инвертированный',
                                                  callback_data='gradient_huge-invert'))
            markup.add(types.InlineKeyboardButton('Свой (WIP🛠️)', callback_data='gradient_custom'))
            markup.add(types.InlineKeyboardButton('Вернуться', callback_data='return'))
            bot.edit_message_text('Выберите градиент:', reply_markup=markup, message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)

    if sett[0] == 'format':
        if sett[-1] == 'txt':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                format = "txt" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'telegraph':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                format = "telegraph" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        elif sett[-1] == 'png':
            with connect(database_path) as con:
                con.cursor().execute(f'''UPDATE users SET
                format = "png" 
                WHERE id = {callback.message.chat.id}''')
                con.commit()
            callback.data = 'return'
        else:
            markup.add(types.InlineKeyboardButton('Текстовик', callback_data='format_txt'))
            markup.add(types.InlineKeyboardButton('Телеграф (ограничения по размеру)',
                                                  callback_data='format_telegraph'))
            markup.add(types.InlineKeyboardButton('Картинка .png', callback_data='format_png'))
            markup.add(types.InlineKeyboardButton('Вернуться', callback_data='return'))
            bot.edit_message_text('Выберите формат:', reply_markup=markup, message_id=callback.message.id,
                                  chat_id=callback.message.chat.id)

    if callback.data == 'return':
        settings_markup(callback.message)

    if callback.data == 'leave':
        print(f'Changed settings for {callback.message.chat.username}')
        bot.edit_message_text('Натройки сохранены.', message_id=callback.message.id,
                              chat_id=callback.message.chat.id)


@bot.message_handler()
def await_message(message):
    check_user(message)
    print(f'Sent await message to {message.from_user.username} with text: {message.text}')
    bot.reply_to(message, 'Отправь фото для преобразования,\n/start для получения краткой инфы,\n'
                          '/settings для настройки,\n/help для помощи')


@bot.message_handler(content_types=['photo'])
def symbolize_message(message):
    result = get_data(message)
    raw = message.photo[2].file_id
    path = raw + ".jpg"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f'photos/{path}', 'wb+') as new_file:
        new_file.write(downloaded_file)
    outcome = symbolize(result[0], result[1], result[2], raw, path)
    if result[2] == 'telegraph':
        bot.reply_to(message=message, text=outcome['url'])
        print(f'Sent image to {message.from_user.username} with result: {outcome["url"]}')
    if result[2] == 'txt':
        with open(f'photos/{raw}.txt', 'rb') as f:
            bot.send_document(message.chat.id, document=f)
        print(f'Sent image to {message.from_user.username} with result on .txt')
    elif result[2] == 'png':
        img = Image.new('RGB', (len(outcome.split('\n')[0]) * 3, len(outcome.split('\n')) * 9), color=(255, 255, 255))
        ImageDraw.Draw(img).text((0, 0), outcome, fill=(0, 0, 0), font=ImageFont.truetype('DejaVuSansMono.ttf', size=5))
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
