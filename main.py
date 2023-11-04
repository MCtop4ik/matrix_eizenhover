import sqlite3
import sys

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QToolBar, QStatusBar, QCheckBox, QMenu, QLineEdit, QVBoxLayout, \
    QDialog, QDialogButtonBox, QPushButton, QComboBox
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
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ['id', 'name', 'description', 'category'][section]


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
        task_id = self.database_service.all()[self.field.row()][0]
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

    def get_categories(self):
        return list(map(lambda elem: elem[0], self.cursor.execute('SELECT title FROM Categories')))


class EisenhowerMatrix(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Матрица Эйзенхауера')
        self.setGeometry(10, 10, 500, 500)
        self.database_service.start_db()

        self.setCentralWidget(self.widget)
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action = QAction("&срочное / важное", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.urgently_important)
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action2 = QAction("&срочное / неважное", self)
        button_action2.setStatusTip("This is your button")
        button_action2.triggered.connect(self.urgently_unimportant)
        toolbar.addAction(button_action2)

        toolbar.addSeparator()

        button_action3 = QAction("&несрочное / важное", self)
        button_action3.setStatusTip("This is your button")
        button_action3.triggered.connect(self.promptly_important)
        toolbar.addAction(button_action3)

        toolbar.addSeparator()

        button_action4 = QAction("&несрочное / неважное", self)
        button_action4.setStatusTip("This is your button")
        button_action4.triggered.connect(self.promptly_unimportant)
        toolbar.addAction(button_action4)

        toolbar.addSeparator()

        button_action5 = QAction("&добавить текущие дела", self)
        button_action5.setStatusTip("This is your button")
        button_action5.triggered.connect(self.add_task)
        toolbar.addAction(button_action5)

        toolbar.addSeparator()

        button_action6 = QAction("&сделанные дела", self)
        button_action6.setStatusTip("This is your button")
        button_action6.triggered.connect(self.past_tasks)
        toolbar.addAction(button_action6)

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

    def urgently_important(self):
        """todo here will be timestamp"""
        self.category_widget('urgently_important')

    def urgently_unimportant(self):
        """todo whom I can delegate task"""
        self.category_widget('urgently_unimportant')

    def promptly_important(self):
        """todo 3 most important things I do today"""
        self.category_widget('promptly_important')

    def promptly_unimportant(self):
        """todo can I send them to infinity list or they will lose their relevance in near future"""
        self.category_widget('promptly_unimportant')

    def infinity_list(self):
        """todo here will be infinity list"""
        self.category_widget('infinity_list')

    def category_widget(self, category):
        self.clear_widget()
        layout = QVBoxLayout()
        if category == "promptly_unimportant":
            infl_button = QPushButton('Infinity List')
            infl_button.clicked.connect(self.infinity_list)
            layout.addWidget(infl_button)

        data = self.database_service.select_by_category(category)
        if data:
            table = QtWidgets.QTableView()
            model = TableModel(data)
            table.setModel(model)
            layout.addWidget(table)
        else:
            label = QLabel('No Data')
            layout.addWidget(label)
        self.widget.setLayout(layout)

    def clear_widget(self):
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EisenhowerMatrix()
    ex.show()
    sys.exit(app.exec())
