from category_table_model import CategoryTableModel
from create_row_window import CreateRowWindow
from database import Database
from delegate import Delegate
from edit_cell_window import EditCellWindow
from imports import *
from infinity_list import InfinityList
from table_model import TableModel
from three_most_important_things import ThreeMostImportantThings
from timetable import Timetable
from to_resolved_dialog import ToResolvedDialog


class EisenhowerMatrix(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        self.database_service = Database()
        self.initUI()
        self.animation = None

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
            label = QLabel('None data')
            pixmap = QPixmap('no_data.png').scaled(200, 200)
            label.setPixmap(pixmap)
            self.animation = QPropertyAnimation(label, b"pos")
            self.animation.setEndValue(QPoint(200, 0))
            self.animation.setDuration(2000)
            label.show()
            layout.addWidget(label)
        self.widget.setLayout(layout)
        if not data and self.animation:
            self.animation.start()

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
            label = QLabel('None data')
            pixmap = QPixmap('no_data.png').scaled(200, 200)
            label.setPixmap(pixmap)
            self.animation = QPropertyAnimation(label, b"pos")
            self.animation.setEndValue(QPoint(200, 100))
            self.animation.setDuration(2000)
            label.show()
            layout.addWidget(label)
            layout.addWidget(label)
        self.widget.setLayout(layout)
        if not data and self.animation:
            self.animation.start()

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
        label = QLabel("Urgently Important Tasks")
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
        label = QLabel("Urgently Unimportant Tasks")
        label.show()
        layout.addWidget(label)

        layout = self.create_table_category(layout, "urgently_unimportant")

        delegate_button = QPushButton('Delegations')
        delegate_button.clicked.connect(self.delegation)
        layout.addWidget(delegate_button)

        return layout

    def promptly_important(self):
        """todo 3 most important things I do today"""
        layout = QVBoxLayout()
        label = QLabel('Promptly Important Tasks')
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

        label = QLabel('Promptly Unimportant Tasks')
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
            label = QLabel('None data')
            pixmap = QPixmap('no_data.png').scaled(200, 200)
            label.setPixmap(pixmap)
            label.show()
            layout.addWidget(label)
        return layout

    def add_to_list(self, category=None, cell_data=None):
        add = ToResolvedDialog(self, cell_data, category)
        add.exec()

    def clear_widget(self):
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
