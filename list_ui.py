from category_table_model import CategoryTableModel
# from delegate import Delegate
from imports import *
# from infinity_list import InfinityList
from list_adding_dialog import ListAddingDialog


class ListUI:

    def add_to_list(self, category):
        dlg = ListAddingDialog(category=category)
        if dlg.exec():
            self.destroy()
            # if category == 'not_in_infinity_list':
            #     infinity_list_window = InfinityList()
            #     infinity_list_window.show()
            # if category == 'urgently_unimportant':
            #     delegation_window = Delegate()
            #     delegation_window.show()

    def generate_table(self, data):
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
            label.show()
            layout.addWidget(label)
        return layout