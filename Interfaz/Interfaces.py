'''
Created on 4 mar. 2019

@author: cortesj
'''
import sys

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMessageBox, QShortcut, QCompleter

from Señales import TunelSenyal

import log
logger = log.get_logger(__name__)

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
class ifCampo(object):
    # Clase madre de los campos de interfaz que se relacionan con un campo de maestro
    def __init__(self, if_campo, mst_campo):
        self.bloqueado = False
        self.ifc = if_campo
        self.mstc = mst_campo

    
class ifCadena(ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, qt_line_edit, conMst, campo):
        super().__init__(qt_line_edit, campo)
        self.ifc.__dict__['ifCampo'] = self # Los campos qt apuntarán al campo de interfaz que los engloba para poder procesar eventos como los del teclado
        self.ifc.editingFinished.connect(lambda: conMst.actualizaMaestro(campo, self))
        self.fGetValor = lambda: self.ifc.text()
    def getValor(self):
        return self.fGetValor()
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.ifc.setText(str(valor))
            else:
                self.ifc.clear()
        
    def limpia(self):
        self.ifc.clear()
        
    def procesaTeclas(self, key):
        if key == QtCore.Qt.Key_Return:
            print('return key pressed')
        else:
            print('key pressed: %s' % key)

class ifCadenaExt(ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena asociada a un campo de tipo Externo
    '''
    def __init__(self, qt_line_edit, lista_mst, campo_lista, conMst, campo):
        super().__init__(qt_line_edit, campo)
        self.lista = lista_mst
        self.campoExt = campo_lista
        
        self.lRef = [str(l[self.campoExt]) for l in self.lista]
        qCompleter = QCompleter(self.lRef)
        self.ifc.setCompleter(qCompleter)

        self.ifc.__dict__['ifCampo'] = self # Los campos qt apuntarán al campo de interfaz que los engloba para poder procesar eventos como los del teclado
        self.ifc.editingFinished.connect(lambda: conMst.actualizaMaestro(campo, self))
        
    def getValor(self):
        valor = self.ifc.text()
        if valor in self.lRef:
            return self.lista[self.lRef.index(valor)]
        else:
            return None
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.ifc.setText(str(valor[self.campoExt]))
            else:
                self.ifc.clear()
        
    def limpia(self):
        self.ifc.clear()
        
    def procesaTeclas(self, key):
        if key == QtCore.Qt.Key_Return:
            print('return key pressed')
        else:
            print('key pressed: %s' % key)
            
class ifTexto(ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, qt_ptext_edit, conMst, campo):
        super().__init__(qt_ptext_edit, campo)        

        self.ifc.textChanged.connect(lambda: conMst.actualizaMaestro(campo, self))

    def getValor(self):
        return self.ifc.toPlainText()
    
    def setValor(self, valor):
        if valor != self.getValor():
            if (valor) or (valor == ""):
                self.ifc.appendPlainText(valor)
            else:
                self.limpia()
        
    def limpia(self):
        self.ifc.blockSignals(True)        
        self.ifc.clear()
        self.ifc.blockSignals(False)        
    
    
class ifVerificacion(object):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, qt_checkbox, qts_habilitados, conMst, campo):
        super().__init__(qt_checkbox, campo)
        self.qtsHabil = qts_habilitados
        self.ifc.stateChanged.connect(lambda: self.actualizaValidador(conMst, campo))

    def getValor(self):
        return self.chb.isChecked()
    
    def setValor(self, valor):
        if valor != self.getValor():
            self.ifc.blockSignals(True)        
            self.ifc.setChecked(valor)
            self.validaCampos()
            self.ifc.blockSignals(False)        
        
    def limpia(self):
        self.chb.blockSignals(True)        
        self.chb.setChecked(False)
        self.chb.blockSignals(False)              

    def actualizaValidador(self, conMst, campo):
        conMst.actualizaMaestro(campo, self)
        self.validaCampos()
        
    def validaCampos(self):
        if self.qtsHabil:
            for elem in self.qtsHabil:
                elem.setEnabled(self.getValor())
    
class ifListaD(object):
    '''
    Objetos de interfaz que muestran una lista desplegable para seleccionar un elemento e internamente su índice
    '''
    def __init__(self, qtComboBox, lista_mst, conMst, campo):
        self.qcb = qtComboBox
        self.qcb.clear()
        self.qcb.addItems(['']+lista_mst[1])
        self.lid = ['']+lista_mst[0]
        self.qcb.currentIndexChanged.connect(lambda: conMst.actualizaMaestro(campo, self.getValor())) 

    def getValor(self):
        if self.qcb.currentIndex():
            return int(self.lid[self.qcb.currentIndex()])
        else:
            return None
                
    def setValor(self, valor):
        if valor != self.getValor():
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
            
class ifListaExt(ifCampo):
    '''
    Objetos de interfaz que muestran un indice y su correspondencia en una lista desplegable
    '''
    def __init__(self, qt_combo_box, lista_mst, campo_lista, conMst, campo):
        super().__init__(qt_combo_box, campo)        
        self.ifc.clear()
        
        self.lista = lista_mst
                        
        self.ifc.addItems(['']+self.lista.col(campo_lista))
        
        self.ifc.currentIndexChanged.connect(lambda: conMst.actualizaMaestro(campo, self)) 
                        
    def getValor(self):
        ci = self.ifc.currentIndex()
        if ci:
            return self.lista[ci-1]
        else:
            return None
            
    def setValor(self, valor):
        if valor != self.getValor():
            self.ifc.blockSignals(True)
            if valor:
                self.ifc.setCurrentIndex(self.lista.index(valor)+1)
            else:
                self.limpia()
            self.ifc.blockSignals(False)
     
    def limpia(self):
        self.ifc.blockSignals(True)
        self.ifc.setCurrentIndex(0)
        self.ifc.blockSignals(False)
        
            
class ifRefListaD(object):
    '''
    Objetos de interfaz que muestran una referencia alfanumérica y su correspondencia en una lista desplegable
    '''
    def __init__(self, qtLineEdit, qtComboBox, lista_mst, conMst, campo):
        self.qle = qtLineEdit
        #self.qle.textEdited.connect(self.__cambioLE)
        self.qle.textChanged.connect(self.__cambioLE)

        self.campos = lista_mst[1]
        self.lista = lista_mst[0]
        self.lRef = [str(l[self.campos[0]]) for l in self.lista]

        qCompleter = QCompleter(self.lRef)
        self.qle.setCompleter(qCompleter)

        self.qcb = qtComboBox
        self.qcb.clear()
        self.qcb.addItems(['']+self.lista.col(self.campos[1]))
        
        self.qcb.currentIndexChanged.connect(self.__cambioCB)
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
        if valor != self.getValor():        
            self.qcb.blockSignals(True)
            if valor:
                listind = self.lista.index(valor)
                self.qcb.setCurrentIndex(listind+1)
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
                    idl = self.lRef.index(dato) + 1
                    self.qcb.setCurrentIndex(idl)
            except ValueError:
                self.qle.blockSignals(True)
                msg = QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("Mensaje Error")
                msg.setText("[Interfaces-IfMaestro] Valor [ " + str(dato) + " ] erróneo")
                msg.setInformativeText("El dato introducido ha de ser un entero")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()
                self.qle.clear()
                self.qle.blockSignals(False)
                
        else:
            self.qcb.setCurrentIndex(0)
            
        
    def __cambioCB(self, i):
        if not i:
            self.qle.clear()
        else:
            self.qle.setText(str(self.lRef[i-1]))
                
        
class ifTabla(object):
    '''
    Objetos de interfaz para el manejo de tablas
    '''
    def __init__(self, qtTableWidget, dict_cols, conMst, campo):
        self.ifc = qtTableWidget
        self.campos = list(dict_cols.keys())

        # Los objetos complejos tienen que tener acceso al maestro ya que tienen señales internas de modificación
        self.conMst = conMst
        self.mstCampo = campo
        # Se crean las columnas de la tabla según la lista paada
        self.ifc.setColumnCount(len(self.campos))
        i = 0
        for s in self.campos:
            self.ifc.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(dict_cols[s]))
            i+=1

        # Se acopla el menú contextual genérico de las tablas
        self.ifc.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ifc.customContextMenuRequested.connect(lambda pos: self.menuIfTabla(pos))       
        # Asigna los tratamientos especiales para teclas de control de movimiento
        #Qt5.QtWidgets.QShortcut(Qt5.QtCore.Qt.Key_Tab, self.cmpEditables[campo].qtw, activated=lambda: self.trataTab(campo))
                
        # porc_col = .98/len(self.campos)
        #self.ifc.setColumnWidth(i,self.ifc.width()*porc_col)
        #self.ifc.setSizeAdjustPolicy(Qt5.QtWidgets.QAbstractScrollArea.AdjustToContents)
        #self.ifc.resizeColumnsToContents()
        cabecera = self.ifc.horizontalHeader() 
        for i in range(self.ifc.columnCount()-1):
            cabecera.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        i += 1
        cabecera.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        
        self.ifc.itemChanged.connect(lambda: conMst.actualizaMaestro(campo, self))
        
    def menuIfTabla(self, posicion):
        menu = QtWidgets.QMenu()
        insertAction = menu.addAction("Inserta Fila")
        borraAction = menu.addAction("Borra Fila")
        agregAction = menu.addAction("Agrega Fila")
        action = menu.exec_(self.ifc.mapToGlobal(posicion))
        #self.senyalMaestro.deshabilitaSenyal(self.tipo_maestro, campo)
        if action == insertAction:
            if self.ifc.currentRow() < 0:
                self.conMst.maestro.nuevaLinea(self.mstCampo)                
            else:
                self.conMst.maestro.nuevaLinea(self.mstCampo, self.ifc.currentRow())                
        elif action == borraAction:
            if (self.ifc.currentRow() >= 0):
                self.conMst.maestro.borraLinea(self.mstCampo, self.ifc.currentRow())
        elif action == agregAction:
            self.conMst.maestro.nuevaLinea(self.mstCampo)

    def trataTab(self, campo):
        #event = Qt5.QtGui.QKeyEvent(Qt5.QtCore.QEvent.KeyPress, Qt5.QtCore.Qt.Key_Tab, Qt5.QtCore.Qt.NoModifier)
        #Qt5.QtCore.QCoreApplication.postEvent(self, event)
        qtw = self.ifc
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
        self.ifc.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(args[0]))
        
    def nombreCol(self, pos):
        return self.campos[pos]
            
    def getValor(self, lin, col):
        return self.ifc.cellWidget(lin, self.campos.index(col))
    
    def setValor(self, lin, col, valor):
        if isinstance(col, str):
            coln = self.campos.index(col)
        else:
            coln = col
            
        self.ifc.blockSignals(True)
        if isinstance(valor, bool):
            chkBox = QtWidgets.QCheckBox(parent=self.ifc)
            chkBox.setChecked(valor)
            chkBox.stateChanged.connect(self.trataPulsaBoton)
            self.ifc.setCellWidget(lin, coln, chkBox)          
        else:
            logger.warning('Alerta!, alerta!')     
            '''    
            if valor:
                self.ifc.setItem(lin, coln, QtWidgets.QTableWidgetItem(str(valor)))
            else:
                self.ifc.setItem(lin, coln, QtWidgets.QTableWidgetItem(''))
            '''
            q = QtWidgets.QLineEdit(parent=self.ifc)
            q.setStyleSheet("border: 0px;")
            q.setText('a')
            self.ifc.setCellWidget(lin, coln, q)
            
        self.ifc.blockSignals(False)
    
    def trataPulsaBoton(self):
        ch = self.ifc.sender()
        print(ch.parent())
        ix = self.ifc.indexAt(ch.pos())
        self.conMst.maestro[self.mstCampo][ix.row()][self.nombreCol(ix.column())] = ch.isChecked()
        
    def agregaFila(self, valores, n_fila=None):
        if n_fila == None:
            n_fila = self.ifc.rowCount()
        self.ifc.insertRow(n_fila)
        if valores:
            i = 0
            for campo in self.campos:
                self.setValor(n_fila, i, valores[campo])
                i += 1
        self.ifc.setCurrentCell(n_fila, 0)
        
    def posActual(self):
        return (self.ifc.currentRow(), self.ifc.currentColumn())
    
    def valorActual(self):
        pos = self.posActual()
        if type(self.ifc.cellWidget(pos[0], pos[1])) == QtWidgets.QCheckBox:
            return self.ifc.cellWidget(pos[0], pos[1]).isChecked()
            #return (self.ifc.item(pos[0],pos[1]).checkState() == 2)
        else:
            return self.ifc.item(pos[0],pos[1]).text()
    
    def limpia(self):
        for i in range(self.ifc.rowCount()-1,-1, -1):
            self.ifc.removeRow(i)


class ifConexionMst(object):
    def __init__(self, manejador, tipo_maestro, funcion_enlace):
        # La funcion_enlace asigna la función para que el Maestro haga modificaciones en la interfaz
        self.mnj = manejador
        self.tipo_maestro = tipo_maestro # Idenficará el tipo de maestro cuyos registros va a editar la interfaz
        self.maestro = self.mnj.nuevoMaestro(self.tipo_maestro) # Por defecto carga un maestro en blanco
         
        # Genera la clase de tunel de sñales para la propagación en la interfaz de los cambios en el maestro principal
        self.senyalMaestro = TunelSenyal('if'+tipo_maestro.capitalize())
        self.senyalMaestro.asignaTunel(funcion_enlace)
        # Habilita el tunel entre el Maestro y la Interfaz del maestro
        self.maestro.asignaTunelSenyal(self.senyalMaestro)
        self.senyalMaestro.habilitaTunel()

    def actualizaMaestro(self, nombre_campo, ifc):
        logger.info('ifConexionMst.actualizaMaestro: ' + str(nombre_campo) + ', ' + str(ifc))

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
                tabla = ifc
                pos = tabla.posActual()
                mst[nombre_campo][pos[0]][tabla.nombreCol(pos[1])] = tabla.valorActual()
            else:
                #self.senyalMaestro.deshabilitaSenyal('1', nombre_campo)
                mst[nombre_campo] = ifc.getValor()
            
        except:
            msg = QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error")
            msg.setText("Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
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
                
    def nuevoMaestro(self):
        self.mnj.descarta(self.maestro)        
        self.maestro = self.mnj.nuevoMaestro(self.tipo_maestro, etiqueta=self.tipo_maestro)
        # Habilita el tunel entre el Maestro y la Interfaz del maestro
        self.maestro.asignaTunelSenyal(self.senyalMaestro)
        self.senyalMaestro.habilitaTunel()
                        
    def almacenaMaestro(self):
        logger.info('ifConexionMst.almacenaMaestro: ' + str([str(s) for s in self.mnj.session]))        
        return self.mnj.almacena()
        
    def borraMaestro(self):        
        return self.mnj.borraMaestro(self.maestro)
    
    def cargaMaestro(self, mov):
        mst = self.mnj.cargaMaestro(mst_ref=self.maestro, mov=mov) 
        if mst and mst != self.maestro:
            self.mnj.descarta(self.maestro)
            self.maestro = mst
            self.maestro.vaciaCamposModif()
        # Habilita el tunel entre el Maestro y la Interfaz del maestro
        self.maestro.asignaTunelSenyal(self.senyalMaestro)
        self.senyalMaestro.habilitaTunel()
        return mst        
        
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
    TipoMaestro = ''
    Interfaz = ''
    ListasMst = {}
    Campos = {}
    BusquedaMaestro = ()
    keyPressed = QtCore.pyqtSignal(int)    
    
    def __init__(self, control_uinfs, *args, **kwargs):
        self.cuinf = control_uinfs
        mnj = control_uinfs.mnjMaestros()

        # Crea un diccionario con las listas predefinidas
        self.valListas = {}
        for lista, caract in self.ListasMst.items():
            self.valListas[lista] = mnj.cargaLista(
                                        tipo=caract[0], campos_lista=caract[1], orden=caract[1][0]
                                        )                                    

        # Conexión con el Manejador y Maestro Principal
        self.conMst = ifConexionMst(mnj, self.TipoMaestro, self.trataSenyal)

        # Crea un diccionario con los enlaces de campos del Maestro con campos de Interfaz
        self.cmpEditables = {} 
        
        # Se llama al constructor de la SuperClase Widget
        super().__init__(*args, **kwargs)
        
        # Carga la interfaz gráfica
        uic.loadUi('Interfaz/Diseño/'+self.Interfaz+'.ui', self)
        

        for campoIf, campoConf in self.Campos.items():
            campoMst = campoConf[-1]
            ifCampo = self.nuevoIfCampo(campoIf, campoConf)
            if not campoMst in self.cmpEditables:
                self.cmpEditables[campoMst] = [ifCampo]
            else:
                self.cmpEditables[campoMst].append(ifCampo)
                
      
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

    def nuevoIfCampo(self, campo, caract):
        # Se cargan los ifCampos y sus desencadenadores al actualizarlos
        tipoIf= caract[0]
        campoMst = caract[-1]
               
        if (tipoIf == "ifCadena"):
            cmpEditable = ifCadena(getattr(self, campo), self.conMst, campoMst)

        elif (tipoIf == 'ifCadenaExt'):
            cmpEditable = ifCadenaExt(getattr(self, campo), self.valListas[caract[1]], caract[2], self.conMst, campoMst)
            
        elif (tipoIf == 'ifListaD'):
            cmpEditable = ifListaD(getattr(self, campo), self.valListas[caract[1]], self.conMst, campoMst)
                        
        elif (tipoIf == 'ifListaExt'):
            cmpEditable = ifListaExt(getattr(self, campo), self.valListas[caract[1]], caract[2], self.conMst, campoMst)

        elif (tipoIf == 'ifRefListaD'):
            cmpEditable = ifListaExt(getattr(self, campo), self.valListas[caract[1]], caract[2], self.conMst, campoMst)
                                  
        elif (tipoIf == 'ifTexto'):
            cmpEditable = ifTexto(getattr(self, campo), self.conMst, campoMst)

        elif (tipoIf == 'ifTabla'):
            cmpEditable = ifTabla(getattr(self, campo), caract[1], self.conMst, campoMst)

        elif (tipoIf == 'ifVerificacion'):
            cmpEditable = ifVerificacion(getattr(self, campo), [getattr(self, cmp) for cmp in caract[1]], self.conMst, campoMst)
        
        return cmpEditable 
        
    def vaciaIfCampos(self, dic=None):
        if not dic:
            dic = self.cmpEditables
        for lifC in dic.values():
            for ifC in lifC:
                if (isinstance(ifC, dict)): # Recorre recursivamente el arbol/diccionario de campos editables 
                    self.vaciaIfCampos(ifC)
                else:
                    ifC.limpia()
    
    def cargaIfCampos(self):
        def cargaRIfC(fuente, dic):
            if not dic:
                dic = self.cmpEditables
            for (campo, valor) in dic.items():
                if (isinstance(valor, dict)): # Recorre recursivamente el arbol/diccionario de campos editables 
                    cargaRIfC(fuente+[campo], valor)
                else:
                    self.trataSenyal(fuente+[campo],'mv', self.conMst.maestro[campo])

        self.vaciaIfCampos()
        cargaRIfC([self.conMst.tipo_maestro], self.cmpEditables)    
        
    def guardarSiCambios (self):
        if self.conMst.modificadoMaestro():
            buttonReply = QMessageBox.question(self, 'Datos Modificados', "Datos modificados. ¿Desea guardarlos?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Cancel:
                return 0
            elif buttonReply == QMessageBox.Yes:
                self.conMst.almacenaMaestro()
        return 1            
    
    '''
     Operaciones del usuario sobre el maestro
    '''
    # primeraAccion a procesar llamada por la página principal
    def primeraAccion (self):
        # Carga el primer maestro en la interfaz
        if not self.cargaMaestro('pri'):
            self.conMst.nuevoMaestro()
                
    # Fucniones de navegación sobre los maestros almacenados
    def cargaMaestro(self, mov):
        if self.guardarSiCambios():
            if self.conMst.cargaMaestro(mov):
                self.cargaIfCampos()
                return True
            else:
                return False

    def nuevo(self):
        if self.guardarSiCambios():
            self.vaciaIfCampos()        
            self.conMst.nuevoMaestro()
                
    def almacena(self):
        return self.conMst.almacenaMaestro()

    def borra(self):
        buttonReply = QMessageBox.question(self, 'Eliminación', "¿Desea eliminar el registro actual?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
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
                busqCampo = self.nuevaConsulta(externo) # Carga la consulta de búsqueda para el campo, si existe
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
        # Tratará las señales procedentes del maestro principal
        logger.info('ifMaestro.trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))
        
        try:
            # Se busca el primer campo de interfaz, si lo hay, que pueda tratar la senyal. Este campo deberá tratar todos los cambios que la senyal lleve implícitos                
            iSigFuente = 0
            valor = args[0]
            ifCampos = self.cmpEditables
            for nomCampo in fuente[1:]:
                ifCampos = ifCampos[nomCampo]
                iSigFuente += 1
            tipoCampo = self.conMst.maestro.getTipoCampo(fuente[iSigFuente])
                                            
            for ifCampo in ifCampos:
                logger.info('ifMaestro.trataSenyal  - Campo: ' + str(ifCampo.ifc.objectName()))
                if (tipoCampo == 'l'):
                    logger.warning(iSigFuente)
                    logger.warning(fuente)
                    logger.warning(valor)
                    if (iSigFuente+1 == len(fuente)):
                        ifCampo.limpia()
                        for fila in valor:
                            ifCampo.agregaFila(fila)

                    else:
                        
                        (fila, campo) = fuente[iSigFuente]
                        if (senyal == 'mv'): # Se ha modificado un valor concreto
                            ifCampo.setValor(fila, campo, valor.getValor(fila, campo))
                        elif (senyal == 'nf'): # Se inserta una fila
                            if args:
                                ifCampo.agregaFila(valor[fila], args[0])
                            else:
                                ifCampo.agregaFila(valor[fila])
                        elif (senyal == 'bf'): # Se borra una fila
                            ifCampo.qtw.removeRow(fila)

                else:
                    ifCampo.setValor(valor)
                    
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Mensaje Error. Interfaces->ifMaestro->trataSenyal")
            msg.setText("Error inesperado: " + str(sys.exc_info()[0]))
            msg.setInformativeText(str(sys.exc_info()[1]))
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
                        

    '''
    FUNCIONES DE LOG PARA LA VERIFICACIÓN DEL CÓDIGO DURANTE LA PROGRAMACIÓN
    '''
                                 
    def logImp(self):
        print('============================')
        print('- '+str(self.conMst.mnj.session))
        for s in self.conMst.mnj.session:
            print (s)
        print('============================')
        print(self.conMst.maestro._camposModif)
        print(self.conMst.mnj.session.is_modified(self.conMst.maestro))

    