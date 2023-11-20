from database import Database
from imports import *
from list_ui import ListUI


class ThreeMostImportantThings(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        for i in range(3):
            label = QLabel(f'№{i}')
            task = QComboBox()
            task.addItems([''] + list(map(lambda x: str(x[1]), self.promptly_important_data())))
            task.setCurrentIndex(self.get_three_most_important_things_value(i + 1))
            task.activated.connect(partial(self.save_in_db, i + 1))
            task.show()
            layout.addWidget(label, i, 0)
            layout.addWidget(task, i, 1)
        self.setLayout(layout)

    def save_in_db(self, three_things_id, task_data):
        try:
            if task_data == 0:
                task_id = 'Null'
            else:
                task_id = self.promptly_important_data()[task_data - 1][0]
            self.database_service.edit_three_things(task_id=task_id, three_important_id=three_things_id)
            print('here')
        except IndexError:
            print('rere')

    def get_three_most_important_things_value(self, three_things_id):
        try:
            for i in range(len(self.promptly_important_data())):
                if self.promptly_important_data()[i][0] == \
                        self.database_service.select_three_most_important()[three_things_id - 1][1]:
                    return i + 1
            return 0
        except IndexError:
            return 0
        except OperationalError:
            return 0

    def promptly_important_data(self):
        return self.database_service.select_by_category('promptly_important')
