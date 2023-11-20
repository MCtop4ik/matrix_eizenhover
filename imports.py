import logging
import sqlite3
import sys
from datetime import time
from functools import partial
from sqlite3 import OperationalError

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QToolBar, QLineEdit, QVBoxLayout, \
    QDialog, QDialogButtonBox, QPushButton, QComboBox, QGridLayout
from PyQt6.QtWidgets import QMainWindow


