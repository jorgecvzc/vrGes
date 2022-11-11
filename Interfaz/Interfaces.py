'''
Created on 4 mar. 2019

@author: cortesj
'''
import sys

import PyQt5 as Qt5
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMessageBox, QShortcut

import pandas as pd

from Señales import TunelSenyal
import log


'''
CLASE PARA MANEJAR EL DIALOGO DE BUSQUEDA DE MAESTRO
'''
class ifDgMstBusqueda(Qt5.QtWidgets.QDialog):
    class TableModel(Qt5.QtCore.QAbstractTableModel):
        def __init__(self, consulta=None, parent=None):
            super().__init__(parent)
            self._data = consulta
    
        def data(self, index, role):
            if index.isValid():
                if role == Qt5.QtCore.Qt.DisplayRole:
                    return Qt5.QtCore.QVariant(str(self._data.iloc[index.row()][index.column()]))
            return Qt5.QtCore.QVariant()
        
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
        
        self.mnj = control_uinfs.mnjConsulta()
        self.campoDevuelto = campo_devuelto
                
        super().__init__(*args, **kwargs)
        uic.loadUi('Interfaz/Diseño/dgMstBusqueda.ui', self)

        # Variables de la clase
        self.ifCampos = {}        
        self.ifLabels = {}
        
        # Añade los campos de búsqueda
        flCampos = self.flBusqueda
        for campo in campos_busqueda:        
            self.ifLabels[campo] = Qt5.QtWidgets.QLabel(campo, self)
            self.ifCampos[campo] = Qt5.QtWidgets.QLineEdit(self)
            flCampos.addRow(self.ifLabels[campo], self.ifCampos[campo])
        # Pone el foco en la entrada del primer campo de busqeuta
        self.ifCampos[campos_busqueda[0]].setFocus()
           
        # Conecta la señal del botón de búsqueda y de doble click sobre la tabla  
        self.pbBuscar.clicked.connect(self.buscar)
        self.qtvResultados.doubleClicked.connect(self.close)
   
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
        

        
'''
CLASES DE UNION ENTRE INTERFAZ Y CAMPOS DE UN MAESTRO
'''
class ifCadena(object):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, conMst, campo, qt_line_edit):
        self.qle = qt_line_edit
        self.qle.__dict__['ifCampo'] = self # Los campos qt apuntarán al campo de interfaz que los engloba para poder procesar eventos como los del teclado
        self.campo = campo
        self.qle.editingFinished.connect(lambda: conMst.actualizaMaestro(campo, self.getValor()))

    def getValor(self):
        return self.qle.text()
    
    def setValor(self, valor):
        self.qle.setText(str(valor))
        
    def limpia(self):
        self.qle.clear()
        
    def procesaTeclas(self, key):
        if key == Qt5.QtCore.Qt.Key_Return:
            print('return key pressed')
        else:
            print('key pressed: %s' % key)

class ifTexto(object):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, conMst, campo, qt_ptext_edit):
        self.qpe = qt_ptext_edit
        self.qpe.textChanged.connect(lambda: conMst.actualizaMaestro(campo, self.getValor()))

    def getValor(self):
        return self.qpe.toPlainText()
    
    def setValor(self, texto):
        if (texto) or (texto == ""):
            self.qpe.appendPlainText(texto)
        else:
            self.limpia()
        
    def limpia(self):
        self.qpe.blockSignals(True)        
        self.qpe.clear()
        self.qpe.blockSignals(False)        
    
    
class ifVerificacion(object):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, conMst, campo, qt_checkbox, qts_habilitados=None):
        self.chb = qt_checkbox
        self.qtsHabil = qts_habilitados
        self.chb.stateChanged.connect(lambda: self.actualizaValidador(conMst, campo))

    def getValor(self):
        return self.chb.isChecked()
    
    def setValor(self, estado):
        self.chb.blockSignals(True)        
        self.chb.setChecked(estado)
        self.validaCampos()
        self.chb.blockSignals(False)        
        
    def limpia(self):
        self.chb.blockSignals(True)        
        self.chb.setChecked(False)
        self.chb.blockSignals(False)              

    def actualizaValidador(self, conMst, campo):
        conMst.actualizaMaestro(campo, self.getValor())
        self.validaCampos()
        
    def validaCampos(self):
        if self.qtsHabil:
            for elem in self.qtsHabil:
                elem.setEnabled(self.getValor())
    
