from eisenhower_matrix import EisenhowerMatrix
from imports import logging
from imports import QApplication
from imports import sys


if __name__ == '__main__':
    logging.basicConfig(filename='log/journal.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logging.info("Running application")
    app = QApplication(sys.argv)
    ex = EisenhowerMatrix()
    ex.show()
    sys.exit(app.exec())
