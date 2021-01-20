import telebot
import os
import re
import requests
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
sql.create_user_position(database_url)


# start message
@bot.message_handler(commands=["start"])
def handle_text(message):
    user_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    user_keyboard.row("Ввести полное название группы / преподавателя / аудитории",
                      "Найти полное название группы / преподавателя / аудитории")
    start_message = "Вас приветствует бот показа расписания занятий в Полесском государственном " \
                    "университете. Для вывода расписания вы должны сделать выбор:"
    bot.send_message(message.from_user.id, start_message, reply_markup=user_keyboard)
    sql.set_getting_position(str(message.chat.id), database_url)


@bot.message_handler(func=lambda message: "Главное меню" == message.text, content_types=['text'])
def handle_text(message):
    keyboard.main_menu(message)


@bot.message_handler(func=lambda message: "Ввести полное название группы / преподавателя / аудитории" == message.text,
                     content_types=["text"])
def handle_text(message):
    find_message = "Введите, пожалуйста, полное название группы (например, 18ММТ-1), преподавателя " \
                   "(например, Бучик Татьяна Александровна) или аудитории (например, 220):"
    msgname = bot.send_message(message.chat.id, find_message)
    bot.register_next_step_handler(msgname, save_name_group)


def save_name_group(message):
    name_group = message.text
    if name_group not in parsing.list_all(second_semestr):
        bot.send_message(message.chat.id, "Такой группы / преподавателя / аудитории нет в университете."
                                          " Попробуйте воспользоваться поиском.")
        keyboard.main_menu(message)
    else:
        sql.set_search_position(str(message.chat.id), name_group, database_url)


print(sorted(parsing.list_groups(second_semestr)))

# print(parsing.make_schedule_for_teacher("19МПП-1", second_semestr))
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
