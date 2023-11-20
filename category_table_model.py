from database import Database
from imports import *


class CategoryTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(CategoryTableModel, self).__init__()
        self._data = list(map(lambda arr: arr[1:3], data))
        self.database_service = Database()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ['name', 'description'][section]
