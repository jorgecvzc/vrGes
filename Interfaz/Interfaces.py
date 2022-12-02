'''
Created on 4 mar. 2019

@author: cortesj
'''
import sys

from sqlalchemy.orm import object_session
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMessageBox, QShortcut, QCompleter

from Señales import TunelSenyal

import log
from PyQt5.Qt import QTableWidget, QLineEdit
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
        
    def trataSenyal(self, fuente, senyal, *args):
        # Tratará las señales procedentes del maestro principal
        logger.info('ifCampo['+self.mstc+'].trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))
        
        # Se pasa la señal al siguiente campo si está representado en la interfaz
        if (len(fuente) == 1):
            self.setValor(args[0])
        else:
            self[fuente[1]].trataSenyal(fuente[1:], senyal, args)        

    
class ifCadena(ifCampo):
        
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, campo_qt, conMst, campo):
        if not isinstance(campo_qt, QtWidgets.QLineEdit):
            campo_qt = QtWidgets.QLineEdit(parent=campo_qt)
        super().__init__(campo_qt, campo)
        self.ifc.__dict__['ifCampo'] = self # Los campos qt apuntarán al campo de interfaz que los engloba para poder procesar eventos como los del teclado
        
        #self.mnj.session.merge(self.valListas['lVariantesArt'][0])  
        self.ifc.editingFinished.connect(lambda: conMst().__setitem__(self.mstc, self.getValor())) 
        self.fGetValor = lambda: self.ifc.text()
    
    def getValor(self):
        return self.ifc.text()
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.ifc.setText(str(valor))
            else:
                self.ifc.clear()
        
    def limpia(self):
        self.ifc.clear()
        
    def procesaTeclas(self, key):
        #self.ifc.returnPressed.connect(self.procesaTeclas)
        if key == QtCore.Qt.Key_Return:
            print('return key pressed')
        else:
            print('key pressed: %s' % key)

