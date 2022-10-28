'''
Created on 4 sept. 2020

@author: cortesj
'''
from PyQt5 import QtWidgets
from PyQt5 import uic
from Control import Control
from mnjDgPedidos import ifPedidos
from mnjWdArticulos import ifArticulos, ifModificadoresArt, ifVariantesArt
from mnjWdTrabajos import ifTrabajos, ifProcesos, ifTareas, ifPosiciones


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("Diseño/mwVRGES.ui", self)
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
        self.uis = {'Pedidos': (lambda x: ifPedidos(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))), 
               'Articulos': (lambda x: ifArticulos(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))),
               'ModificadoresArt': (lambda x: ifModificadoresArt(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))),
               'VariantesArt': (lambda x: ifVariantesArt(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))),
               'Posiciones': (lambda x: ifPosiciones(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))),
               'Tareas': (lambda x: ifTareas(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))),
               'Procesos': (lambda x: ifProcesos(mnj=self.cm.nuevoManejador(Maestros=ifs[x]))),
               'Trabajos': (lambda x: ifTrabajos(mnj=self.cm.nuevoManejador(Maestros=ifs[x])))
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
            ui = self.uis.get(if_nombre, lambda: None)(if_nombre)
            if ui:
                self.mdiArea.addSubWindow(ui)
                ui.showMaximized()
    
                ui.show()
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
                    self.mdiArea.activeSubWindow().widget().logImpMaestro()
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
            self.mdiArea.activeSubWindow().widget().vePosicion(mov)
    
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow(Control('..'))
    ui.show()
    sys.exit(app.exec_())
