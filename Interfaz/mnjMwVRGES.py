'''
Created on 4 sept. 2020

@author: cortesj
'''
import sys
from PyQt5 import QtWidgets
from PyQt5 import uic
from Interfaz.mnjDgPedidos import ifPedidos
from Interfaz.ifArticulos import ifArticulos, ifModificadoresArt, ifVariantesArt
from Interfaz.ifTrabajos import ifTrabajos, ifProcesos, ifTareas, ifPosiciones


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("Interfaz/Diseño/mwVRGES.ui", self)
        self.cm = mc
        
        ifs = {'Pedidos': ['Pedido', 'Articulo'], 
               'Articulos': ['Articulo'],
               'Posiciones': ['Posicion'], 
               'Tareas': ['Tarea'],
               'Procesos': ['Proceso', 'Tarea'],
               'Trabajos': ['Trabajo', 'Proceso','Tarea', 'Posicion', 'Cliente', 'Articulo'],
               'ModificadoresArt': ['ModificadorArt'],
               'VariantesArt': ['VarianteArt']
               }
        self.uis = {'Pedidos': (lambda: ifPedidos(self.cm)), 
               'Articulos': (lambda: ifArticulos(self.cm)),
               'ModificadoresArt': (lambda: ifModificadoresArt(self.cm)),
               'VariantesArt': (lambda: ifVariantesArt(self.cm)),
               'Posiciones': (lambda: ifPosiciones(self.cm)),
               'Tareas': (lambda: ifTareas(self.cm)),
               'Procesos': (lambda: ifProcesos(self.cm)),
               'Trabajos': (lambda: ifTrabajos(self.cm))
               }

        self.actPedidos.triggered.connect(lambda: self.abrirVentana('Pedidos'))
        self.actArticulos.triggered.connect(lambda: self.abrirVentana('Articulos'))
        self.actVariantesArt.triggered.connect(lambda: self.abrirVentana('VariantesArt'))
        self.actModificadoresArt.triggered.connect(lambda: self.abrirVentana('ModificadoresArt'))
        self.actPosiciones.triggered.connect(lambda: self.abrirVentana('Posiciones'))
        self.actTareas.triggered.connect(lambda: self.abrirVentana('Tareas'))
        self.actProcesos.triggered.connect(lambda: self.abrirVentana('Procesos'))
        self.actTrabajos.triggered.connect(lambda: self.abrirVentana('Trabajos'))
        
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
        
    def abrirVentana(self, if_nombre):
        try:    
            ui = self.uis.get(if_nombre, lambda: None)()
            if ui:
                self.mdiArea.addSubWindow(ui)
                ui.showMaximized()
                ui.primeraAccion()
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error")
            msg.setText("Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()        

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

