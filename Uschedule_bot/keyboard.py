# -*- coding: utf-8 -*-

import telebot


class Keyboard:
    def __init__(self, bot):
        self.bot = bot

    # create the main menu
    def main_menu(self, message):
        user_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        user_keyboard.row("🏫 Ввести полное название группы / преподавателя / аудитории:")
        user_keyboard.row("🔎 Поиск названия группы / преподавателя / аудитории:")
        start_message = "Вас приветствует бот показа расписания занятий в Полесском государственном " \
                        "университете. Для вывода расписания вы должны сделать выбор:"
        self.bot.send_message(message.from_user.id, start_message, reply_markup=user_keyboard)

    # create the menu for showing the schedule of lessons
    def schedule_menu(self, message):
        schedule_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        schedule_keyboard.row("📌 Расписание на сегодняшний день", "📌 Расписание на завтрашний день")
        schedule_keyboard.row("📆 Расписание на неделю")
        schedule_keyboard.row("⏰ Подписаться на ежедневные оповещения о занятиях в 7-00")
        schedule_keyboard.row("🔕 Отписаться от ежедневных оповещений о занятиях в 7-00")
        schedule_keyboard.row("✅ Главное меню")
        warningmsg = "Выберите период:"
        self.bot.send_message(message.from_user.id, warningmsg, reply_markup=schedule_keyboard)

    # create the menu with main menu and back buttons
    def main_back_menu(self, message):
        main_back_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        main_back_keyboard.row("🔀 Назад")
        main_back_keyboard.row("✅ Главное меню")
        self.bot.send_message(message.from_user.id, "Выберите пункт меню:", reply_markup=main_back_keyboard)
