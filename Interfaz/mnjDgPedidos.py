'''
Created on 19 dic. 2018

@author: cortesj
'''
from PyQt5 import QtWidgets, QtCore, uic
from Control import Control
from Interfaces import ifMaestro

class ifPedidos(QtWidgets.QDialog, ifMaestro):
    '''
    classdocs
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, tipo_maestro="Pedido")
        uic.loadUi("Diseño/dgPedidos.ui", self)
        
        '''
        Crea los ifCanpos que enlazaran los objetos del maestro con los de la interfaz
        '''
        mst_cli = self.mnj.nuevoMaestro('Cliente')
        mst_cli.setId(0)
        cons = self.mnj.consultaMaestros(mst_cli, None, ['id', 'nombre'], ["nombre"])
        self.nuevoIfCampo('cliente', 'ifIdListaD', self.leCliente, self.cbCliNombre, list(cons['id']), list(cons['nombre']))
                
        self.nuevoIfCampo('contacto', 'ifCadena', self.leContacto)        

        self.twLineasCols = {'refArticulo':'Artículo', 'nombre':'Nombre', 'cantidad':'Cantidad'}
        self.nuevoIfCampo('lineas', 'ifTabla', self.twLineas, self.twLineasCols)
        
        #self.twLineas.cellChanged.connect(self.actualizaMstLineas)
        
        self.twLineas.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.twLineas.customContextMenuRequested.connect(self.menuTwLineas)
        
        self.veAnterior()
                
    def menuTwLineas(self, position):
        menu = QtWidgets.QMenu()
        insertAction = menu.addAction("Inserta Fila")
        borraAction = menu.addAction("Borra Fila")
        action = menu.exec_(self.twLineas.mapToGlobal(position))
        self.senyalMaestro.deshabilitaSenyal('Pedido', 'lineas')                
        if action == insertAction:
            if self.twLineas.currentRow() < 0:
                self.twLineas.setRowCount(1)
                self.maestro['lineas'].nuevaFila()                
            else:
                self.maestro['lineas'].nuevaFila(self.twLineas.currentRow())                
                self.twLineas.insertRow(self.twLineas.currentRow())
        elif action == borraAction:
            if self.twLineas.currentRow() >= 0:
                self.maestro['lineas'].borraFila(self.twLineas.currentRow())
                self.twLineas.removeRow(self.twLineas.currentRow())
        self.senyalMaestro.habilitaSenyal('pedido', 'lineas')

    # Actualizcion del maestro principal desde campos especiales
    def actualizaMaestro(self, nombre_campo, valor):
        # Si se ha modificado un referencia de articulo en las lineas del pedido, se deshabilita su señal para que no hayan bucles
        #  se carga la nueva linea a traves de los dependientes de la clave principal y se propaga la señal inicial
        if (nombre_campo == 'lineas'):
            tabla = self.cmpEditables[nombre_campo]
            pos = tabla.posActual()
            if (tabla.campos[pos[1]] == 'refArticulo'):
                mst_articulo = self.mnj.nuevoMaestro('Articulo')
                mst_articulo['ref'] = (tabla.valorActual()+'%').upper()
                mst_articulo = self.mnj.cargaMaestro('Articulo', nombre_campo, mst_articulo, condicion='pi')
                self.maestro[nombre_campo].setValor(pos[0], 'articulo', mst_articulo.getId())            
            else:
                super().actualizaMaestro(nombre_campo, valor)
        else:
            super().actualizaMaestro(nombre_campo, valor)
              

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ifPedidos(mnj=Control('..').nuevoManejador(['Pedido', 'Articulo']))
    ui.show()
    sys.exit(app.exec_())

        
    
