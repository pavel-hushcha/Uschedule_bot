import telebot
import os
import re
import datetime
import sql
import parsing
import keyboard
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
    user_keyboard.row("Поиск полного названия группы / преподавателя / аудитории:")
    start_message = "Вас приветствует бот показа расписания занятий в Полесском государственном " \
                    "университете. Для вывода расписания вы должны сделать выбор:"
    bot.send_message(message.from_user.id, start_message, reply_markup=user_keyboard)


@bot.message_handler(func=lambda message: "Главное меню" == message.text, content_types=['text'])
def handle_text(message):
    keyboard.main_menu(message)
    sql.clear_getting_position(str(message.from_user.id))  # _____________разобраться с таблицей (очищать значения)


@bot.message_handler(func=lambda message: "Назад" == message.text, content_types=['text'])
def handle_text(message):
    keyboard.schedule_menu(message)


@bot.message_handler(func=lambda message: "Поиск полного названия группы / преподавателя / аудитории:" == message.text,
                     content_types=["text"])
def handle_text(message):
    search_message = "Для поиска введите не менее 3 символов:"
    msgname = bot.send_message(message.chat.id, search_message)
    bot.register_next_step_handler(msgname, search_name_group)


def search_name_group(message):
    search_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    search_keyboard.row("Главное меню")
    sample_name_group = message.text
    if len(sample_name_group) > 2:
        list_name_group = ""
        for piece in parsing.list_all(semestr):
            if sample_name_group in piece:
                list_name_group += str(piece) + "\n"
        if list_name_group:
            bot.send_message(message.chat.id, "Результат поиска:")
            bot.send_message(message.chat.id, list_name_group, reply_markup=search_keyboard)
        else:
            bot.send_message(message.chat.id, "Поиск не дал результатов, попробуйте уточнить критерии.")
            keyboard.main_menu(message)
    else:
        bot.send_message(message.chat.id, "Введите не менее 3 символов для поиска!")
        keyboard.main_menu(message)


@bot.message_handler(func=lambda message: "Ввести полное название группы / преподавателя / аудитории:" == message.text,
                     content_types=["text"])
def handle_text(message):
    sql.set_getting_position(str(message.chat.id))
    find_message = "Введите, пожалуйста, полное название группы (например, 18ММТ-1), преподавателя " \
                   "(например, Иванов Иван Иванович) или аудитории (например, 220):"
    msgname = bot.send_message(message.chat.id, find_message)
    bot.register_next_step_handler(msgname, save_name_group)


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


@bot.message_handler(func=lambda message: "Расписание на сегодняшний день" == message.text or
                                          "Расписание на завтрашний день" == message.text or
                                          "Расписание на неделю" == message.text, content_types=["text"])
def handle_text(message):
    name = sql.verification(str(message.chat.id))
    now = datetime.datetime.now().date().strftime("%d-%m-%Y")
    date_changes = parsing.pars_changes(semestr)
    parsing_schedule = parsing.make_schedule_for_teacher(name, semestr)
    if not sql.check_table(name):
        if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
            sql.insert_lessons_group(parsing_schedule, date_changes)
        else:
            sql.insert_lessons_teacher(parsing_schedule, date_changes)

    def display_schedule(date):
        main_back_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        main_back_keyboard.row("Назад")
        main_back_keyboard.row("Главное меню")
        date_table = datetime.datetime.strptime(sql.read_date(name), "%Y-%m-%d %H:%M:%S")
        if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
            if date_table == date_changes:
                lessons = sql.read_lessons_group(name)
            else:
                sql.delete_table(name)
                sql.insert_lessons_group(parsing_schedule, date_changes)
                lessons = sql.read_lessons_group(name)
        else:
            if date_table == date_changes:
                lessons = sql.read_lessons_teacher(name)
            else:
                sql.delete_table(name)
                sql.insert_lessons_teacher(parsing_schedule, date_changes)
                lessons = sql.read_lessons_teacher(name)
        display_schedule = ""
        if date in lessons:
            for part in lessons.get(date):  # проверка на день есть ли расписание
                if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
                    display_schedule += f"{part[0]} | {part[1]} | {part[2]} | {part[3]} | {part[4]}"
                    display_schedule += "\n"
                else:
                    display_schedule += f"{part[0]} | {part[1]} | {part[2]} | {part[3]}"
                    display_schedule += "\n"
        else:
            display_schedule += "Занятия отсутствуют."
        return display_schedule

    if message.text == "Расписание на сегодняшний день":
        today_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        today_keyboard.row("Назад")
        today_keyboard.row("Главное меню")
        today_message = "Расписание на сегодня " + now + ":" + "\n\n" + display_schedule("08-02-2021")
        bot.send_message(message.chat.id, today_message, reply_markup=today_keyboard)

    if message.text == "Расписание на завтрашний день":
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        tomorrow_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        tomorrow_keyboard.row("Назад")
        tomorrow_keyboard.row("Главное меню")
        tomorrow_message = "Расписание на завтра " + tomorrow + ":" + "\n\n" + display_schedule("09-02-2021")
        bot.send_message(message.chat.id, tomorrow_message, reply_markup=tomorrow_keyboard)

    if message.text == "Расписание на неделю":
        week_markup = telebot.types.InlineKeyboardMarkup()
        weeks = parsing.list_weeks(name, semestr)
        for day in weeks:
            week_markup.add(telebot.types.InlineKeyboardButton(text=day[0:6] + now[-2:] + day[6:] + now[-2:],
                                                               callback_data=day[0:2] + "-" + day[3:5] + "-"
                                                                             + now[-4:]))
        bot.send_message(message.chat.id, "Выберите необходимую Вам неделю", reply_markup=week_markup)

    @bot.callback_query_handler(func=lambda call: True)
    def handle_query(call):
        back_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        back_keyboard.row("Назад")
        back_keyboard.row("Главное меню")
        days = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота"}
        monday = datetime.datetime.strptime(call.data, "%d-%m-%Y")
        for day_schedule in range(0, 6):
            dayz = datetime.datetime.strftime(monday + datetime.timedelta(days=day_schedule), "%d-%m-%Y")
            bot.send_message(call.message.chat.id, f"Расписание на {days.get(day_schedule)} {dayz}:")
            display_day = display_schedule(dayz)
            bot.send_message(call.message.chat.id, display_day)
        bot.send_message(call.message.chat.id, "Выберите пункт меню:", reply_markup=back_keyboard)


def update_base():
    for item in parsing.list_all(semestr):
        if parsing.list_weeks(item, semestr):
            if not sql.check_table(item):
                if re.match(r"\d\d[А-Я]", item) or re.match(r"[А-Я]{2}-\d\d", item):
                    sql.insert_lessons_group(parsing.make_schedule_for_teacher(item, semestr),
                                             parsing.pars_changes(semestr))
                else:
                    sql.insert_lessons_teacher(parsing.make_schedule_for_teacher(item, semestr),
                                               parsing.pars_changes(semestr))
            else:
                sql.delete_table(item)
                if re.match(r"\d\d[А-Я]", item) or re.match(r"[А-Я]{2}-\d\d", item):
                    sql.insert_lessons_group(parsing.make_schedule_for_teacher(item, semestr),
                                             parsing.pars_changes(semestr))
                else:
                    sql.insert_lessons_teacher(parsing.make_schedule_for_teacher(item, semestr),
                                               parsing.pars_changes(semestr))


scheduler = BackgroundScheduler()
scheduler.add_job(update_base, trigger="cron", hour=4, minute=0)
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass

if __name__ == '__main__':
    bot.infinity_polling()
