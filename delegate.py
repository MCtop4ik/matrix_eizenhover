from database import Database
from imports import *
from list_ui import ListUI


class Delegate(QtWidgets.QWidget, ListUI):
    def __init__(self):
        super().__init__()
        self.database_service = Database()
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        for i in range(len(self.delegations())):
            delegation_task = self.delegations()[i]
            label = QLabel(str(delegation_task[1]))
            delegation_input = QLineEdit()
            delegation_input.setText(str(delegation_task[9]))
            print(delegation_task)
            delegation_input.textChanged.connect(partial(
                self.save_in_delegations,
                str(delegation_task[7])
            ))
            layout.addWidget(label, i, 0)
            layout.addWidget(delegation_input, i, 1)
        button = QPushButton('Create a delegation')
        button.clicked.connect(partial(self.add_to_list, 'urgently_unimportant'))
        button.show()
        layout.addWidget(button)
        self.setLayout(layout)

    def save_in_delegations(self, delegation_id, performer):
        print(delegation_id)
        self.database_service.edit_delegation_performer(
            delegation_id=delegation_id,
            performer=performer
        )

    def urgently_unimportant_data(self):
        return self.database_service.select_by_category('urgently_unimportant')

    def delegations(self):
        return self.database_service.select_delegations()
