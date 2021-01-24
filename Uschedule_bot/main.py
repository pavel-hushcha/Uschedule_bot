# -*- coding: utf-8 -*-

import telebot
import os
import re
import datetime
import sql
import parsing
import keyboard
import display
from apscheduler.schedulers.background import BackgroundScheduler

# get tokens from token file if it exist or from environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path, encoding='utf-8-sig') as env:
        for i in env:
            k, v = i.rstrip().split("=")
            os.environ[k] = v

# variables
token = os.environ.get("TOKEN")
database_url = os.environ.get("DATABASE_URL")
first_semestr = "https://www.polessu.by/ruz/cab/"
second_semestr = "https://www.polessu.by/ruz/cab/term2/"
semestr = second_semestr

bot = telebot.TeleBot(token)
keyboard = keyboard.Keyboard(bot)
sql = sql.Sql(database_url)
sql.create_user_position()


# start message
@bot.message_handler(commands=["start"])
def handle_text(message):
    user_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    user_keyboard.row("Ввести полное название группы / преподавателя / аудитории:")
    user_keyboard.row("Поиск названия группы / преподавателя / аудитории:")
    start_message = "Вас приветствует бот показа расписания занятий в Полесском государственном " \
                    "университете. Для вывода расписания вы должны сделать выбор:"
    bot.send_message(message.from_user.id, start_message, reply_markup=user_keyboard)


# returns to main menu handler
@bot.message_handler(func=lambda message: "Главное меню" == message.text, content_types=['text'])
def handle_text(message):
    keyboard.main_menu(message)
    sql.clear_getting_position(str(message.from_user.id))   # clear the user_id in user_position table


# returns to search schedule menu handler
@bot.message_handler(func=lambda message: "Назад" == message.text, content_types=['text'])
def handle_text(message):
    keyboard.schedule_menu(message)


# search the name of group and teacher menu handler
@bot.message_handler(func=lambda message: "Поиск названия группы / преподавателя / аудитории:" == message.text,
                     content_types=["text"])
def handle_text(message):
    search_message = "Для поиска введите не менее 3 символов:"
    msgname = bot.send_message(message.chat.id, search_message)
    bot.register_next_step_handler(msgname, search_name_group)


# search the name of group or teacher in the list of them
def search_name_group(message):
    search_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    search_keyboard.row("Главное меню")
    sample_name_group = message.text.lower()
    search_markup = telebot.types.InlineKeyboardMarkup()
    if len(sample_name_group) > 2:  # check for minimum 3 symbols searching
        list_name_group = ""
        list_teachers = parsing.list_all(semestr)
        for piece in list_teachers:
            if sample_name_group in piece.lower():  # create keyboard with found teachers
                search_markup.add(telebot.types.InlineKeyboardButton  # call == index of teacher in teacher's list
                                  (text=piece, callback_data=list_teachers.index(piece)))
                list_name_group += piece
        if list_name_group:
            bot.send_message(message.chat.id, "Результат поиска:", reply_markup=search_markup)
        else:
            bot.send_message(message.chat.id, "Поиск не дал результатов, попробуйте уточнить критерии.")
            keyboard.main_menu(message)
    else:
        bot.send_message(message.chat.id, "Введите не менее 3 символов для поиска!")
        keyboard.main_menu(message)


# collecting the name of group or teacher handler
@bot.message_handler(func=lambda message: "Ввести полное название группы / преподавателя / аудитории:" == message.text,
                     content_types=["text"])
def handle_text(message):
    sql.set_getting_position(str(message.chat.id))
    find_message = "Введите, пожалуйста, полное название группы (например, 18ММТ-1), преподавателя " \
                   "(например, Иванов Иван Иванович) или аудитории (например, 220):"
    msgname = bot.send_message(message.chat.id, find_message)
    bot.register_next_step_handler(msgname, save_name_group)


# save the name of group or teacher for continuous search
def save_name_group(message):
    name_group = message.text
    if name_group not in parsing.list_all(semestr):
        bot.send_message(message.chat.id, "Такой группы / преподавателя / аудитории нет в университете."
                                          " Попробуйте воспользоваться поиском.")
        keyboard.main_menu(message)
    else:
        if not parsing.list_weeks(name_group, semestr):
            bot.send_message(message.chat.id, "Занятия отсутствуют.")
            sql.clear_getting_position(str(message.chat.id))
            keyboard.main_menu(message)
        else:
            sql.set_search_position(str(message.chat.id), name_group)
            keyboard.schedule_menu(message)


