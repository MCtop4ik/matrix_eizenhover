from database import Database
from imports import *


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
            if self.category == 'urgently_unimportant':
                self.database_service.insert_in_delegations(task_id)
            self.accept()
        except IndexError:
            self.reject()
        except ValueError:
            self.reject()
