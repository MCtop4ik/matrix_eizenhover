from database import Database
from imports import *


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
