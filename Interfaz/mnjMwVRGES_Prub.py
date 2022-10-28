'''
Created on 4 sept. 2020

@author: cortesj
'''
from Diseño.mwVRGES import Ui_MainWindow
from mnjDgPedidos2 import uidPedidos 
from PyQt5 import QtWidgets
from Manejadores import ControlManejadores

class uid(Ui_MainWindow):
    def __init__(self, mc):
        super().__init__()
        self.cm = mc
        
    def abrirVentana(self):
        Dialog = QtWidgets.QDialog()
        mnj = self.cm.nuevoManejador(['Pedido','Articulo'])
        ui = uidPedidos(self, mnj)
        ui.show()
           
        
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.actionTareas.triggered.connect(self.abrirVentana)
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = uid(ControlManejadores('..'))
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
