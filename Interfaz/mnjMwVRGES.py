'''
Created on 4 sept. 2020

@author: cortesj
'''
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from Interfaz.mnjDgPedidos import ifPedidos
from Interfaz.ifArticulos import ifArticulos, ifModificadoresArt, ifVariantesArt, ifPosiciones
from Interfaz.ifTrabajos import ifTrabajos, ifProcesos, ifTareas
from Interfaz import ifPersonas


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mc, *args, **kwargs):
        super().__init__(*args, **kwargs)
                 
        uic.loadUi("Interfaz/Diseño/mwVRGES.ui", self)
        self.cm = mc

        self.uis = {'actPedidos': (lambda: ifPedidos(self.cm)), 
               'actArticulos': (lambda: ifArticulos(self.cm)),
               'actModificadoresArt': (lambda: ifModificadoresArt(self.cm)),
               'actVariantesArt': (lambda: ifVariantesArt(self.cm)),
               'actPosiciones': (lambda: ifPosiciones(self.cm)),
               'actTareas': (lambda: ifTareas(self.cm)),
               'actProcesos': (lambda: ifProcesos(self.cm)),
               'actTrabajos': (lambda: ifTrabajos(self.cm)),
               'actPosiciones': (lambda: ifPosiciones(self.cm)),
               
               'actClientes': (lambda: ifPersonas.ifClientes(self.cm)),
               'actProveedores': (lambda: ifPersonas.ifProveedores(self.cm)),
               }
        
        self.mnuMaestros.triggered.connect(self.abrirVentana)

        self.salirAction = QtWidgets.QAction('Salir', self)
        self.mnuPrinc.addAction(self.salirAction)
        self.salirAction.triggered.connect(self.close)
        
        
        self.mdiArea.cascadeSubWindows()

        self.actOpNuevo.triggered.connect(lambda: self.acMaestro('n'))
        self.actOpGuardar.triggered.connect(lambda: self.acMaestro('g'))
        self.actOpEliminar.triggered.connect(lambda: self.acMaestro('e'))
        self.actOpBuscar.triggered.connect(lambda: self.acMaestro('b'))
        
        self.actOpRegPrimero.triggered.connect(lambda: self.veMaestro('pri'))
        self.actOpRegAnterior.triggered.connect(lambda: self.veMaestro('ant'))
        self.actOpRegSiguiente.triggered.connect(lambda: self.veMaestro('sig'))
        self.actOpRegUltimo.triggered.connect(lambda: self.veMaestro('ult'))
        
        self.actCerrarVentana.triggered.connect(lambda: self.cerrarVentana())
        
        self.actLogImp.triggered.connect(lambda: self.acMaestro('i'))

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def abrirVentana(self, action):
        if (action.objectName() != 'actCerrarVentana'):
            try:
                ui = self.uis.get(action.objectName(), lambda: None)()
                if ui:
                    self.mdiArea.addSubWindow(ui)
                    ui.showMaximized()
                    ui.primeraAccion()
            except:
                error_dialog = QtWidgets.QErrorMessage(self)
                error_dialog.setWindowModality(QtCore.Qt.WindowModal)
                error_dialog.showMessage("Error inesperado: " + 
                                         str(sys.exc_info()[0]) +'\n' + 
                                         str(sys.exc_info()[1]))                
                #msg = QtWidgets.QMessageBox()
                #msg.setIcon(QtWidgets.QMessageBox.Information)
                #msg.setWindowTitle("Mensaje Error")
                #msg.setText("Error inesperado: " + str(sys.exc_info()[0]))
                #msg.setInformativeText(str(sys.exc_info()[1]))
                #msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            
    def cerrarVentana(self):
        try:
            if self.mdiArea.activeSubWindow():
                if self.mdiArea.activeSubWindow().widget().guardarSiCambios():
                    self.mdiArea.activeSubWindow().close()
            else:
                self.close()
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error")
            msg.setText("[Menu->Cerrar Ventana] Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()   
                
    def acMaestro(self, accion):
        try:
            if self.mdiArea.activeSubWindow():
                if (accion == 'n'):
                    self.mdiArea.activeSubWindow().widget().nuevo()
                elif (accion == 'g'):
                    self.mdiArea.activeSubWindow().widget().almacena()
                elif (accion == 'e'):
                    self.mdiArea.activeSubWindow().widget().borra()                    
                elif (accion == 'b'):
                    self.mdiArea.activeSubWindow().widget().abrirBusquedaMaestro()
                elif (accion == 'i'):
                    self.mdiArea.activeSubWindow().widget().logImp()
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error")
            msg.setText("[Menu->Abrir Ventana] Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
                
            
    def veMaestro(self, mov):
        if (self.mdiArea.activeSubWindow()) and (self.mdiArea.activeSubWindow().widget()):
            self.mdiArea.activeSubWindow().widget().cargaMaestro(mov)