class ifRefExt(ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena asociada a un campo de tipo Externo
    '''
    def __init__(self, campo_qt, lista_mst, campo_lista, con_mst, campo):
        if not isinstance(campo_qt, QtWidgets.QLineEdit):
            campo_qt = QtWidgets.QLineEdit(campo_qt)
        super().__init__(campo_qt, campo)
        self.lista = lista_mst
        self.campoMst = campo_lista
        
        self.lRef = [str(l[self.campoMst]) for l in self.lista]
        qCompleter = QCompleter(self.lRef)
        self.ifc.setCompleter(qCompleter)

        # self.ifc.__dict__['ifCampo'] = self # Los campos qt apuntarán al campo de interfaz que los engloba para poder procesar eventos como los del teclado
        self.conMst = con_mst        
        self.ifc.editingFinished.connect(lambda: self.actualizaMaestro())
      
    def actualizaMaestro(self):
        self.conMst().__setitem__(self.mstc, self.getValor())        

    def getValor(self):
        valor = self.ifc.text()
        if valor in self.lRef:
            ext = self.lista[self.lRef.index(valor)]
            return object_session(self.conMst()).merge(ext)
        else:
            return None
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.ifc.setText(str(valor[self.campoMst]))
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

        self.ifc.textChanged.connect(lambda: conMst().__setitem__(campo, self.getValor()))

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
    
    
class ifVerificacion(ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, qt_checkbox, qts_habilitados, conMst, campo):
        super().__init__(qt_checkbox, campo)
        self.qtsHabil = qts_habilitados
        self.ifc.stateChanged.connect(lambda: self.actualizaValidador(conMst(), campo))

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
        conMst()[campo] = self.getValor()
        self.validaCampos()
        
    def validaCampos(self):
        if self.qtsHabil:
            for elem in self.qtsHabil:
                elem.setEnabled(self.getValor())
    
class ifListaD(ifCampo):
    '''
    Objetos de interfaz que muestran una lista desplegable para seleccionar un elemento e internamente su índice
    '''
    def __init__(self, qtComboBox, lista_mst, conMst, campo):
        self.qcb = qtComboBox
        self.qcb.clear()
        self.qcb.addItems(['']+lista_mst[1])
        self.lid = ['']+lista_mst[0]
        self.qcb.currentIndexChanged.connect(lambda: conMst().__setitem__(campo, self.getValor())) 

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
    def __init__(self, qt_combo_box, lista_mst, campo_lista, con_mst, campo):
        super().__init__(qt_combo_box, campo)      
        self.ifc.clear()
        
        self.lista = lista_mst
                        
        self.campoLista = campo_lista
        self.ifc.addItems(['']+self.lista.col(campo_lista))
        
        self.conMst = con_mst
        self.ifc.currentIndexChanged.connect(lambda: self.actualizaMaestro()) 

    def actualizaMaestro(self):
        valor = object_session(self.conMst()).merge(self.getValor())
        self.conMst().__setitem__(self.mstc, valor)
                                
    def getValor(self):
        ci = self.ifc.currentIndex()
        if ci:
            return object_session(self.conMst()).merge(self.lista[ci-1])
        else:
            return None
            
    def setValor(self, valor):
        if valor != self.getValor():
            self.ifc.blockSignals(True)
            if valor:
                self.ifc.setCurrentText(valor[self.campoLista])
            else:
                self.limpia()
            self.ifc.blockSignals(False)
     
    def limpia(self):
        self.ifc.blockSignals(True)
        self.ifc.setCurrentIndex(0)
        self.ifc.blockSignals(False)
        

        
class ifLineaTabla(object):
    def __init__(self, mst):
        self.maestro = mst
        
    def conMst(self):
        return self.maestro
    
    
class ifTabla(ifCampo):
    '''
    Objetos de interfaz para el manejo de tablas
    '''
    def __init__(self, qtTableWidget, dict_cols, conMst, campo):
        self.ifc = qtTableWidget
        self.confCampos = dict_cols
        self.conMstPadre = conMst

        # Los objetos complejos tienen que tener acceso al maestro ya que tienen señales internas de modificación
        self.mstCampo = campo
        # Se crean las columnas de la tabla según la lista paada
        self.ifc.setColumnCount(len(self.confCampos))
        i = 0
        for s in self.confCampos.keys():
            self.ifc.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(s))
            i+=1

        # Se acopla el menú contextual genérico de las tablas
        self.ifc.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ifc.customContextMenuRequested.connect(lambda pos: self.menuIfTabla(pos))       
        # Asigna los tratamientos especiales para teclas de control de movimiento
        # QtWidgets.QShortcut(QtCore.Qt.Key_Tab, self.ifc, activated=lambda: self.trataTab(campo))
                
        # porc_col = .98/len(self.campos)
        #self.ifc.setColumnWidth(i,self.ifc.width()*porc_col)
        #self.ifc.setSizeAdjustPolicy(Qt5.QtWidgets.QAbstractScrollArea.AdjustToContents)
        #self.ifc.resizeColumnsToContents()
        cabecera = self.ifc.horizontalHeader() 
        for i in range(self.ifc.columnCount()-1):
            cabecera.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        i += 1
        cabecera.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        
        self.ifc.itemChanged.connect(lambda: conMst().__setitem__(campo, self.getValor()))
        
        
    def menuIfTabla(self, posicion):
        menu = QtWidgets.QMenu()
        insertAction = menu.addAction("Inserta Fila")
        borraAction = menu.addAction("Borra Fila")
        agregAction = menu.addAction("Agrega Fila")
        action = menu.exec_(self.ifc.mapToGlobal(posicion))
        #self.senyalMaestro.deshabilitaSenyal(self.tipo_maestro, campo)
        if action == insertAction:
            if self.ifc.currentRow() < 0:
                self.conMstPadre().nuevaLinea(self.mstCampo)                
            else:
                self.conMstPadre().nuevaLinea(self.mstCampo, self.ifc.currentRow())                
        elif action == borraAction:
            if (self.ifc.currentRow() >= 0):
                self.conMstPadre().borraLinea(self.mstCampo, self.ifc.currentRow())
        elif action == agregAction:
            self.conMstPadre().nuevaLinea(self.mstCampo)

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
        ix = self.ifc.indexAt(ch.pos())
        self.conMst.maestro[self.mstCampo][ix.row()][self.nombreCol(ix.column())] = ch.isChecked()
    
    def conMst(self):
        return self.conMstPadre()[self.mstCampo][self.ifc.currentRow()]
        
    def agregaFila(self, valores, n_fila=None):
        # Se cargan los ifCampos y sus desencadenadores al actualizarlos
        if n_fila == None:
            n_fila = self.ifc.rowCount()        
        self.ifc.insertRow(n_fila)
        i = 0
        for confCampo in self.confCampos.values():
            # Se cargan los ifCampos y sus desencadenadores al actualizarlos
            qtCamp = None
            tipoIf= confCampo[0]
            campoMst= confCampo[-1]

            cmpEditable = nuevoIfCampo(self, tipoIf, self.conMst, campoMst, campo_qt=qtCamp, param=confCampo[1:-1])
            cmpEditable.setValor(valores[campoMst])
            self.ifc.setCellWidget(n_fila, i, cmpEditable.ifc)
            self.ifc.setStyleSheet("border : 0px;")
            i += 1               

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

    def trataSenyal(self, fuente, senyal, *args):
        # Tratará las señales procedentes del maestro principal
        logger.info('ifMaestro.trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))

        # Se pasa la señal a todos los ifCampos unidos al campo maestro si los hay
        if (len(fuente)-1):
            nFila = fuente[1]
            if senyal == 'nf':
                self.agregaFila(self.conMstPadre()[self.mstCampo][nFila], nFila)
            elif (len(fuente)-2):
                if (senyal == 'mv'): # Se ha modificado un valor concreto
                    self.setValor(nFila, fuente[2], args[0])                

        elif senyal == 'mv':
            self.limpia()
            for l in args[0]:
                self.agregaFila(l, l.orden)
                

def nuevoIfCampo(if_widget, tipoIf, conMst, campoMst, **kwargs):
    # Se cargan los ifCampos y sus desencadenadores al actualizarlos
    # Parámetros kwargs
    #  - campo_qt: Campo qt asociado al ifCampo. Si no existe se crea uno nuevo
    #  - param: Parámetros extra para la creación de cada ifCampo
    
    qtCmp = kwargs.pop('campo_qt', None)
    if qtCmp == None:
        qtCmp = if_widget.ifc
       
    param = kwargs.pop('param', [])
           
    if (tipoIf == "ifCadena"):
        ifCampo = ifCadena(qtCmp, conMst, campoMst)

    elif (tipoIf == 'ifTexto'):
        ifCampo = ifTexto(qtCmp, conMst, campoMst)
        
    elif (tipoIf == 'ifRefExt'):
        ifCampo = ifRefExt(qtCmp, if_widget.valListas[param[0]], param[1], conMst, campoMst)
        
    elif (tipoIf == 'ifListaD'):
        ifCampo = ifListaD(qtCmp, if_widget.valListas[param[0]], conMst, campoMst)
                    
    elif (tipoIf == 'ifListaExt'):
        ifCampo = ifListaExt(qtCmp, if_widget.valListas[param[0]], param[1], conMst, campoMst)

    elif (tipoIf == 'ifRefListaD'):
        ifCampo = ifListaExt(qtCmp, if_widget.valListas[param[0]], param[1], conMst, campoMst)
                              
    elif (tipoIf == 'ifVerificacion'):
        ifCampo = ifVerificacion(qtCmp, [getattr(self, cmp) for cmp in param[0]], conMst, campoMst)
    
    elif (tipoIf == 'ifTabla'):
        ifCampo = ifTabla(qtCmp, param[0], conMst, campoMst)            
        
    return ifCampo 
   
     
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
        # Inicializa ControlUinf, Manejador, Tunel de Señales y Maestro
        self.cuinf = control_uinfs
        self.mnj = control_uinfs.mnjMaestros()
        self.mnjListas = control_uinfs.mnjMaestros()
        self.senyalMaestro = TunelSenyal('if'+self.TipoMaestro.capitalize())
        self.senyalMaestro.asignaTunel(self.trataSenyal)
        self.maestro = None
        
        # Crea un diccionario con los enlaces de campos del Maestro con campos de Interfaz
        self.cmpEditables = {} 
        
        # Crea un diccionario con las listas predefinidas
        self.valListas = {}
        for lista, caract in self.ListasMst.items():
            self.valListas[lista] = self.mnjListas.cargaLista(
                                        tipo=caract[0], campos_lista=caract[1], orden=caract[1][0]
                                        )                                    

        # Se llama al constructor de la SuperClase Widget
        super().__init__(*args, **kwargs)
        
        # Carga la interfaz gráfica
        uic.loadUi('Interfaz/Diseño/'+self.Interfaz+'.ui', self)
        self.leNombre

        # Se crean los campos de interfaz
        for campoIf, campoConf in self.Campos.items():
            campoMst = campoConf[-1]
            ifCampo = self.agregaIfCampo(campoIf, campoConf)
            if not campoMst in self.cmpEditables:
                self.cmpEditables[campoMst] = [ifCampo]
            else:
                self.cmpEditables[campoMst].append(ifCampo)

        # AAsigna atajos de teclado y comandos correspondientes
        self.shortcut_open = QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcut_open.activated.connect(lambda: self.procesaAtajo('BC')) 
        self.keyPressed.connect(self.on_key)
        
        self.nuevo()
               
    def keyPressEvent(self, event):
        super(ifMaestro, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())
        
    def on_key(self, key):
        '''
        Remite la tecla al ifCampo actual para que la procese
        '''
        if self.focusWidget():
            pfw = self.focusWidget().parent().parent()
            print(pfw)
            if isinstance(pfw, QTableWidget):
                if (pfw.currentRow() == pfw.rowCount()-1):
                    if (pfw.currentColumn() == pfw.columnCount()-1):
                        pfw.insertRow(pfw.rowCount())
            self.focusNextPrevChild(True)
            #self.focusWidget().ifCampo.procesaTeclas(key)
    
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
    
    def conMst(self):
        return self.maestro
    
    def agregaIfCampo(self, campo, param):
        # Se cargan los ifCampos y sus desencadenadores al actualizarlos
        qtCamp = getattr(self, campo)
        tipoIf= param[0]
        campoMst = param[-1]
        
        cmpEditable = nuevoIfCampo(self, tipoIf, self.conMst, campoMst, campo_qt=qtCamp, param=param[1:-1])
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
                    self.trataSenyal(fuente+[campo],'mv', self.maestro[campo])

        self.vaciaIfCampos()
        cargaRIfC([self.TipoMaestro], self.cmpEditables)    
        
    def guardarSiCambios (self):
        if self.maestro and self.maestro.modificado():
            buttonReply = QMessageBox.question(self, 'Datos Modificados', "Datos modificados. ¿Desea guardarlos?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Cancel:
                return 0
            elif buttonReply == QMessageBox.Yes:
                self.mnj.almacena()
        return 1            
    
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
            mst = self.mnj.cargaMaestro(mst_ref=self.maestro, mov=mov) 
            if mst:
                if mst != self.maestro:
                    self.mnj.descarta(self.maestro)
                    self.maestro = mst
                    self.maestro.vaciaCamposModif()
                    self.maestro.asignaTunelSenyal(self.senyalMaestro)
                    self.senyalMaestro.habilitaTunel()
                    self.cargaIfCampos()
                return True                
            else:
                return False

    def nuevo(self):
        if self.guardarSiCambios():
            self.vaciaIfCampos()
            self.mnj.descarta(self.maestro)        
            self.maestro = self.mnj.nuevoMaestro(self.TipoMaestro, etiqueta=self.TipoMaestro)
            # Habilita el tunel entre el Maestro y la Interfaz del maestro
            self.maestro.asignaTunelSenyal(self.senyalMaestro)
            self.senyalMaestro.habilitaTunel()              

                
    def almacena(self):
        return self.mnj.almacena()

    def borra(self):
        buttonReply = QMessageBox.question(self, 'Eliminación', "¿Desea eliminar el registro actual?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            if self.mnj.borraMaestro(self.maestro):
                self.vaciaIfCampos()      
    
    def abrirBusquedaMaestro(self):
        # Si hay definida una busqueda para el maestro se abre
        if self.BusquedaMaestro and self.guardarSiCambios():
            ui = ifDgMstBusqueda(self.cuinf, self.TipoMaestro, self.BusquedaMaestro[0], self.BusquedaMaestro[1])
            if ui:
                ui.exec()
            campoB = ui.campoFilasSelec('id')
            if campoB:
                self.maestro.setId(int(campoB[0]))
                self.cargaMaestro('ig')    

    def abrirBusquedaCampo(self, campo):
        # Abre la busqueda de un campo y devuelve el valor buscado o nada en caso de cancelar
        externo = self.maestro.campoModifExterno(campo)
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
            # Se pasa la señal a todos los ifCampos unidos al campo maestro si los hay
            if (len(fuente)-1) and (fuente[1] in self.cmpEditables):
                for ifc in self.cmpEditables[fuente[1]]: 
                    ifc.trataSenyal(fuente[1:], senyal, *args)
     
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
        print('- '+str(self.mnj.session))
        for s in self.mnj.session:
            print (s)
        print('============================')
        print(self.maestro._camposModif)
        print(self.mnj.session.is_modified(self.maestro))

    