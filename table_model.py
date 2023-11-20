from database import Database
from imports import *


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = list(map(lambda arr: arr[:4], data))
        self.database_service = Database()

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 3:
                return self.database_service.get_category_name_by_id(self._data[index.row()][index.column()])[0]
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return ['id', 'name', 'description', 'category'][section]
