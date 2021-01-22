import telebot
import os
import re
import datetime
import sql
import parsing
import keyboard


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
    sql.clear_getting_position(str(message.from_user.id))# _____________разобраться с таблицей (очищать значения)


@bot.message_handler(func=lambda message: "Назад" == message.text, content_types=['text'])
def handle_text(message):
    keyboard.schedule_menu(message)


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
    if name_group not in parsing.list_all(second_semestr):
        bot.send_message(message.chat.id, "Такой группы / преподавателя / аудитории нет в университете."
                                          " Попробуйте воспользоваться поиском.")
        keyboard.main_menu(message)
    else:
        if not parsing.list_weeks(name_group, second_semestr):
            bot.send_message(message.chat.id, "Занятия отсутствуют или нет связи с сайтом университета")
            keyboard.main_menu(message)
        else:
            sql.set_search_position(str(message.chat.id), name_group)
            keyboard.schedule_menu(message)


@bot.message_handler(func=lambda message: "Расписание на сегодняшний день" == message.text or
                                          "Расписание на завтрашний день" == message.text or
                                          "Расписание на текущую неделю" == message.text or
                                          "Расписание на следующую неделю" == message.text, content_types=["text"])
def handle_text(message):
    errormsg = "Занятия отсутствуют или нет связи с сайтом университета"
    name = sql.verification(str(message.chat.id))
    now = datetime.datetime.now().date().strftime("%d-%m-%Y")
    date_changes = parsing.pars_changes(second_semestr)
    if not sql.check_table(name):
        if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
            sql.insert_lessons_group(parsing.make_schedule_for_teacher(name, second_semestr), date_changes)
        else:
            sql.insert_lessons_teacher(parsing.make_schedule_for_teacher(name, second_semestr), date_changes)

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
                sql.insert_lessons_group(parsing.make_schedule_for_teacher(name, second_semestr), date_changes)
                lessons = sql.read_lessons_group(name)
        else:
            if date_table == date_changes:
                lessons = sql.read_lessons_teacher(name)
            else:
                sql.delete_table(name)
                sql.insert_lessons_teacher(parsing.make_schedule_for_teacher(name, second_semestr), date_changes)
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
            bot.send_message(message.chat.id, errormsg, reply_markup=main_back_keyboard)
        return display_schedule

    if message.text == "Расписание на сегодняшний день":
        today_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        today_keyboard.row("Назад")
        today_keyboard.row("Главное меню")
        bot.send_message(message.chat.id, f"Расписание на сегодня {now}:")
        display_today = display_schedule("08-02-2021")
        if len(display_today) > 0:
            bot.send_message(message.chat.id, display_today, reply_markup=today_keyboard)

    if message.text == "Расписание на завтрашний день":
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        tomorrow_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        tomorrow_keyboard.row("Назад")
        tomorrow_keyboard.row("Главное меню")
        bot.send_message(message.chat.id, f"Расписание на завтра {tomorrow}:")
        display_tomorrow = display_schedule("09-02-2021")
        if len(display_tomorrow) > 0:
            bot.send_message(message.chat.id, display_tomorrow, reply_markup=tomorrow_keyboard)

    # if message.text == "Расписание на текущую неделю":
    #



print(parsing.list_weeks("Кулаков Василий Николаевич", second_semestr))
# print(parsing.make_schedule_for_teacher("Кулаков Василий Николаевич", second_semestr))
# lessons = sql.read_lessons_teacher('Гуща Павел Васильевич')
# print(lessons.get("08-02-2021")[0][0])
# for i in lessons.get("08-02-2021")[0]:
#     print(i)
# date_table = datetime.datetime.strptime(sql.read_date("19МПП-1"), "%Y-%m-%d %H:%M:%S")
# date_changes = parsing.pars_changes(second_semestr)
# print(date_table, date_changes)
# print(date_table > date_changes)
# print(sorted(parsing.list_all(second_semestr)))
# print(parsing.pars_changes(second_semestr))
# print(datetime.datetime.now(pytz.timezone("Europe/Minsk")))
print(datetime.datetime.now().date().strftime("%d-%m-%Y"))
print(sql.check_table("18ММТ-1"))


# print(parsing.make_schedule_for_teacher("Кулаков Василий Николаевич", second_semestr))
# a = parsing.make_schedule_for_teacher("19МПП-1", second_semestr)
# d = str(parsing.pars_changes(second_semestr))
# print(d)
# sql.insert_lessons_group(a, d, database_url)
# sql.delete_table("Гуща Павел Васильевич", database_url)

# for i in list_teacher():
#     try:
#         if re.match(r"\d\d[А-Я]", i) or re.match(r"[А-Я]{2}-\d\d", i):
#             sql.insert_lessons_group(make_schedule_for_teacher(i, semestr))
#             print(i)
#         else:
#             sql.insert_lessons_teacher(make_schedule_for_teacher(i, semestr), date_of_changes)
#             print(i)
#     except Exception:
#         print(i, "- false")

# print(read_lessons_teacher("Астренков Андрей Валерьевич"))
# # delete_table("Апанович Анжелика Павловна")
# print(read_date("Астренков Андрей Валерьевич"))
# delete_table("Арашкевич Ирина Николаевна")


if __name__ == '__main__':
    bot.infinity_polling()
