from database import Database
from imports import *


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
        try:
            self.database_service.add_cell(
                self.cell_name.text(),
                self.cell_description.text(),
                self.database_service.get_category_id_by_name(self.cell_category.currentText())[0]
            )
            self.accept()
        except ValueError:
            QMessageBox.critical(self, 'Error adding', 'You re not allowed to add empty row')
