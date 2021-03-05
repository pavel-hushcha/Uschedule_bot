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
        user_keyboard.row("📨 Обратная связь")
        start_message = "Вас приветствует бот показа расписания занятий в Полесском государственном " \
                        "университете. Для вывода расписания вы должны сделать выбор:"
        self.bot.send_message(message.from_user.id, start_message, reply_markup=user_keyboard)

    # create the menu for showing the schedule of lessons
    def schedule_menu(self, message):
        schedule_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        schedule_keyboard.row("📌 Расписание на сегодняшний день", "📌 Расписание на завтрашний день")
        schedule_keyboard.row("👈 Расписание на текущую неделю", "📆 Расписание на неделю",
                              "👉 Расписание на следующую неделю")
        schedule_keyboard.row("⏰ Оформить (отменить) подписку на ежедневные оповещения о занятиях")
        schedule_keyboard.row("✅ Главное меню")
        warningmsg = "Выберите период:"
        self.bot.send_message(message.from_user.id, warningmsg, reply_markup=schedule_keyboard)

    # create the menu with main menu and back buttons
    def main_back_menu(self, message):
        main_back_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        main_back_keyboard.row("🔀 Назад")
        main_back_keyboard.row("✅ Главное меню")
        self.bot.send_message(message.from_user.id, "Выберите пункт меню:", reply_markup=main_back_keyboard)

    def subscribers_menu(self, message):
        subscribers_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        subscribers_keyboard.row("⏰ Подписаться на ежедневные оповещения о занятиях")
        subscribers_keyboard.row("🔕 Отписаться от ежедневных оповещений о занятиях")
        self.bot.send_message(message.from_user.id, "Выберите пункт меню:", reply_markup=subscribers_keyboard)