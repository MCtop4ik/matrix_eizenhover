import sqlite3
import sys
import threading
from datetime import timedelta, datetime, time
from functools import partial
from sqlite3 import OperationalError

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QToolBar, QStatusBar, QCheckBox, QMenu, QLineEdit, QVBoxLayout, \
    QDialog, QDialogButtonBox, QPushButton, QComboBox, QGridLayout, QTableWidgetItem
from PyQt6.QtWidgets import QMainWindow


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = list(map(lambda arr: arr[:4], data))
        self.database_service = Database()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 3:
                return self.database_service.get_category_name_by_id(self._data[index.row()][index.column()])[0]
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ['id', 'name', 'description', 'category'][section]


class CategoryTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(CategoryTableModel, self).__init__()
        self._data = list(map(lambda arr: arr[1:3], data))
        self.database_service = Database()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ['name', 'description'][section]


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        test = QLineEdit()
        test.show()
        self.layout.addWidget(message)
        self.layout.addWidget(test)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class ToResolvedDialog(QDialog):
    def __init__(self, parent=None, cell_data=None, category=None):
        super().__init__(parent)
        self.database_service = Database()

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.resolving_button)
        self.buttonBox.rejected.connect(self.reject)

        self.data_row = self.database_service.select_by_category(category)[cell_data.row()]

        self.layout = QVBoxLayout()
        message = QLabel(str(cell_data.data()))
        done_label = QLabel('Is resolved?')
        self.resolved_checkbox = QComboBox()
        self.resolved_checkbox.addItems(["YES", "NO"])
        print(self.data_row)
        self.resolved_checkbox.setCurrentIndex((self.data_row[4] + 1) & 1)
        self.layout.addWidget(message)
        self.layout.addWidget(done_label)
        self.layout.addWidget(self.resolved_checkbox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def resolving_button(self):
        self.database_service.edit_cell(
            task_id=self.data_row[0],
            column_name='resolved',
            new_value=1 if self.resolved_checkbox.currentText() == "YES" else 0
        )
        self.accept()


class CreateRowWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Task")
        self.database_service = Database()

        qBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(qBtn)
        self.buttonBox.accepted.connect(self.send_data_to_database)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message1 = QLabel("Name")
        self.cell_name = QLineEdit()
        self.cell_name.show()
        message2 = QLabel("Description")
        self.cell_description = QLineEdit()
        self.cell_description.show()
        message3 = QLabel("Category")
        self.cell_category = QComboBox()
        self.cell_category.addItems(map(lambda x: self.database_service.get_category_name_by_id(x)[0], range(1, 6)))
        self.cell_category.show()
        self.layout.addWidget(message1)
        self.layout.addWidget(self.cell_name)
        self.layout.addWidget(message2)
        self.layout.addWidget(self.cell_description)
        self.layout.addWidget(message3)
        self.layout.addWidget(self.cell_category)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def send_data_to_database(self):
        """todo create query :done"""
        self.database_service.add_cell(
            self.cell_name.text(),
            self.cell_description.text(),
            self.database_service.get_category_id_by_name(self.cell_category.currentText())[0]
        )
        self.accept()


class EditCellWindow(QDialog):
    def __init__(self, parent=None, field=None):
        super().__init__(parent)

        self.setWindowTitle("Edit Cell")
        self.database_service = Database()
        self.field = field

        qBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(qBtn)
        self.buttonBox.accepted.connect(self.send_data_to_database)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        if self.field.column() == 3:
            message = QLabel(f"Change category")
            self.cell_category = QComboBox()
            self.cell_category.addItems(self.database_service.get_categories())
            self.cell_category.setCurrentIndex(self.database_service.get_categories().index(self.field.data()))
            self.cell_category.show()
            self.layout.addWidget(message)
            self.layout.addWidget(self.cell_category)
        else:
            message = QLabel(f"Edit `{field.data()}`")
            self.new_value = QLineEdit()
            self.new_value.show()
            self.layout.addWidget(message)
            self.layout.addWidget(self.new_value)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def send_data_to_database(self):
        """todo update query :done"""
        table_fields = ['id', 'name', 'description', 'category_id', 'resolved', 'hide', 'timestamp']
        if self.field.column() == 3:
            self.new_value = self.database_service.get_category_id_by_name(self.cell_category.currentText())[0]
        else:
            self.new_value = self.new_value.text()
        task_id = list(filter(lambda x: x[5] == 0, self.database_service.all()))[self.field.row()][0]
        column_name = table_fields[self.field.column()]
        self.database_service.edit_cell(
            task_id=task_id,
            column_name=column_name,
            new_value=self.new_value
        )
        self.accept()


class Database:

    def __init__(self):
        self.db = sqlite3.connect('data.db')
        self.cursor = self.db.cursor()

    def start_db(self):
        if not self.cursor.execute('SELECT name from sqlite_master where type="table"').fetchall():
            self.create_databases()
            self.create_views()
            self.fill_in_categories()
            self.fill_in_timetable()

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
        self.cursor.execute("""CREATE VIEW IF NOT EXISTS timetable AS 
                                SELECT a_t.*, tt.task_id
                                FROM AllTasks a_t, Timetable tt 
                                WHERE a_t.category_id=1 AND a_t.id=tt.task_id""")
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
        self.cursor.execute(f'UPDATE Timetable SET task_id="{task_id}" WHERE id={timetable_id}')
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

    def get_categories(self):
        return list(map(lambda elem: elem[0], self.cursor.execute('SELECT title FROM Categories')))

    def add_in_infinity_list(self, task_id):
        self.cursor.execute(f'INSERT INTO InfinityList(task_id) VALUES ({task_id})')
        self.db.commit()


class EisenhowerMatrix(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Матрица Эйзенхауера')

        self.setFixedSize(700, 500)
        self.database_service.start_db()

        self.setCentralWidget(self.widget)
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action = QAction("&дела", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.category_widget)
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action2 = QAction("&добавить текущие дела", self)
        button_action2.setStatusTip("This is your button")
        button_action2.triggered.connect(self.add_task)
        toolbar.addAction(button_action2)

        toolbar.addSeparator()

        button_action3 = QAction("&сделанные дела", self)
        button_action3.setStatusTip("This is your button")
        button_action3.triggered.connect(self.past_tasks)
        toolbar.addAction(button_action3)

        self.add_task()

    def add_task(self):
        """todo here you need to add task"""
        self.clear_widget()

        add_button = QPushButton('Add Task')
        add_button.clicked.connect(self.add_row)
        layout = QVBoxLayout()
        layout.addWidget(add_button)
        data = self.database_service.all()
        if data:
            table = QtWidgets.QTableView()
            model = TableModel(data)
            table.setModel(model)
            table.clicked.connect(self.edit_row)
            layout.addWidget(table)
        else:
            label = QLabel('No Data')
            layout.addWidget(label)

        self.widget.setLayout(layout)

    def add_row(self):
        """todo create row in table"""
        dlg = CreateRowWindow(self)
        if dlg.exec():
            print("Success!")
        self.add_task()

    def edit_row(self, k):
        """todo update row in table"""
        dlg = EditCellWindow(self, k)
        if dlg.exec():
            print("Success!")
        self.add_task()

    def past_tasks(self):
        """todo here will be completed tasks"""
        self.clear_widget()
        data = self.database_service.select_by_category('resolved_tasks')

        layout = QVBoxLayout()
        if data:
            table = QtWidgets.QTableView()
            model = CategoryTableModel(data)
            table.setModel(model)
            layout.addWidget(table)
        else:
            label = QLabel('No data')
            layout.addWidget(label)
        self.widget.setLayout(layout)

    def category_widget(self):
        self.clear_widget()
        layout = QGridLayout()
        layout.addLayout(self.urgently_important(), 0, 0)
        layout.addLayout(self.urgently_unimportant(), 0, 1)
        layout.addLayout(self.promptly_important(), 1, 0)
        layout.addLayout(self.promptly_unimportant(), 1, 1)

        self.widget.setLayout(layout)

    def urgently_important(self):
        """todo here will be timestamp"""
        layout = QVBoxLayout()
        label = QLabel("urgently_important")
        label.show()
        layout.addWidget(label)

        layout = self.create_table_category(layout, "urgently_important")

        timetable_button = QPushButton('Timetable')
        timetable_button.clicked.connect(self.timetable)
        layout.addWidget(timetable_button)

        return layout

    def urgently_unimportant(self):
        """todo whom I can delegate task"""
        layout = QVBoxLayout()
        label = QLabel("urgently_unimportant")
        label.show()
        layout.addWidget(label)

        layout = self.create_table_category(layout, "urgently_unimportant")

        delegate_button = QPushButton('Delegate to someone')
        delegate_button.clicked.connect(self.delegation)
        layout.addWidget(delegate_button)

        return layout

    def promptly_important(self):
        """todo 3 most important things I do today"""
        layout = QVBoxLayout()
        label = QLabel('promptly_important')
        label.show()
        layout.addWidget(label)

        layout = self.create_table_category(layout, "promptly_important")

        three_things_button = QPushButton('Three most important things')
        three_things_button.clicked.connect(self.three_most_important_things)
        layout.addWidget(three_things_button)

        return layout

    def promptly_unimportant(self):
        """can I set it to infinity list?"""
        layout = QVBoxLayout()

        label = QLabel('promptly_unimportant')
        label.show()
        layout.addWidget(label)

        layout = self.create_table_category(layout, "promptly_unimportant")

        infl_button = QPushButton('Infinity List')
        infl_button.clicked.connect(self.infinity_list)
        layout.addWidget(infl_button)

        return layout

    def three_most_important_things(self):
        self.three_things_window = ThreeMostImportantThings()
        self.three_things_window.show()

    def delegation(self):
        self.delegation_window = Delegate()
        self.delegation_window.show()

    def timetable(self):
        self.timetable_window = Timetable()
        self.timetable_window.show()

    def infinity_list(self):
        """todo here will be infinity list"""
        self.infinity_list_window = InfinityList()
        self.infinity_list_window.show()

    def create_table_category(self, layout, category):
        data = self.database_service.select_by_category(category)
        if data:
            table = QtWidgets.QTableView()
            model = CategoryTableModel(data)
            table.setModel(model)
            table.clicked.connect(partial(self.add_to_list, category))
            layout.addWidget(table)
        else:
            label = QLabel('No Data')
            layout.addWidget(label)
        return layout

    def add_to_list(self, category=None, cell_data=None):
        add = ToResolvedDialog(self, cell_data, category)
        add.exec()

    def clear_widget(self):
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)


class ListAddingDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.database_service = Database()
        self.category = category

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.add_to_db)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        label = QLabel('Choose task to add:')
        layout.addWidget(label)

        self.data = self.database_service.select_by_category(category)
        self.add_combobox = QComboBox()
        self.add_combobox.addItems(['<-------------------->'] + list(map(lambda x: str(x[1]), self.data)))
        layout.addWidget(self.add_combobox)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def add_to_db(self):
        try:
            t = self.add_combobox.currentText()
            if t == '<-------------------->':
                self.reject()
            task = list(filter(lambda x: str(x[1]) == t, self.data))
            if not task:
                self.reject()
            task_id = task[0][0]
            if self.category == 'not_in_infinity_list':
                self.database_service.add_in_infinity_list(task_id)
            self.accept()
        except IndexError:
            self.reject()
        except ValueError:
            self.reject()


