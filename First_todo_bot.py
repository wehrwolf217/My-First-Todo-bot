#! /usr/bin/env python3
#! /usr/bin/env python3

import datetime
import pickle

import telebot
from telebot import types

token = ''  # ваш токен

bot = telebot.TeleBot(token)

todo = {}

keyboard_main = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard_main.add('справка ❓', 'добавить задачу 📝', 'показать все задачи 📋', 'показать задачи на дату 📆',
                  'удалить 🗑', row_width=2)

keyboard_add = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard_add.add('добавить задачу 📝', 'сохранить 💾', 'назад 🔄', row_width=2)

keyboard_del = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard_del.add('удалить все задачи на дату 📑🚮', 'удалить одну задачу 📃🚮', 'назад 🔄', row_width=2)


@bot.message_handler(commands='start')
def bot_start(message):
    """начало работы бота подгружаем наш файлик и определяем пользователя,
     если был то его словарь если нет, то создаем новый"""
    name = message.from_user.first_name
    filename = f'./todo.txt'  # путь к файлу со словарем
    dict_name = message.from_user.id
    with open(filename, 'rb') as f:
        global todo
        todo = pickle.load(f)
        if dict_name in todo:
            msg = bot.send_message(message.chat.id, f'Добрый день {name}', reply_markup=keyboard_main)
            bot.register_next_step_handler(msg, process_step)
        else:
            msg = bot.send_message(message.chat.id, f'Приятно познакомиться {name}', reply_markup=keyboard_main)
            bot.register_next_step_handler(msg, process_step)
            todo[dict_name] = dict()
    return todo.update()


def process_step(message):
    """Свитчер"""
    if message.text == 'справка ❓':
        bot_help(message)
    elif message.text == 'добавить задачу 📝':
        todo_add(message)
    elif message.text == 'сохранить 💾':
        create_file(message)
    elif message.text == 'удалить 🗑':
        del_tasks(message)
    elif message.text == 'показать все задачи 📋':
        print_all(message)
    elif message.text == 'показать задачи на дату 📆':
        print_on_date(message)
    elif message.text == 'назад 🔄':
        msg = bot.send_message(message.chat.id, 'начнем сначала', reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, process_step)
    else:
        name = message.from_user.first_name
        msg = bot.send_message(message.chat.id, f'Добрый день {name}, я не понимаю чего вы от меня хотите',
                               reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, process_step)


def bot_help(message):
    """возможно в будущем будет информация о функциях, или контактах для связи..."""
    name = message.from_user.first_name
    msg = bot.send_message(message.chat.id, f'Добрый день {name}, я работаю только с командами из клавиатуры',
                           reply_markup=keyboard_main)
    bot.register_next_step_handler(msg, process_step)


def todo_add(message):
    """добавление задачи начинаем с получения даты(в дальнейшем неплохо бы на графический календарь переделать)"""
    msg = bot.reply_to(message, 'Введите дату день месяц год(пример: 28 01 2021): ')
    bot.register_next_step_handler(msg, process_enter_date)


def process_enter_date(message):
    """заполняем словарь в качестве ключа дата"""
    try:
        enter_date = message.text
        day, month, year = map(int, enter_date.split(' '))
        task_date = datetime.date(year, month, day)  # преобразуем ввод в дату
        msg = bot.reply_to(message, 'введите задачу: ')
        bot.register_next_step_handler(msg, lambda msg1: process_add_task(task_date, msg1))
    except ValueError:
        bot.reply_to(message, 'Неверный формат даты')
        msg = bot.reply_to(message, 'Введите дату день месяц год(пример: 28 01 2021): ')
        bot.register_next_step_handler(msg, process_enter_date)


def process_add_task(task_date, message):
    """продолжаем заполнять значение словаря(список)"""
    task = message.text
    dict_name = message.from_user.id
    if dict_name in todo.keys():
        if task_date in todo[dict_name].keys():
            todo[dict_name][task_date].append(task)
        else:
            todo[dict_name][task_date] = list()
            todo[dict_name][task_date].append(task)
    task_date_str = task_date.strftime('%d %m %Y')

    msg = bot.send_message(message.chat.id, f'Задание на дату {task_date_str}, добавлено.\nДля возможности '
                                            f'просмотра задачи в будущем, обязательно '
                                            f'нажмите\n*сохранить*', reply_markup=keyboard_add)
    bot.register_next_step_handler(msg, process_step)


def create_file(message):
    """сохраняет в файл изменения сделанные в словаре"""
    name = message.from_user.first_name
    filename = f'./todo.txt'
    with open(filename, 'wb') as f:
        pickle.dump(todo, f)
    msg = bot.send_message(message.chat.id, f'изменения сохранены для пользователя {name}', reply_markup=keyboard_main)
    bot.register_next_step_handler(msg, process_step)


