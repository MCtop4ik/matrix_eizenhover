from imports import *


class Database:

    def __init__(self):
        self.db = sqlite3.connect('db/data.db')
        self.cursor = self.db.cursor()

    def start_db(self):
        if not self.cursor.execute('SELECT name from sqlite_master where type="table"').fetchall():
            self.create_databases()
            self.create_views()
            self.fill_in_categories()
            self.fill_in_timetable()
            self.fill_in_three_most_important_things()

    def create_databases(self):
        """todo create timestamps table :done"""
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Categories(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title string(100) NOT NULL
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS AllTasks(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name string(100) NOT NULL,
                                description text NOT NULL,
                                category_id int NOT NULL,
                                resolved boolean NOT NULL,
                                hide boolean NOT NULL,
                                timestamp_id int NOT NULL,
                                FOREIGN KEY (category_id) REFERENCES Categories(id),
                                FOREIGN KEY (timestamp_id) REFERENCES Timestamps(id)
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Timestamps(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                created_on int,
                                updated_on int,
                                resolved_on int
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS InfinityList(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                task_id INTEGER
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Timetable(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                task_id INTEGER
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Delegations(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                task_id INTEGER,
                                performer STRING
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ThreeMostImportant(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                task_id INTEGER
                            )""")
        self.db.commit()

    def create_views(self):
        """todo create views for all categories :done"""
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS urgently_important AS 
                                SELECT * FROM AllTasks WHERE category_id=1""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS urgently_unimportant AS
                                SELECT * FROM AllTasks WHERE category_id=2""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS promptly_important AS
                                SELECT * FROM AllTasks WHERE category_id=3""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS promptly_unimportant AS 
                                SELECT * FROM AllTasks WHERE category_id=4""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS infinity_list AS 
                                SELECT a_t.*, il.task_id
                                FROM AllTasks a_t, InfinityList il 
                                WHERE a_t.category_id=4 AND a_t.id=il.task_id""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS timetable_view AS 
                                SELECT a_t.*, tt.task_id
                                FROM AllTasks a_t, Timetable tt 
                                WHERE a_t.category_id=1 AND a_t.id=tt.task_id""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS delegations_view AS 
                                SELECT a_t.*, dl.*
                                FROM AllTasks a_t, Delegations dl
                                WHERE a_t.category_id=2 AND a_t.id=dl.task_id""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS not_in_infinity_list AS 
                                SELECT a_t.*
                                FROM AllTasks a_t
                                WHERE a_t.category_id=4 AND 
                                NOT EXISTS (
                                SELECT 1 FROM InfinityList il 
                                WHERE a_t.id = il.task_id
                                )""")
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS resolved_tasks AS 
                                SELECT * FROM AllTasks WHERE resolved=1""")
        self.db.commit()

    def all(self):
        return self.cursor.execute("SELECT * FROM AllTasks WHERE hide = 0").fetchall()

    def select_by_category(self, category):
        return self.cursor.execute(f"SELECT * FROM {category} WHERE hide = 0").fetchall()

    def select_timetable(self):
        return self.cursor.execute(f"SELECT * FROM Timetable").fetchall()

    def select_three_most_important(self):
        return self.cursor.execute(f"SELECT * FROM ThreeMostImportant").fetchall()

    def add_cell(self, name, description, category_id):
        """todo create exception for nil values :done
        todo timestamps """
        if not name or not description or not category_id:
            raise ValueError('you not allowed to add on this field null values')
        print(name, description, category_id)
        self.cursor.execute('INSERT INTO AllTasks('
                            'name,'
                            'description,'
                            'category_id,'
                            'resolved,'
                            'hide,'
                            'timestamp_id)'
                            f' VALUES ("{name}", "{description}", {category_id}, 0, 0, 1)')
        self.db.commit()

    def edit_cell(self, task_id, column_name, new_value):
        """todo create exception for nil values"""
        self.cursor.execute(f'UPDATE AllTasks SET {column_name}="{new_value}" WHERE id={task_id}')
        self.db.commit()

    def edit_timetable(self, timetable_id, task_id):
        """todo create exception for nil values"""
        self.cursor.execute(f'UPDATE Timetable SET task_id={task_id} WHERE id={timetable_id}')
        self.db.commit()

    def get_category_name_by_id(self, category_id):
        return self.cursor.execute('SELECT title FROM Categories WHERE id=?', (category_id,)).fetchone()

    def get_category_id_by_name(self, category_name):
        return self.cursor.execute('SELECT id FROM Categories WHERE title=?', (category_name,)).fetchone()

    def fill_in_categories(self):
        self.cursor.execute('INSERT INTO Categories(title) VALUES ("urgently_important")')
        self.cursor.execute('INSERT INTO Categories(title) VALUES ("urgently_unimportant")')
        self.cursor.execute('INSERT INTO Categories(title) VALUES ("promptly_important")')
        self.cursor.execute('INSERT INTO Categories(title) VALUES ("promptly_unimportant")')
        self.cursor.execute('INSERT INTO Categories(title) VALUES ("not mentioned")')
        self.db.commit()

    def fill_in_timetable(self):
        for i in range(12):
            self.cursor.execute('INSERT INTO Timetable(task_id) VALUES (NULL)')
        self.db.commit()

    def fill_in_three_most_important_things(self):
        for i in range(3):
            self.cursor.execute('INSERT INTO ThreeMostImportant(task_id) VALUES (NULL)')
        self.db.commit()

    def get_categories(self):
        return list(map(lambda elem: elem[0], self.cursor.execute('SELECT title FROM Categories')))

    def add_in_infinity_list(self, task_id):
        self.cursor.execute(f'INSERT INTO InfinityList(task_id) VALUES ({task_id})')
        self.db.commit()

    def select_delegations(self):
        return self.cursor.execute(f"SELECT * FROM delegations_view").fetchall()

    def insert_in_delegations(self, task_id):
        self.cursor.execute(f'INSERT INTO Delegations(task_id, performer) VALUES ({task_id}, NULL)')
        self.db.commit()

    def edit_three_things(self, task_id, three_important_id):
        self.cursor.execute(f'UPDATE ThreeMostImportant SET task_id={task_id} WHERE id={three_important_id}')
        self.db.commit()

    def edit_delegation_performer(self, delegation_id, performer):
        print(performer, delegation_id)
        self.cursor.execute(f'UPDATE Delegations SET performer="{performer}" WHERE id={delegation_id}')
        self.db.commit()
