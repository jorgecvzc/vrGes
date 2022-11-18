import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 table - pythonspot.com'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

        # Show widget
        self.show()

    def createTable(self):
       # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
        self.tableWidget.setItem(0,1, QTableWidgetItem("Cell (1,2)"))
        self.tableWidget.setItem(1,0, QTableWidgetItem("Cell (2,1)"))
        self.tableWidget.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
        self.tableWidget.setItem(2,0, QTableWidgetItem("Cell (3,1)"))
        self.tableWidget.setItem(2,1, QTableWidgetItem("Cell (3,2)"))
        self.tableWidget.setItem(3,0, QTableWidgetItem("Cell (4,1)"))
        self.tableWidget.setItem(3,1, QTableWidgetItem("Cell (4,2)"))
        self.tableWidget.move(0,0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())  


import sys
from PyQt5 import QtCore, QtWidgets

class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.edit = QtWidgets.QLineEdit()
        self.combo = QtWidgets.QComboBox()
        self.table = QtWidgets.QTableWidget(3, 3)
        self.button = QtWidgets.QPushButton('Disable Table Tabbing', self)
        self.button.clicked.connect(self.handleButton)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.edit, 0, 0)
        layout.addWidget(self.combo, 0, 1)
        layout.addWidget(self.table, 1, 0, 1, 2)
        layout.addWidget(self.button, 2, 0, 1, 2)
        self.table.installEventFilter(self)
        self.edit.setFocus()

    def handleButton(self):
        if self.table.tabKeyNavigation():
            self.button.setText('Enable Table Tabbing')
            self.table.setTabKeyNavigation(False)
        else:
            self.button.setText('Disable Table Tabbing')
            self.table.setTabKeyNavigation(True)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.table and source.isEnabled() and
            source.tabKeyNavigation()):
            index = self.table.currentIndex()
            if event.key() == QtCore.Qt.Key_Backtab:
                if index.row() == index.column() == 0:
                    QtWidgets.QAbstractScrollArea.focusNextPrevChild(
                        self.table, False)
                    return True
            elif event.key() == QtCore.Qt.Key_Tab:
                model = self.table.model()
                if (index.row() == model.rowCount() - 1 and
                    index.column() == model.columnCount() - 1):
                    QtWidgets.QAbstractScrollArea.focusNextPrevChild(
                        self.table, True)
                    return True
        return super(Window, self).eventFilter(source, event)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(600, 100, 400, 250)
    window.show()
    sys.exit(app.exec_())