class ifListaD(object):
    '''
    Objetos de interfaz que muestran una lista desplegable para seleccionar un elemento e internamente su índice
    '''
    def __init__(self, conMst, campo, qtComboBox, lista_ids, lista_datos):
        self.qcb = qtComboBox
        self.qcb.clear()
        self.qcb.addItems(['']+lista_datos)
        self.lid = ['']+lista_ids
        self.qcb.currentIndexChanged.connect(lambda: conMst.actualizaMaestro(campo, self.getValor())) 

    def getValor(self):
        if self.qcb.currentIndex():
            return int(self.lid[self.qcb.currentIndex()])
        else:
            return None
                
    def setValor(self, valor):
        if valor:
            self.qcb.blockSignals(True)          
            self.qcb.setCurrentIndex(self.lid.index(int(valor)))
            self.qcb.blockSignals(False)
        else:
            self.limpia()
     
    def limpia(self):
        self.qcb.blockSignals(True)            
        self.qcb.setCurrentIndex(0)
        self.qcb.blockSignals(False)
            
class ifIdListaD(object):
    '''
    Objetos de interfaz que muestran un indice y su correspondencia en una lista desplegable
    '''
    def __init__(self, conMst, campo, qtLineEdit, qtComboBox, lista_ids, lista_datos):
        self.qle = qtLineEdit
        self.qle.textEdited.connect(self.__cambioLE)
        
        self.qcb = qtComboBox
        self.qcb.clear()
        self.qcb.addItems(['']+lista_datos)
        self.lid = ['']+lista_ids
        self.qcb.currentIndexChanged.connect(self.__cambioCB)
        
        self.qcb.currentIndexChanged.connect(lambda: conMst.actualizaMaestro(campo, self.getValor())) 
        # args[0].editingFinished.connect(lambda: self.conMst.actualizaMaestro(campo, self.cmpEditables[campo].getValor()))
        # args[1].activated.connect(lambda: self.conMst.actualizaMaestro(campo, self.cmpEditables[campo].getValor()))  
        

    def getValor(self):
        if self.qle.text():
            return int(self.qle.text())
        else:
            return None
            
    def setValor(self, valor):
        self.qcb.blockSignals(True)
        if valor:
            self.qcb.setCurrentIndex(self.lid.index(int(valor)))
            self.qle.blockSignals(True)
            self.qle.setText((str(valor)))
            self.qle.blockSignals(False)
        else:
            self.limpia()
            
        self.qcb.blockSignals(False)
     
    def limpia(self):
        self.qle.blockSignals(True)
        self.qcb.blockSignals(True)
        self.qcb.setCurrentIndex(0)
        self.qle.clear()           
        self.qcb.blockSignals(False)
        self.qle.blockSignals(False)                               
                                   
    def __cambioLE(self, dato):
        if (dato):
            try:
                idl = int(dato)
                if idl in self.lid:
                    self.qcb.setCurrentIndex(self.lid.index(idl))
            except ValueError:
                self.qle.blockSignals(True)
                msg = QMessageBox()
                msg.setIcon(Qt5.QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("Mensaje Error")
                msg.setText("[Interfaces-IfMaestro] Valor [ " + str(dato) + " ] erróneo")
                msg.setInformativeText("El dato introducido ha de ser un entero")
                msg.setStandardButtons(Qt5.QtWidgets.QMessageBox.Ok)
                msg.exec_()
                self.qle.clear()
                self.qle.blockSignals(False)
                
        else:
            self.qcb.setCurrentText('')
            
        
    def __cambioCB(self, i):
        self.qle.setText(str(self.lid[i]))

            
class ifRefListaD(object):
    '''
    Objetos de interfaz que muestran una referencia alfanumérica y su correspondencia en una lista desplegable
    '''
    def __init__(self, conMst, campo, qtLineEdit, qtComboBox, lista_mst):
        self.qle = qtLineEdit
        self.qle.textEdited.connect(self.__cambioLE)

        self.lista = lista_mst[0].lista
        campos = lista_mst[1]
        self.lId =  ['']+[l.getId() for l in self.lista]
        self.lRef = ['']+[l[campos[0]] for l in self.lista]
        self.lista = ['']+self.lista
        self.qcb = qtComboBox
        self.qcb.clear()
        self.qcb.addItems(['']+lista_mst[0].col(campos[1]))
        
        #self.qcb.currentIndexChanged.connect(self.__cambioCB)
        
        self.qcb.currentIndexChanged.connect(lambda: conMst.actualizaMaestro(campo, self.getValor())) 
        # args[0].editingFinished.connect(lambda: self.conMst.actualizaMaestro(campo, self.cmpEditables[campo].getValor()))
        # args[1].activated.connect(lambda: self.conMst.actualizaMaestro(campo, self.cmpEditables[campo].getValor()))  
        

    def getValor(self):
        texto = self.qle.text() 
        if texto:
            return self.lista[self.lRef.index(texto)]
        else:
            return None
            
    def setValor(self, valor):
        self.qcb.blockSignals(True)
        if valor:
            listind = self.lId.index(valor.getId())
            self.qcb.setCurrentIndex(listind)
            self.qle.blockSignals(True)
            self.qle.setText(self.lRef[listind])
            self.qle.blockSignals(False)
        else:
            self.limpia()
            
        self.qcb.blockSignals(False)
     
    def limpia(self):
        self.qle.blockSignals(True)
        self.qcb.blockSignals(True)
        self.qcb.setCurrentIndex(0)
        self.qle.clear()           
        self.qcb.blockSignals(False)
        self.qle.blockSignals(False)                               
                                   
    def __cambioLE(self, dato):
        if (dato):
            try:
                if dato in self.lRef:
                    idl = self.lId[self.lref.index(dato)]
                    self.qcb.setCurrentIndex(self.lId.index(idl))
            except ValueError:
                self.qle.blockSignals(True)
                msg = QMessageBox()
                msg.setIcon(Qt5.QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("Mensaje Error")
                msg.setText("[Interfaces-IfMaestro] Valor [ " + str(dato) + " ] erróneo")
                msg.setInformativeText("El dato introducido ha de ser un entero")
                msg.setStandardButtons(Qt5.QtWidgets.QMessageBox.Ok)
                msg.exec_()
                self.qle.clear()
                self.qle.blockSignals(False)
                
        else:
            self.qcb.setCurrentText('')
            
        
    def __cambioCB(self, i):
        self.qle.setText(str(self.lref[i]))
                
        
class ifTabla(object):
    '''
    Objetos de interfaz para el manejo de tablas
    '''
    def __init__(self, conMst, campo, qtTableWidget, dict_cols, con_mst, mst_campo):
        self.qtw = qtTableWidget
        self.campos = list(dict_cols.keys())
        # Los objetos complejos tienen que tener acceso al maestro ya que tienen señales internas de modificación
        self.conMst = con_mst
        self.mstCampo = mst_campo
        # Se crean las columnas de la tabla según la lista paada
        self.qtw.setColumnCount(len(self.campos))
        i = 0
        for s in self.campos:
            self.qtw.setHorizontalHeaderItem(i, Qt5.QtWidgets.QTableWidgetItem(dict_cols[s]))
            i+=1

        # Se acopla el menú contextual genérico de las tablas
        self.qtw.setContextMenuPolicy(Qt5.QtCore.Qt.CustomContextMenu)
        self.qtw.customContextMenuRequested.connect(lambda pos: self.menuIfTabla(pos))       
        # Asigna los tratamientos especiales para teclas de control de movimiento
        #Qt5.QtWidgets.QShortcut(Qt5.QtCore.Qt.Key_Tab, self.cmpEditables[campo].qtw, activated=lambda: self.trataTab(campo))
        
        
        # porc_col = .98/len(self.campos)
        #self.qtw.setColumnWidth(i,self.qtw.width()*porc_col)
        #self.qtw.setSizeAdjustPolicy(Qt5.QtWidgets.QAbstractScrollArea.AdjustToContents)
        #self.qtw.resizeColumnsToContents()
        cabecera = self.qtw.horizontalHeader() 
        for i in range(self.qtw.columnCount()-1):
            cabecera.setSectionResizeMode(i, Qt5.QtWidgets.QHeaderView.ResizeToContents)
        i += 1
        cabecera.setSectionResizeMode(i, Qt5.QtWidgets.QHeaderView.Stretch)
        
        self.qtw.itemChanged.connect(lambda: conMst.actualizaMaestro(campo, self))
        
        
    def menuIfTabla(self, posicion):
        menu = Qt5.QtWidgets.QMenu()
        insertAction = menu.addAction("Inserta Fila")
        borraAction = menu.addAction("Borra Fila")
        agregAction = menu.addAction("Agrega Fila")
        action = menu.exec_(self.qtw.mapToGlobal(posicion))
        #self.senyalMaestro.deshabilitaSenyal(self.tipo_maestro, campo)
        campo = self.conMst.getCampo(self.mstCampo)
        if action == insertAction:
            if self.qtw.currentRow() < 0:
                campo.nuevaFila()                
            else:
                campo.nuevaFila(self.qtw.currentRow())                
        elif action == borraAction:
            if (self.qtw.currentRow() >= 0):
                campo.borraFila(self.qtw.currentRow())
        elif action == agregAction:
            campo.nuevaFila()

    def trataTab(self, campo):
        #event = Qt5.QtGui.QKeyEvent(Qt5.QtCore.QEvent.KeyPress, Qt5.QtCore.Qt.Key_Tab, Qt5.QtCore.Qt.NoModifier)
        #Qt5.QtCore.QCoreApplication.postEvent(self, event)
        qtw = self.qtw
        lin = qtw.currentRow()
        col = qtw.currentColumn()
        if (col == qtw.columnCount()-1):
            if (lin == qtw.rowCount()-1):
                self.maestro[campo].nuevaFila()
                qtw.insertRow(qtw.rowCount()) 
                qtw.setCurrentCell(lin+1, 0)
            else:
                qtw.setCurrentCell(lin+1, 0)
        else:
            qtw.setCurrentCell(lin, col+1)
                                
    def setColPropiedades(self, nombre_col, *args):
        i = self.campos.index(nombre_col)
        self.qtw.setHorizontalHeaderItem(i, Qt5.QtWidgets.QTableWidgetItem(args[0]))
        
    def nombreCol(self, pos):
        return self.campos[pos]
            
    def getValor(self, lin, col):
        return self.qtw.cellWidget(lin, self.campos.index(col))
    
    def setValor(self, lin, col, valor):
        if isinstance(col, str):
            coln = self.campos.index(col)
        else:
            coln = col
            
        self.qtw.blockSignals(True)
        if isinstance(valor, bool):
            chkBox = Qt5.QtWidgets.QCheckBox(parent=self.qtw)
            chkBox.setChecked(valor)
            chkBox.stateChanged.connect(self.trataPulsaBoton)
            self.qtw.setCellWidget(lin, coln, chkBox)          
        else:
            self.qtw.setItem(lin, coln, Qt5.QtWidgets.QTableWidgetItem(str(valor)))
        self.qtw.blockSignals(False)
    
    def trataPulsaBoton(self):
        ch = self.qtw.sender()
        print(ch.parent())
        ix = self.qtw.indexAt(ch.pos())
        self.conMst.getCampo(self.mstCampo).setValor(ix.row(), self.nombreCol(ix.column()), ch.isChecked())
        
    def agregaFila(self, valores=None):
        nfil = self.qtw.rowCount()
        self.qtw.insertRow(nfil)
        if valores:
            i = 0
            for campo in self.campos:
                self.setValor(nfil, i, valores[campo])
                i += 1
    
    def posActual(self):
        return (self.qtw.currentRow(), self.qtw.currentColumn())
    
    def valorActual(self):
        pos = self.posActual()
        if type(self.qtw.cellWidget(pos[0], pos[1])) == Qt5.QtWidgets.QCheckBox:
            return self.qtw.cellWidget(pos[0], pos[1]).isChecked()
            #return (self.qtw.item(pos[0],pos[1]).checkState() == 2)
        else:
            return self.qtw.item(pos[0],pos[1]).text()
    
    def limpia(self):
        for i in range(self.qtw.rowCount()-1,-1, -1):
            self.qtw.removeRow(i)


class ifConexionMst(object):
    def __init__(self, manejador, tipo_maestro, funcion_enlace):
        self.log = log.ini_logger(__name__)
        # La funcion_enlace asigna la función para que el Maestro haga modificaciones en la interfaz
        self.mnj = manejador
        self.tipo_maestro = tipo_maestro # Inficará el tipo de maestro cuyos registros va a editar la interfaz
        self.maestro = self.mnj.nuevoMaestro(self.tipo_maestro, etiqueta=self.tipo_maestro) # Por defecto carga un maestro en blanco
         
        # Genera la clase de tunel de sñales para la propagación en la interfaz de los cambios en el maestro principal
        self.senyalMaestro = TunelSenyal('if'+tipo_maestro.capitalize())
        self.senyalMaestro.asignaTunel(funcion_enlace)
        # Habilita el tunel entre el Maestro y la Interfaz del maestro
        self.maestro.asignaTunelSenyal(self.senyalMaestro)
        self.senyalMaestro.habilitaTunel()

    def nuevoMaestro(self):
        self.maestro = self.mnj.nuevoMaestro(self.tipo_maestro, etiqueta=self.tipo_maestro)
        
    def actualizaMaestro(self, nombre_campo, valor):
        self.log.info('[InterfacesloggerConexion-ActualizaMaestro: ' + str(nombre_campo) + ', ' + str(valor))

        try:
            if '->' in nombre_campo: #Se actualiza un campo dentro de otro campo. Nprmalmente se deberá a un acceso a adjunto.
                listaCampos = nombre_campo.split('->') 
                mst = self.maestro[listaCampos[0]]
                for nombre in listaCampos[1:-1]:
                    mst = mst[nombre]
                nombre_campo= listaCampos[-1]
            else:
                mst = self.maestro

            if mst.getTipoCampo(nombre_campo) == 'l':
                tabla = valor
                pos = tabla.posActual()
                mst[nombre_campo].setValor(pos[0], tabla.nombreCol(pos[1]), tabla.valorActual())
            else:
                self.senyalMaestro.deshabilitaSenyal(self.tipo_maestro, nombre_campo)
                mst[nombre_campo] = valor
                self.senyalMaestro.habilitaSenyal(self.tipo_maestro, nombre_campo)
            
        except:
            msg = QMessageBox()
            msg.setIcon(Qt5.QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error")
            msg.setText("Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(Qt5.QtWidgets.QMessageBox.Ok)
            msg.exec_()
            
    def getCampo(self, nombre_campo):
        if '->' in nombre_campo: #Se actualiza un campo dentro de otro campo. Nprmalmente se deberá a un acceso a adjunto.
            listaCampos = nombre_campo.split('->') 
            campo = self.maestro[listaCampos[0]]
            for nombre in listaCampos[1:]:
                campo = campo[nombre]
        else:
            campo = self.maestro[nombre_campo]
        return campo

    def getTipoCampo(self, nombre_campo):
        if '->' in nombre_campo: #Se actualiza un campo dentro de otro campo. Nprmalmente se deberá a un acceso a adjunto.
            listaCampos = nombre_campo.split('->') 
            mst = self.maestro[listaCampos[0]]
            for nombre in listaCampos[1:-1]:
                mst = mst[nombre]
            nombre_campo = listaCampos[-1]
        else:
            mst = self.maestro
        return mst.getTipoCampo(nombre_campo)
                
    def almacenaMaestro(self):
        self.log.info('[InterfacesloggerConexion-AlmacenaMaestro: ' + str([str(s) for s in self.mnj.session]))        
        return self.mnj.almacena()
        
    def borraMaestro(self):        
        return self.mnj.borraMaestro(self.maestro)
    
    def cargaMaestro(self, mov):
        mst = self.maestro
        self.maestro = self.mnj.cargaMaestro(mst_ref=self.maestro, mov=mov) 
        if not self.maestro:
            self.mnj.session.add(mst)
            self.maestro = mst
        self.maestro.vaciaCamposModif()            
        return self.maestro        
        
    def buscaMaestro(self, **kwargs):
        return self.mnj.buscaMaestro(kwargs)
    
    def modificadoMaestro(self):
        return self.maestro.modificado()
        
        
'''
CLASE DE INTERFAZ DE MAESTRO
'''
class ifMaestro(QtWidgets.QWidget):
    '''
    Interfaz de Maestro. Peunte entre usuario y el tratamiento de un maestro.
    '''
    keyPressed = Qt5.QtCore.pyqtSignal(int)    
    
    def __init__(self, control_uinfs, *args, **kwargs):
        self.log = log.ini_logger(__name__)
        
        self.cuinf = control_uinfs
        # Conexión con el Manejador y Maestro Principal
        self.conMst = ifConexionMst(control_uinfs.mnjMaestro(), self.TipoMaestro, self.trataSenyal)

        # Campso de la interfaz editables por el usuario
        self.cmpEditables = {} 

        # Se llama al constructor de la SuperClase Widget
        super().__init__(*args, **kwargs)
        
        # Carga la interfaz gráfica
        uic.loadUi('Interfaz/Diseño/Articulos/'+self.Interfaz, self)
        
        # Crea un diccionario con las listas predefinidas
        self.valListas = {}
        self.mnjl = control_uinfs.mnjListasMaestros()
        for lista, caract in self.Listas.items():
            self.valListas[lista] = (self.mnjl.cargaLista(tipo=caract[0], campos_lista=caract[1]), caract[1])

        
        # Crea los enlaces de campos del Maestro con campos de Interfaz
        for campo, caract in self.Campos.items():
            self.nuevoIfCampo(campo, caract)
      
        # Atajos de teclado y comandos correspondientes
        self.shortcut_open = QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcut_open.activated.connect(lambda: self.procesaAtajo('BC'))   
        #self.keyPressed.connect(self.on_key)
        
    def keyPressEvent(self, event):
        super(ifMaestro, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())
        
    def on_key(self, key):
        '''
        Remite la tecla al ifCampo actual para que la procese
        '''
        if self.focusWidget():
            self.focusWidget().ifCampo.procesaTeclas(key)
    
    def procesaAtajo(self, comando):
        '''
        Dependiendo del comando ejecuta la operación asignada
        '''
        if (comando == 'BM'):
            self.abrirBusquedaMaestro()
        elif (comando == 'BC'):
            if self.focusWidget():
                self.abrirBusquedaCampo(self.focusWidget().ifCampo.campo)
        
    def texto(self, campo):
        if campo == None:
            return ''
        return str(campo)        

    def guardarSiCambios (self):
        if self.conMst.modificadoMaestro():
            buttonReply = QMessageBox.question(self, 'Datos Modificados', "Datos modificados. ¿Desea guardarlos?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Cancel:
                return 0
            elif buttonReply == QMessageBox.Yes:
                self.conMst.almacenaMaestro()
        return 1            
            
    def nuevoIfCampo(self, campo, caract):
        # Se cargan los ifCampos y sus desencadenadores al actualizarlos
        tipo_if = caract[0]
               
        if (tipo_if == "ifCadena"):
            cmpEditable = ifCadena(self.conMst, campo, getattr(self, caract[1]))

        elif (tipo_if == 'ifListaD'):
            cmpEditable = ifListaD(self.conMst, campo, caract[1], caract[2], caract[3])
                        
        elif (tipo_if == 'ifIdListaD'):
            cmpEditable = ifIdListaD(self.conMst, campo, caract[1], caract[2], caract[3], caract[4])

        elif (tipo_if == 'ifRefListaD'):
            cmpEditable = ifRefListaD(self.conMst, campo,  getattr(self, caract[1]),  getattr(self, caract[2]), self.valListas[caract[3]])
                                  
        elif (tipo_if == 'ifTexto'):
            cmpEditable = ifTexto(self.conMst, campo, caract[1])

        elif (tipo_if == 'ifTabla'):
            cmpEditable = ifTabla(self.conMst, campo, caract[1], caract[2], self.conMst, campo)

        elif (tipo_if == 'ifVerificacion'):
            if (len(caract) > 2):
                cmpEditable = ifVerificacion(self.conMst, campo, caract[1], caract[2])
            else:
                cmpEditable = ifVerificacion(self.conMst, campo, caract[1])
        
        # Se genera la entrada en el diccionario que contendrá los campos editables.
        #Se anidarán diccionarios en caso de que haya campos que estén den tro de campos externos o adjuntos del maestro.          
        if ('->' in campo):
            campos = campo.split('->')
            cmpant = self.cmpEditables
            for cmp in campos[:-1]:
                if not (cmp in cmpant):
                    cmpant[cmp] = {}
                cmpant = cmpant[cmp]
            cmpant[campos[-1]] = cmpEditable        
        else:
            self.cmpEditables[campo] = cmpEditable
            
        return cmpEditable 
        
    def vaciaIfCampos(self, dic=None):
        if not dic:
            dic = self.cmpEditables
        for valor in dic.values():
            if (isinstance(valor , dict)): # Recorre recursivamente el arbol/diccionario de campos editables 
                self.vaciaIfCampos(valor)
            else:
                valor.limpia()
    
    def cargaIfCampos(self):
        def cargaRIfC(fuente, dic):
            if not dic:
                dic = self.cmpEditables
            for (campo, valor) in dic.items():
                if (isinstance(valor, dict)): # Recorre recursivamente el arbol/diccionario de campos editables 
                    cargaRIfC(fuente+[campo], valor)
                else:
                    self.trataSenyal(fuente+[campo],'mv')

        self.vaciaIfCampos()
        cargaRIfC([self.conMst.tipo_maestro], self.cmpEditables)    
        
    
    '''
     Operaciones del usuario sobre el maestro
    '''
    # primeraAccion a procesar llamada por la página principal
    def primeraAccion (self):
        # Carga el primer maestro en la interfaz
        self.cargaMaestro('pri')
                
    # Fucniones de navegación sobre los maestros almacenados
    def cargaMaestro(self, mov):
        if self.guardarSiCambios():
            if self.conMst.cargaMaestro(mov):
                self.cargaIfCampos()

    def nuevo(self):
        if self.guardarSiCambios():
            self.vaciaIfCampos()        
            self.conMst.nuevoMaestro()
                
    def almacena(self):
        return self.conMst.almacenaMaestro()

    def borra(self):
        if self.conMst.borraMaestro():
            self.vaciaIfCampos()      
    
    def abrirBusquedaMaestro(self):
        # Si hay definida una busqueda para el maestro se abre
        if self.BusquedaMaestro and self.guardarSiCambios():
            ui = ifDgMstBusqueda(self.cuinf, self.TipoMaestro, self.BusquedaMaestro[0], self.BusquedaMaestro[1])
            if ui:
                ui.exec()
            campoB = ui.campoFilasSelec('id')
            if campoB:
                self.conMst.maestro.setId(int(campoB[0]))
                self.cargaMaestro('ig')    

    def abrirBusquedaCampo(self, campo):
        # Abre la busqueda de un campo y devuelve el valor buscado o nada en caso de cancelar
        externo = self.conMst.maestro.campoModifExterno(campo)
        try:
            if externo:
                busqCampo = self.mnj.nuevaConsulta(externo) # Carga la consulta de búsqueda para el campo, si existe
                if busqCampo:
                    ui = ifDgMstBusqueda(self.mnj, busqCampo)
                    if ui:
                        ui.exec()
                    campoB = ui.campoFilasSelec(campo)
                    if campoB:
                        self.vePosicion((campoB[0],))            
        except: # Como no todos los maestros tendrán búsqueda se trata el error poniendo la variable a None 
            campo = None
        return campo

    '''
     Tratamiento de las señales procedentes del maestro
    '''
    def trataSenyal(self, fuente, senyal, *args):
        self.log.info('[Interfaces] ifMaestro-TrataSenyal' + str(fuente) + ' - ' + senyal + ' - ' + str(args))
        
        try:
            if (fuente[0] == self.conMst.tipo_maestro) and (len(fuente) > 1):
                # Si el que emite la senyal es el maestro principal se busca si hay algún campo de interfaz asociado y en caso afirmativo se trata

                # Se busca el primer campo de interfaz, si lo hay, que pueda tratar la senyal. Este campo deberá tratar todos los cambios que la senyal lleve implícitos                
                ifNombreCampo = None
                iSigFuente = 1
                mstCampo = self.conMst.maestro
                listaEditables = self.cmpEditables
                while (not ifNombreCampo) and (iSigFuente < len(fuente)):
                    if (fuente[iSigFuente] in listaEditables): 
                        if not isinstance(listaEditables[fuente[iSigFuente]], dict):
                            ifNombreCampo = fuente[iSigFuente]
                        else:
                            listaEditables = listaEditables[fuente[iSigFuente]]
                    tipoCampo = mstCampo.getTipoCampo(fuente[iSigFuente])
                    mstCampo = mstCampo[fuente[iSigFuente]]
                    iSigFuente += 1
                        
                if ifNombreCampo:
                    ifCampo = listaEditables[ifNombreCampo]
                    if (tipoCampo == 'l'):
                        if (iSigFuente == len(fuente)):
                            ifCampo.limpia()
                            for i in range(mstCampo.numeroFilas()):
                                valores = mstCampo.getValoresCamposFila(i)
                                ifCampo.agregaFila(valores)
                        else:
                            (campo, fila) = fuente[iSigFuente]
                            if (senyal == 'mv') and (campo in listaEditables[ifNombreCampo].campos): # Se ha modificado un valor concreto
                                ifCampo.setValor(fila, campo, mstCampo.getValor(fila, campo))
                            elif (senyal == 'nf'): # Se inserta una fila
                                ifCampo.qtw.insertRow(fila)
                            elif (senyal == 'bf'): # Se borra una fila
                                ifCampo.qtw.removeRow(fila)
                    else:
                        ifCampo.setValor(mstCampo)
                        
        except:
            msg = Qt5.QtWidgets.QMessageBox()
            msg.setIcon(Qt5.QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error. Interfaces->ifMaestro->trataSenyal")
            msg.setText("Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(Qt5.QtWidgets.QMessageBox.Ok)
            msg.exec_()
                        

    '''
    FUNCIONES DE LOG. PARA LA VERIFICACIÓN DEL CÓDIGO DURANTE LA PROGRAMACIÓN
    '''
                                 
    def logImpMaestro(self):
        print(self.conMst.maestro)
        
                        