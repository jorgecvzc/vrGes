'''
Created on 12 ene. 2023

@author: cortesj
'''

from PyQt5 import uic, QtWidgets, QtCore

'''
CLASE PARA SUBVENTANAS CON ACCESO A UN MAESTRO
'''
class ifDgMst (QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # Borrar el diálogo   
        uic.loadUi('Interfaz/Diseño/dgIfMst.ui', self)    
        self.pbAceptar.clicked.connect(self.aceptar)
        self.pbCancelar.clicked.connect(self.cancelar)
        
    def __del__(self):
        del(self.dw)
        print(f'Delete {self!s}')
        
    def aceptar(self):
        guardado = self.dw.widget().guardarSiCambios(True)
        if guardado == 1:
            self.accept()
        else:
            self.reject()
            
    def cancelar(self):
        self.reject()
        

'''
CLASE PARA MANEJAR EL DIALOGO DE BUSQUEDA DE MAESTRO
'''
class ifDgMstBusqueda(QtWidgets.QDialog):
    class TableModel(QtCore.QAbstractTableModel):
        def __init__(self, consulta=None, parent=None):
            super().__init__(parent)
            self._data = consulta
    
        def data(self, index, role):
            if index.isValid():
                if role == QtCore.Qt.DisplayRole:
                    return QtCore.QVariant(str(self._data.iloc[index.row()][index.column()]))
            return QtCore.QVariant()
        
        def rowCount(self, parent):
            return len(self._data.values)
    
        def columnCount(self, parent):
            return self._data.columns.size
   
    '''
    classdocs
    '''
    def __init__(self, control_uinfs, tipo_maestro, campos_busqueda, campos_lista, campo_devuelto='id', *args, **kwargs):
        self.model = None # Se inicia a vacio para que se pueda identificar la falta de búsqueda
        
        # Carga los parámetros de la búsqueda
        
        self.mnj = control_uinfs.mnjConsultas()
        self.campoDevuelto = campo_devuelto
                
        super().__init__(*args, **kwargs)
        uic.loadUi('Interfaz/Diseño/dgMstBusqueda.ui', self)
        
        # Variables de la clase
        self.ifCampos = {}        
        self.ifLabels = {}
        
        # Añade los campos de búsqueda
        flCampos = self.flBusqueda
        for campo in campos_busqueda:        
            self.ifLabels[campo] = QtWidgets.QLabel(campo, self)
            self.ifCampos[campo] = QtWidgets.QLineEdit(self)
            flCampos.addRow(self.ifLabels[campo], self.ifCampos[campo])
        # Pone el foco en la entrada del primer campo de busqeuta
        self.ifCampos[campos_busqueda[0]].setFocus()
           
        # Conecta la señal del botón de búsqueda y de doble click sobre la tabla  
        self.pbBuscar.clicked.connect(self.buscar)
        self.qtvResultados.doubleClicked.connect(self.close)
   
        # Carga la consulta para la búsqueda de maestros
        self.consulta = self.mnj.generaConsulta(tipo_maestro, campos_busqueda, campos_lista)
        
    '''
    Función de busqueda y de muestra de resultados
    '''
    def buscar(self):
        for (key, item) in self.ifCampos.items():
            if item.text():
                self.consulta[key] = item.text().replace(' ', '%')+'%'
            else:
                self.consulta[key] = None
                
        # Carga la consulta según los parámetros de búsqueda
        self.consulta = self.mnj.cargaConsulta(self.consulta)
        
        if not self.consulta.resultado.empty:
            self.model = self.TableModel(self.consulta.resultado)
            self.qtvResultados.setModel(self.model)
            self.qtvResultados.setFocus()
            self.lblInfo.setText('Se han encontrado {0:d} resultados'.format(self.model.rowCount(self)))
        
    def campoFilasSelec(self, campo):
        camposSel = []
        if self.model:
            valores = self.model._data[campo]
            indexes = self.qtvResultados.selectionModel().selectedRows()
            for index in sorted(indexes):
                dato = valores[index.row()]
                if not (dato in camposSel):
                    camposSel.append(dato)  
            rows = sorted(set(index.row() for index in self.qtvResultados.selectedIndexes()))
            for row in rows:
                dato = valores[row]
                if not dato in camposSel:
                    camposSel.append(dato)
        return camposSel         