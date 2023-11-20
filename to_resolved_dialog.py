from database import Database
from imports import *


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