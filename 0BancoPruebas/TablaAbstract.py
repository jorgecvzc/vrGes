from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import operator

# This class was generated from the Qt Creator
class Ui_tableView_ex(object):
    def setupUi(self, tableView_ex):
        tableView_ex.setObjectName("tableView_ex")
        tableView_ex.resize(800, 600)
        self.centralwidget = QWidget(tableView_ex)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.myTable = QTableView(self.centralwidget)
        self.myTable.setObjectName("monTablo")
        self.gridLayout.addWidget(self.myTable, 0, 0, 1, 1)
        tableView_ex.setCentralWidget(self.centralwidget)

        self.retranslateUi(tableView_ex)
        QMetaObject.connectSlotsByName(tableView_ex)

    def retranslateUi(self, tableView_ex):
        _translate = QCoreApplication.translate
        tableView_ex.setWindowTitle(_translate("tableView_ex", "MainWindow"))


class TableTest(QMainWindow, Ui_tableView_ex):
    def __init__(self, datos, parent=None):
        super(TableTest, self).__init__(parent)
        self.setupUi(self)

        self.model = TableModel(datos)
        self.myTable.setModel(self.model)
        self.myTable.setShowGrid(False)

        self.hView = HeaderView(self.myTable)
        self.myTable.setHorizontalHeader(self.hView)
        self.myTable.verticalHeader().hide()

        # adding alternate colours
        self.myTable.setAlternatingRowColors(True)
        self.myTable.setStyleSheet("alternate-background-color: rgb(209, 209, 209)"
                                   "; background-color: rgb(244, 244, 244);")

        # self.myTable.setSortingEnabled(True)
        # self.myTable.sortByColumn(1, Qt.AscendingOrder)


class HeaderView(QHeaderView):
    def __init__(self, parent):
        QHeaderView.__init__(self, Qt.Horizontal, parent)
        datos = Datos()
        self.model = TableModel(datos)
        self.setModel(self.model)

        # Setting font for headers only
        self.font = QFont("Arial", 24)
        self.setFont(self.font)

        # Changing section backgroud color. font color and font weight
        self.setStyleSheet("::section{background-color: pink; color: green; font-weight: bold}")

        self.setSectionResizeMode(1)
        self.setSectionsClickable(True)

class Datos(object):
    def __init__(self):
        self.cabeceras  = ["Name", "Age", "Grades"]
        self.datos = [["George", "26", "80%"],
                       ["Bob", "16", "95%"],
                       ["Martha", "22", "98%"]] 
        
class TableModel(QAbstractTableModel):

    def __init__(self, datos):
        QAbstractTableModel.__init__(self)
        super(TableModel, self).__init__()

        self.headers = datos.cabeceras
        self.data = datos.datos 

    def update(self, in_data):
        self.data = in_data

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def setData(self, index, value, role=None):
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            col = index.column()
            self.data[row][col] = value
            return True

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self.data[row][col]
            return value

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers

    def flags(self, index):
        fl = super(self.__class__,self).flags(index)
        fl |= Qt.ItemIsEditable
        fl |= Qt.ItemIsSelectable
        fl |= Qt.ItemIsEnabled
        fl |= Qt.ItemIsDragEnabled
        fl |= Qt.ItemIsDropEnabled
        return fl
# -----------------NOT WORKING!!!---------------
# =================================================

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self.data = sorted(self.data, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.data.reverse()
        self.layoutChanged.emit()
# =================================================


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    datos = Datos()
    main_window = TableTest(datos)
    main_window.show()
    app.exec_()
    print(datos.datos)
    sys.exit()
    