class ListUI:

    def add_to_list(self, category):
        dlg = ListAddingDialog(category=category)
        if dlg.exec():
            print('need an update')

    def generate_table(self, data):
        layout = QVBoxLayout()
        if data:
            table = QtWidgets.QTableView()
            model = CategoryTableModel(data)
            table.setModel(model)
            layout.addWidget(table)
        else:
            label = QLabel('None data')
            label.show()
            layout.addWidget(label)
        return layout

    def to_resolved(self, table_row, data, category):
        class DataStruct:
            def __init__(self, row, data_cell):
                self.row = row
                self.data = data_cell

            def row(self):
                return self.row

            def data(self):
                return self.data

        add = ToResolvedDialog(cell_data=DataStruct(table_row, data), category=category)
        add.exec()


class InfinityList(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addLayout(self.generate_table(self.infinity_list_data()))
        button = QPushButton('Add to infinity list')
        button.clicked.connect(partial(self.add_to_list, 'not_in_infinity_list'))
        button.show()
        layout.addWidget(button)
        self.setLayout(layout)

    def promptly_unimportant_data(self):
        return self.database_service.select_by_category('promptly_unimportant')

    def infinity_list_data(self):
        return self.database_service.select_by_category('infinity_list')


class Timetable(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        time_from = time(hour=9)
        for i in range(12):
            label = QLabel(time_from.replace(time_from.hour + i).strftime('%H:%M'))
            try:
                data = self.database_service.select_by_category('timetable')
            except OperationalError:
                data = []
            name = ''
            if data:
                name = data[i][1]
            task = QComboBox()
            task.addItems([''] + list(map(lambda x: str(x[1]), self.urgently_important_data())))
            task.setCurrentIndex(self.get_timetable_value(i + 1))
            task.activated.connect(partial(self.save_in_db, i + 1))
            is_resolved = QCheckBox()
            is_resolved.toggled.connect(partial(self.to_resolved, 1, name))
            layout.addWidget(label, i, 0)
            layout.addWidget(task, i, 1)
            layout.addWidget(is_resolved, i, 2)
        self.setLayout(layout)

    def save_in_db(self, timetable_id, cell_data):
        try:
            task_id = self.urgently_important_data()[cell_data - 1][0]
            self.database_service.edit_timetable(timetable_id=timetable_id, task_id=task_id)
            print('here')
        except IndexError:
            print('rere')

    def urgently_important_data(self):
        return self.database_service.select_by_category('urgently_important')

    def get_timetable_value(self, timetable_id):
        try:
            print(self.database_service.select_by_category('timetable')[timetable_id][0])
            return list(filter(
                lambda x: self.database_service.select_by_category('timetable')[timetable_id][0] == x[0],
                self.urgently_important_data()
            ))[0][0]
        except IndexError:
            return 0
        except OperationalError as e:
            return 0


class ThreeMostImportantThings(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel('hi')
        layout.addWidget(label)
        self.setLayout(layout)

    def promptly_important_data(self):
        return self.database_service.select_by_category('promptly_important')


class Delegate(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel('hi')
        layout.addWidget(label)
        self.setLayout(layout)

    def urgently_unimportant_data(self):
        return self.database_service.select_by_category('urgently_unimportant')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EisenhowerMatrix()
    ex.show()
    sys.exit(app.exec())
