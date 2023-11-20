from database import Database
from imports import *
from list_ui import ListUI


class Timetable(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        self.layout()
        layout = QGridLayout()
        time_from = time(hour=9)
        for i in range(12):
            label = QLabel(time_from.replace(time_from.hour + i).strftime('%H:%M'))
            task = QComboBox()
            task.addItems([''] + list(map(lambda x: str(x[1]), self.urgently_important_data())))
            task.setCurrentIndex(self.get_timetable_value(i + 1))
            task.activated.connect(partial(self.save_in_db, i + 1))
            task.show()
            layout.addWidget(label, i, 0)
            layout.addWidget(task, i, 1)
        self.setLayout(layout)

    def save_in_db(self, timetable_id, task_data):
        print(timetable_id, task_data)
        try:
            if task_data == 0:
                task_id = 'Null'
            else:
                task_id = self.urgently_important_data()[task_data - 1][0]
            print(task_id, timetable_id)
            self.database_service.edit_timetable(timetable_id=timetable_id, task_id=task_id)
            print('here')
        except IndexError:
            print('rere')

    def urgently_important_data(self):
        return self.database_service.select_by_category('urgently_important')

    def get_timetable_value(self, timetable_id):
        try:
            for i in range(len(self.urgently_important_data())):
                if self.urgently_important_data()[i][0] == self.database_service.select_timetable() \
                        [timetable_id - 1][1]:
                    return i + 1
            return 0
        except IndexError:
            return 0
        except OperationalError:
            return 0