def print_all(message):
    """выводит все задачи из словаря пользователя"""
    dict_name = message.from_user.id
    if todo[dict_name]:
        for t_date, tasks in sorted(todo[dict_name].items()):
            t_date = datetime.date.strftime(t_date, "%d-%m-%Y")  # преобразуем в формат даты снг
            string = str('\n'.join('%d  %s' % (i, s) for i, s in enumerate(tasks, 1)))
            bot.send_message(message.chat.id, f"Вот список задач на {t_date}:\n{string}")
        msg = bot.send_message(message.chat.id, f"Сделал дело, гуляй смело!", reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, process_step)
    else:
        msg = bot.send_message(message.chat.id, 'У вас еще нет задач', reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, process_step)


def print_on_date(message):
    """получаем дату на которую нужно распечатать задачи"""
    msg = bot.reply_to(message, 'Введите дату день месяц год(пример: 28 01 2021): ')
    bot.register_next_step_handler(msg, process_print_date)


def process_print_date(message):
    """выводит задачи на заданную дату"""
    try:
        dict_name = message.from_user.id
        enter_date = message.text
        day, month, year = map(int, enter_date.split(' '))
        task_date = datetime.date(year, month, day)
        if task_date in todo[dict_name]:
            tasks = todo[dict_name][task_date]
            string = str('\n'.join('%d  %s' % (i, t) for i, t in enumerate(tasks, 1)))
            t_date = datetime.date.strftime(task_date, "%d-%m-%Y")
            msg = bot.send_message(message.chat.id, f"Вот список задач на {t_date}:\n{string}",
                                   reply_markup=keyboard_main)
            bot.register_next_step_handler(msg, process_step)
        else:
            msg = bot.send_message(message.chat.id, 'У вас еще нет задач на эту дату', reply_markup=keyboard_main)
            bot.register_next_step_handler(msg, process_step)
    except ValueError:
        bot.reply_to(message, 'Неверный формат даты')
        msg = bot.reply_to(message, 'Введите дату день месяц год(пример: 28 01 2021): ')
        bot.register_next_step_handler(msg, process_print_date)


def del_tasks(message):
    """получаем дату на которую нужно распечатать задачи"""
    msg = bot.reply_to(message, 'Введите дату день месяц год(пример: 28 01 2021): ')
    bot.register_next_step_handler(msg, choice_del)


def choice_del(message):
    """выбираем что удалять(дату)"""
    try:
        dict_name = message.from_user.id
        enter_date = message.text
        day, month, year = map(int, enter_date.split(' '))
        task_date = datetime.date(year, month, day)
        if task_date in todo[dict_name]:
            tasks = todo[dict_name][task_date]
            string = str('\n'.join('%d  %s' % (i, t) for i, t in enumerate(tasks, 1)))
            t_date = datetime.date.strftime(task_date, "%d-%m-%Y")
            msg = bot.send_message(message.chat.id, f"Вот список задач на {t_date}:\n{string}",
                                   reply_markup=keyboard_del)
            bot.register_next_step_handler(msg, lambda msg1: process_del(task_date, msg1))
        else:
            msg = bot.send_message(message.chat.id, 'У вас еще нет задач на эту дату', reply_markup=keyboard_main)
            bot.register_next_step_handler(msg, process_step)
    except ValueError:
        bot.reply_to(message, 'Неверный формат даты')
        msg = bot.reply_to(message, 'Введите дату день месяц год(пример: 28 01 2021): ')
        bot.register_next_step_handler(msg, choice_del)


def process_del(task_date, message):
    """свичер для удаления, все задачи или по одной"""
    dict_name = message.from_user.id
    if message.text == 'удалить все задачи на дату 📑🚮':
        del todo[dict_name][task_date]
        todo.update()
        create_file(message)
    elif message.text == 'удалить одну задачу 📃🚮':
        msg = bot.send_message(message.chat.id, 'введите номер задачи из списка выше')
        bot.register_next_step_handler(msg, lambda msg1: del_one_task(task_date, msg1))
    elif message.text == 'назад 🔄':
        msg = bot.send_message(message.chat.id, 'начнем сначала', reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, process_step)


def del_one_task(task_date, message):
    """удаляем по 1й задаче в заданный день"""
    dict_name = message.from_user.id
    if message.text.isdigit() and int(message.text) != 0:
        task_num = int(message.text) - 1
        try:
            del todo[dict_name][task_date][task_num]
            if len(todo[dict_name][task_date]) == 0:
                del todo[dict_name][task_date]
                todo.update()
                create_file(message)
                bot.send_message(message.chat.id, f'задачи на эту дату удалены', reply_markup=keyboard_main)
            else:
                todo.update()
                create_file(message)
                tasks = todo[dict_name][task_date]
                string = str('\n'.join('%d  %s' % (i, t) for i, t in enumerate(tasks, 1)))
                t_date = datetime.date.strftime(task_date, "%d-%m-%Y")
                bot.send_message(message.chat.id, f"Вот список оставшихся задач на {t_date}:\n{string}",
                                 reply_markup=keyboard_main)
        except IndexError:
            msg = bot.send_message(message.chat.id, 'такого номера нет в списке', reply_markup=keyboard_main)
            bot.register_next_step_handler(msg, process_step)
    else:
        msg = bot.send_message(message.chat.id, 'мне нужен был всего лишь правильный номер', reply_markup=keyboard_main)
        bot.register_next_step_handler(msg, process_step)


bot.polling(none_stop=True)
