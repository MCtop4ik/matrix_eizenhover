from database import Database
from imports import *
from list_ui import ListUI


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
