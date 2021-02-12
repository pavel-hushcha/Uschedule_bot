# -*- coding: utf-8 -*-

import sql
import datetime
import parsing
import re
import os

# # get tokens from token file if it exist or from environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path, encoding='utf-8-sig') as env:
        for i in env:
            k, v = i.rstrip().split("=")
            os.environ[k] = v

database_url = os.environ.get("DATABASE_URL")
sql = sql.Sql(database_url)


# check database tables and returns the dictionary of teacher's lessons
def check_return_lessons(name, semestr):
    date_changes = parsing.pars_changes(semestr)
    parsing_schedule = parsing.make_schedule_for_teacher(name, semestr)
    if not sql.check_table(name):  # check if lessons of teacher do not exist in database
        if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
            sql.insert_lessons_group(parsing_schedule, date_changes)  # create the table with lessons
        else:
            sql.insert_lessons_teacher(parsing_schedule, date_changes)
    # check the date of changes in table
    date_table = datetime.datetime.strptime(sql.read_date(name), "%Y-%m-%d %H:%M:%S")
    if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
        if date_table == date_changes:
            lessons = sql.read_lessons_group(name)
        else:
            sql.delete_table(name)  # upgrade the table if date is over
            sql.insert_lessons_group(parsing_schedule, date_changes)
            lessons = sql.read_lessons_group(name)
    else:
        if date_table == date_changes:
            lessons = sql.read_lessons_teacher(name)
        else:
            sql.delete_table(name)
            sql.insert_lessons_teacher(parsing_schedule, date_changes)
            lessons = sql.read_lessons_teacher(name)
    return lessons


# print to telegram chat the schedule of lessons on the day
def display_schedule(name, date, lessons):
    displ_schedule = ""
    if date in lessons:     # check if lessons in this day exist
        for part in lessons.get(date):
            if re.match(r"\d\d[А-Я]", name) or re.match(r"[А-Я]{2}-\d\d", name):
                displ_schedule += f"📍*{part[0]}* | {part[1]} | *{part[2]}* | {part[3]} | {part[4]}"
                displ_schedule += "\n"
            else:
                displ_schedule += f"📍*{part[0]}* | {part[1]} | *{part[2]}* | {part[3]}"
                displ_schedule += "\n"
    return displ_schedule