# main search menu handler
@bot.message_handler(func=lambda message: "Расписание на сегодняшний день" == message.text or
                                          "Расписание на завтрашний день" == message.text or
                                          "Расписание на неделю" == message.text, content_types=["text"])
# display the today and tomorrow schedule of lessons
def handle_text(message):
    name = sql.verification(str(message.chat.id))
    now = datetime.datetime.now().date().strftime("%d-%m-%Y")

    if message.text == "Расписание на сегодняшний день":
        lessons = display.check_return_lessons(name, semestr)
        today_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        today_keyboard.row("Назад")
        today_keyboard.row("Главное меню")
        today_message = now + ":" + "\n\n" + display.display_schedule(name, now, lessons)
        bot.send_message(message.chat.id, today_message, reply_markup=today_keyboard)

    if message.text == "Расписание на завтрашний день":
        lessons = display.check_return_lessons(name, semestr)
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        tomorrow_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        tomorrow_keyboard.row("Назад")
        tomorrow_keyboard.row("Главное меню")
        tomorrow_message = tomorrow + ":" + "\n\n" + display.display_schedule(name, tomorrow, lessons)
        bot.send_message(message.chat.id, tomorrow_message, reply_markup=tomorrow_keyboard)

    if message.text == "Расписание на неделю":
        week_markup = telebot.types.InlineKeyboardMarkup()
        weeks = parsing.list_weeks(name, semestr)
        for day in weeks:
            week_markup.add(telebot.types.InlineKeyboardButton(text=day[0:6] + now[-2:] + day[6:] + now[-2:],
                                                               callback_data=day[0:2] + "-" + day[3:5] + "-"
                                                                             + now[-4:]))
        bot.send_message(message.chat.id, "Выберите необходимую Вам неделю", reply_markup=week_markup)


# schedule week of lessons handler
@bot.callback_query_handler(func=lambda call: True)
# display the schedule of week lessons
def handle_query(call):
    if call.data.isdigit():
        list_teachers = parsing.list_all(semestr)
        if not parsing.list_weeks(list_teachers[int(call.data)], semestr):
            bot.send_message(call.message.chat.id, "Занятия отсутствуют.")
            keyboard.main_menu(call)
        else:
            sql.set_getting_position(str(call.message.chat.id))
            sql.set_search_position(str(call.message.chat.id), list_teachers[int(call.data)])
            keyboard.schedule_menu(call)
    else:
        name = sql.verification(str(call.message.chat.id))
        lessons = display.check_return_lessons(name, semestr)
        back_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        back_keyboard.row("Назад")
        back_keyboard.row("Главное меню")
        days = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота"}
        monday = datetime.datetime.strptime(call.data, "%d-%m-%Y")
        for day_schedule in range(0, 6):
            dayz = datetime.datetime.strftime(monday + datetime.timedelta(days=day_schedule), "%d-%m-%Y")
            bot.send_message(call.message.chat.id, f"{days.get(day_schedule)} {dayz}:")
            display_day = display.display_schedule(name, dayz, lessons)
            if display_day:
                bot.send_message(call.message.chat.id, display_day)
        bot.send_message(call.message.chat.id, "Выберите пункт меню:", reply_markup=back_keyboard)


# everyday update the database
def update_base():
    for item in parsing.list_all(semestr):
        if parsing.list_weeks(item, semestr):
            sql.delete_table(item)
            if re.match(r"\d\d[А-Я]", item) or re.match(r"[А-Я]{2}-\d\d", item):
                sql.insert_lessons_group(parsing.make_schedule_for_teacher(item, semestr),
                                         parsing.pars_changes(semestr))
            else:
                sql.insert_lessons_teacher(parsing.make_schedule_for_teacher(item, semestr),
                                           parsing.pars_changes(semestr))


# scheduler of database updating at 4-00 AM everyday
scheduler = BackgroundScheduler()
scheduler.add_job(update_base, trigger="cron", hour=4, minute=0)
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass

if __name__ == '__main__':
    bot.infinity_polling()
