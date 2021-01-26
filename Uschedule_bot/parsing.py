# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from datetime import timedelta


#  make dictionary of schedule of teacher or group of students
def make_schedule_for_teacher(teacher, semestr):
    # parsing html page with schedule;
    def pars_schedule(teach_group, sem):
        params = {"f": None, "q": teach_group}
        return BeautifulSoup(requests.get(sem, params).text, "lxml")

    # transform numbers of weeks in names of lessons to lists
    # '3-5, 8-14, 16-17' --> [3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 16, 17]
    def weeks_specify(weeks_from_lesson):
        numbers_of_weeks = []
        for numbers in weeks_from_lesson:
            if len(numbers) > 2:
                numbers = numbers.split(", ")
                for _i in numbers:
                    if len(_i) > 2:
                        _i = _i.split("-")
                        for _item in range(int(_i[0]), int(_i[1]) + 1):
                            numbers_of_weeks.append(_item + 1)
                    else:
                        numbers_of_weeks.append(int(_i) + 1)
            else:
                numbers_of_weeks.append(int(numbers) + 1)
        return numbers_of_weeks

    # transforming dictionary with lessons by days of week to dictionary with
    # lessons by date
    def transform_to_days(massive):
        d_of_week = {"Понедельник": 0, "Вторник": 1, "Среда": 2, "Четверг": 3, "Пятница": 4, "Суббота": 5}
        for lesson in massive.get(day):
            # cut numbers of weeks in names of lessons and transform its
            list_of_numbers_of_weeks = weeks_specify(re.findall(r"\(([^а-яА-Я]*)\)", lesson[1]))
            for part in list_of_numbers_of_weeks:
                #  clear the names of lessons from numbers of weeks
                lesson[1] = re.sub(r"\(([^а-яА-Я]*)\)\s", "", lesson[1])
                #  set the date of day
                date = datetime.strptime(weeks.get(part)[:6], "%d.%m.") + timedelta(days=d_of_week.get(day))
                cur_date = datetime.strftime(date, "%d-%m-") + str(year)
                days.setdefault(cur_date, [])
                days[cur_date].append(lesson)  # add lessons to dictionary by dates

    # finding block with the schedule in html page
    year = pars_changes(semestr).year
    schedule = []
    for parts in pars_schedule(teacher, semestr).find("tbody", id="weeks-filter").find_all("tr"):
        for line in parts:
            if line.text not in ["(Неделя) Предмет", "Аудитория", "Группа", "Преподаватель"]:
                schedule.append(line.text)

    # make dictionary with schedule (keys = days of week)
    schedule_days = {}  # dictionary view: {'Понедельник': [['10:20-11:55', '(3-5, 8-14, 16-17) \
    # Основы менеджмента и организационное поведение - лек.', '407', '20ПД-1 ']]}
    day = None  # 'Понедельник'
    count, count_d = 0, 0
    for item in schedule:
        if item in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]:
            day = item  # make key in dictionary
            schedule_days[item] = []  # add blank list
            count = 0  # count lesson in one day
            count_d = 0  # count days
        elif count == 0:  # add time to lesson
            schedule_days[day].append([item])
            count += 1
        elif count == 3 and not (re.match(r"\d\d[А-Я]", teacher) or re.match(r"[А-Я]{2}-\d\d", teacher)):
            # add classroom to lesson
            schedule_days[day][count_d].append(item)
            count = 0
            count_d += 1
        elif count == 4 and (re.match(r"\d\d[А-Я]", teacher) or re.match(r"[А-Я]{2}-\d\d", teacher)):
            # add subgroup of student to lesson
            schedule_days[day][count_d].append(item)
            count = 0
            count_d += 1
        else:
            schedule_days[day][count_d].append(item)  # add name lesson and group or teacher
            count += 1

    # make the dictionary with duration of weeks (keys = numbers of weeks)
    weeks = {}  # dictionary view: {2: '08.02.-13.02.'}
    # parsing duration of weeks
    ul_li = pars_schedule(teacher, semestr).find("ul", id="weeks-menu").find_all("li")
    for piece in ul_li:
        week_number = re.findall(r"(\d+)\s", piece.text)  # cut week number
        week_duration = re.findall(r"\((.*)\)", piece.text)  # cut week duration
        if week_number:
            weeks[int(week_number[0])] = week_duration[0]

    # add to dictionary the lessons by date
    days = {}
    for day in schedule_days:
        transform_to_days(schedule_days)
    schedule_of_teacher = {teacher: days}
    return schedule_of_teacher


# create the dictionary with numbers of weeks and its duration
def list_weeks(teacher, semestr):
    params = {"f": None, "q": teacher}
    weeks = []  # dictionary view: {2: '08.02.-13.02.'}
    check = BeautifulSoup(requests.get(semestr, params).text, "lxml").find("ul", id="weeks-menu")
    if check:
        ul_li = check.find_all("li")
        for piece in ul_li:
            week_number = re.findall(r"(\d+)\s", piece.text)  # cut week number
            week_duration = re.findall(r"\((.*)\)", piece.text)  # cut week duration
            if week_number:
                weeks.append(week_duration[0])
    else:
        weeks = False
    return weeks


# parsing list of teachers and groups of students
def list_all(semestr):
    main_page = requests.get(semestr).text
    teachers = str(re.findall(r"var query = \[(.*)]", main_page))[2:-2]
    cut_teachers = []
    for one in re.sub("'", "", teachers).split(","):
        cut_teachers.append(one.rstrip())
    return cut_teachers


# returns list of student's groups
def list_groups(semestr):
    list_al = list_all(semestr)
    list_gr = []
    for group in list_al:
        if re.match(r"\d\d[А-Я]", group) or re.match(r"[А-Я]{2}-\d\d", group):
            list_gr.append(group)
    return list_gr


# returns list of teachers and classrooms
def list_teachers(semestr):
    list_al = list_all(semestr)
    list_gr = []
    for group in list_al:
        if not re.match(r"\d\d[А-Я]", group) or re.match(r"[А-Я]{2}-\d\d", group):
            list_gr.append(group)
    return list_gr


# parsing the date of last changes of schedule
def pars_changes(semestr):
    for piece in BeautifulSoup(requests.get(semestr).text, "lxml"). \
            find("footer").find_all("p"):
        d_date = str(re.findall(r"Последние изменения вносились:\s(.*)", piece.text))[2:-4]
        if d_date:
            return datetime.strptime(d_date, "%d.%m.%Y %H:%M")
