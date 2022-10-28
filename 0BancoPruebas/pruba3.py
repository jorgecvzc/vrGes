import PyQt5 as Qt5
from PyQt5 import QtWidgets

class Window(QtWidgets.QWidget):
    def __init__(self, rows, columns):
        Qt5.QtWidgets.QWidget.__init__(self)
        self.table = Qt5.QtWidgets.QTableWidget(rows, columns, self)
        for column in range(columns):
            for row in range(rows):
                item = Qt5.QtWidgets.QTableWidgetItem('Text%d' % row)
                if row % 2:
                    item.setFlags(Qt5.QtCore.Qt.ItemIsUserCheckable |
                                  Qt5.QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(Qt5.QtCore.Qt.Unchecked)
                self.table.setItem(row, column, item)
        self.table.itemClicked.connect(self.handleItemClicked)
        layout = Qt5.QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        self._list = []

    def handleItemClicked(self, item):
        if item.checkState() == Qt5.QtCore.Qt.Checked:
            print('"%s" Checked' % item.text())
            self._list.append(item.row())
            print(self._list)
        else:
            print('"%s" Clicked' % item.text())

if __name__ == '__main__':

    import sys
    app = Qt5.QtWidgets.QApplication(sys.argv)
    window = Window(6, 3)
    window.resize(350, 300)
    window.show()
    sys.exit(app.exec_())