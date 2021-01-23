# -*- coding: utf-8 -*-

import psycopg2


class Sql:
    def __init__(self, url):
        self.url = url

    # insert in database the table named by teacher or classroom with lessons
    def insert_lessons_teacher(self, dict_teacher, date_ch):
        columns_teacher = ",".join(
            ["DATE_CH", "DATE", "TIME_LESSON", "LESSON", "CLASSROOM", "GROUPS"])  # column's names
        name = list(dict_teacher.keys())[0]  # name of table
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS \"{name}\" ("
                    f"DATE_CH TEXT NULL, "  # create the table
                    f"DATE TEXT NULL, "
                    f"TIME_LESSON TEXT NULL, "
                    f"LESSON TEXT NULL, "
                    f"CLASSROOM TEXT NULL, "
                    f"GROUPS TEXT NULL);")
        for day in dict_teacher.get(name):
            for lesson in dict_teacher.get(name)[day]:
                val_lesson = lesson[:]
                val_lesson.insert(0, str(date_ch))
                val_lesson.insert(1, day)
                cur.execute(f"INSERT INTO \"{name}\" ({columns_teacher}) VALUES {tuple(val_lesson)};")
        con.commit()
        cur.close()
        con.close()

    # insert in database the table named by student's group with lessons
    def insert_lessons_group(self, dict_group, date_ch):
        columns_group = ",".join(["DATE_CH", "DATE", "TIME_LESSON", "LESSON", "CLASSROOM", "GROUPS", "SUBGROUPS"])
        name = list(dict_group.keys())[0]  # name of table
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS \"{name}\" ("
                    f"DATE_CH TEXT NULL, "  # create the table
                    f"DATE TEXT NULL, "
                    f"TIME_LESSON TEXT NULL, "
                    f"LESSON TEXT NULL, "
                    f"CLASSROOM TEXT NULL, "
                    f"GROUPS TEXT NULL,"
                    f"SUBGROUPS TEXT NULL);")
        for day in dict_group.get(name):
            for lesson in dict_group.get(name)[day]:
                val_lesson = lesson[:]
                val_lesson.insert(0, str(date_ch))
                val_lesson.insert(1, day)
                cur.execute(f"INSERT INTO \"{name}\" ({columns_group}) VALUES {tuple(val_lesson)};")
        con.commit()
        cur.close()
        con.close()

    # read the teacher's lessons from sql:
    # {'15-02-2021': [['8:30-10:05', 'Маркетинг  - лек.', '406', 'Рыбалко Юлия Александровна', '']]}
    def read_lessons_teacher(self, name_teacher):
        columns_reader = ", ".join(["DATE", "TIME_LESSON", "LESSON", "CLASSROOM", "GROUPS"])
        sql_answer = {}
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"SELECT {columns_reader} from \"{name_teacher}\";")
        rows = cur.fetchall()
        for row in rows:
            sql_answer.setdefault(row[0], []).append(list(row[1:]))
        cur.close()
        con.close()
        return sql_answer

    # read the group's lessons from sql:
    # {'15-02-2021': [['8:30-10:05', 'Маркетинг  - лек.', '406', 'Рыбалко Юлия Александровна', '']]}
    def read_lessons_group(self, name_group):
        columns_reader = ", ".join(["DATE", "TIME_LESSON", "LESSON", "CLASSROOM", "GROUPS", "SUBGROUPS"])
        sql_answer = {}
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"SELECT {columns_reader} from \"{name_group}\";")
        rows = cur.fetchall()
        for row in rows:
            sql_answer.setdefault(row[0], []).append(list(row[1:]))
        cur.close()
        con.close()
        return sql_answer

    # deleting table from database
    def delete_table(self, name_table):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"DROP TABLE IF EXISTS \"{name_table}\";")
        con.commit()
        cur.close()
        con.close()

    # reading the date of changes in table of lessons
    def read_date(self, name_table):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"SELECT DATE_CH from \"{name_table}\";")
        row = cur.fetchone()
        cur.close()
        con.close()
        return str(*row)

    # check table if exists
    def check_table(self, name_table):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"SELECT EXISTS (SELECT * FROM information_schema.tables WHERE table_name = \'{name_table}\');")
        exist = bool(cur.fetchone()[0])
        cur.close()
        con.close()
        return exist

    # create the empty table named by user_position
    def create_user_position(self):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS USER_POSITION ("
                    "ID SERIAL PRIMARY KEY, "
                    "USER_ID TEXT NULL, "
                    "NAME_GROUP TEXT NULL, "
                    "SEARCH_POS TEXT NULL);")
        con.commit()
        cur.close()
        con.close()

    # insert into user_position table telegram user_id
    def set_getting_position(self, user_id):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"INSERT INTO USER_POSITION (USER_ID, NAME_GROUP, SEARCH_POS) VALUES "
                    f"({user_id}, 'none', 'none');")
        con.commit()
        cur.close()
        con.close()

    # insert into user_position table the name of group that wants to find the user
    def set_search_position(self, user_id, name_group):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"UPDATE USER_POSITION SET NAME_GROUP = ('{name_group}') WHERE ID IN "
                    f"(SELECT max(ID) FROM USER_POSITION WHERE USER_ID = ('{user_id}'));")
        con.commit()
        cur.close()
        con.close()

    # for the future functionality
    def set_weeks_position(self, user_id):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"UPDATE USER_POSITION SET SEARCH_POS = ('1') WHERE ID IN "
                    f"(SELECT max(ID) FROM USER_POSITION WHERE USER_ID = ('{user_id}'));")
        con.commit()
        cur.close()
        con.close()

    # get the telegram user_id
    def verification(self, user_id):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"SELECT NAME_GROUP FROM USER_POSITION WHERE ID IN "
                    f"(SELECT max(ID) FROM USER_POSITION WHERE USER_ID = ('{user_id}'));")
        search = cur.fetchone()
        return str(*search)

    # delete row with telegram user_id from user_position table
    def clear_getting_position(self, user_id):
        con = psycopg2.connect(self.url)
        cur = con.cursor()
        cur.execute(f"DELETE FROM USER_POSITION WHERE USER_ID = ('{user_id}');")
        con.commit()
        cur.close()
        con.close()
