import telebot


class Keyboard:
    def __init__(self, bot):
        self.bot = bot

    def main_menu(self, message):
        user_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        user_keyboard.row("Ввести полное название группы / преподавателя / аудитории:",
                          "Поиск полного названия группы / преподавателя / аудитории:")
        start_message = "Вас приветствует бот показа расписания занятий в Полесском государственном " \
                        "университете. Для вывода расписания вы должны сделать выбор:"
        self.bot.send_message(message.from_user.id, start_message, reply_markup=user_keyboard)

    def schedule_menu(self, message):
        schedule_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        schedule_keyboard.row("Расписание на сегодняшний день")
        schedule_keyboard.row("Расписание на завтрашний день")
        schedule_keyboard.row("Расписание на текущую неделю")
        schedule_keyboard.row("Расписание на следующую неделю")
        schedule_keyboard.row("Главное меню")
        self.bot.send_message(message.from_user.id, "Выберите период:", reply_markup=schedule_keyboard)

    def search_menu(self, message):
        find_message = "Введите, пожалуйста, полное название группы (например, 18ММТ-1), преподавателя " \
                       "(например, Бучик Татьяна Александровна) или аудитории (например, 220):"
        msgname = self.bot.send_message(message.from_user.id, find_message)
        self.bot.register_next_step_handler(msgname, self.save_name_group)


