from sqlalchemy.orm import object_session

from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import QTableWidget, QLineEdit, QComboBox
from PyQt5.QtWidgets import QCompleter

import log
logger = log.get_logger(__name__)

'''
CLASES DE UNION ENTRE INTERFAZ Y CAMPOS DE UN MAESTRO
'''
class ifCampo(object):
    # Clase madre de los campos de interfaz que se relacionan con un campo de maestro
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bloqueado = False
        self.conMst = None
        self.campoMst = None
        
    def trataSenyal(self, fuente, senyal, *args):
        # Tratará las señales procedentes del maestro principal
        logger.info('ifCampo['+self.campoMst+'].trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))
        
        # Se pasa la señal al siguiente campo si está representado en la interfaz
        if (len(fuente) == 1):
            self.setValor(args[0])
        else:
            self[fuente[1]].trataSenyal(fuente[1:], senyal, args)        

    
class ifCadena(QLineEdit, ifCampo):
        
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conMst = None
        self.campoMst = None
                
        self.editingFinished.connect(lambda: self.conMst().__setitem__(self.campoMst, self.getValor())) 
 
    def inicializa(self, conMst, campoMst, *args):
        self.conMst = conMst
        self.campoMst = campoMst  
           
    def getValor(self):
        return self.text()
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.setText(str(valor))
            else:
                self.clear()
        
    def limpia(self):
        self.clear()
        
    def procesaTeclas(self, key):
        #self.ifc.returnPressed.connect(self.procesaTeclas)
        if key == QtCore.Qt.Key_Return:
            print('return key pressed')
        else:
            print('key pressed: %s' % key)

class ifRefExt(QLineEdit, ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena asociada a un campo de tipo Externo
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conMst = None          
        self.campoMst = None
        self.lista = None        
        self.lRef = None
     
        self.editingFinished.connect(lambda: self.conMst().__setitem__(self.campoMst, self.getValor())) 
            
    def inicializa(self, con_mst, campo,*args):
        self.campoMst = campo

        self.lista = args[-1][args[-3]] # lista_mst
        self.campoLista = args[-2]
        
        self.lRef = [str(l[self.campoLista]) for l in self.lista]
        print(self.lRef)
        qCompleter = QCompleter(self.lRef)
        self.setCompleter(qCompleter)
        print('aquí')
        # self.ifc.__dict__['ifCampo'] = self # Los campos qt apuntarán al campo de interfaz que los engloba para poder procesar eventos como los del teclado
        self.conMst = con_mst        

    def getValor(self):
        valor = self.text()
        if valor in self.lRef:
            ext = self.lista[self.lRef.index(valor)]
            return object_session(self.conMst()).merge(ext)
        else:
            return None
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.setText(str(valor[self.campoLista]))
            else:
                self.clear()
        
    def limpia(self):
        self.clear()
        
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

        self.textChanged.connect(lambda: conMst().__setitem__(campo, self.getValor()))

    def getValor(self):
        return self.toPlainText()
    
    def setValor(self, valor):
        if valor != self.getValor():
            if (valor) or (valor == ""):
                self.appendPlainText(valor)
            else:
                self.limpia()
        
    def limpia(self):
        self.blockSignals(True)        
        self.clear()
        self.blockSignals(False)        
    
    
class ifVerificacion(ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, qt_checkbox, qts_habilitados, conMst, campo):
        super().__init__(qt_checkbox, campo)
        self.qtsHabil = qts_habilitados
        self.stateChanged.connect(lambda: self.actualizaValidador(conMst(), campo))

    def getValor(self):
        return self.chb.isChecked()
    
    def setValor(self, valor):
        if valor != self.getValor():
            self.blockSignals(True)        
            self.setChecked(valor)
            self.validaCampos()
            self.blockSignals(False)        
        
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
            
            
class ifListaExt(ifCampo, QComboBox):
    '''
    Objetos de interfaz que muestran un indice y su correspondencia en una lista desplegable
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conMst = None          
        self.campoMst = None
        self.lista = None        
        self.lRef = None

    def inicializa(self, con_mst, campo,*args):        
        # *args: nombre_lista_mst, campo_lista, listas
        self.conMst = con_mst
        self.campoMst = campo
        
        self.clear()
        self.lista = args[-1][args[0]]
                        
        self.campoLista = args[1]
        self.addItems(['']+self.lista.col(self.campoLista))

        self.currentIndexChanged.connect(
            lambda: self.conMst().__setitem__(self.campoMst, self.getValor()))

    def getValor(self):
        ci = self.currentIndex()
        if ci:
            return object_session(self.conMst()).merge(self.lista[ci-1])
        else:
            return None
            
    def setValor(self, valor):
        if valor != self.getValor():
            self.blockSignals(True)
            if valor:
                self.setCurrentText(valor[self.campoLista])
            else:
                self.limpia()
            self.blockSignals(False)
     
    def limpia(self):
        self.blockSignals(True)
        self.setCurrentIndex(0)
        self.blockSignals(False)
        

        
class ifLineaTabla(object):
    def __init__(self, mst):
        self.maestro = mst
        
    def conMst(self):
        return self.maestro
    
    
class ifTabla(ifCampo, QTableWidget):
    '''
    Objetos de interfaz para el manejo de tablas
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confCampos = None
        self.conMst = None
        self.campoMst = None
        
    def inicializa(self, con_mst, campo_mst, *args):
        self.confCampos = args[0]
        self.conMst = con_mst

        # Los objetos complejos tienen que tener acceso al maestro ya que tienen señales internas de modificación
        self.campoMst = campo_mst
        # Se crean las columnas de la tabla según la lista paada
        self.setColumnCount(len(self.confCampos))
        i = 0
        for s in self.confCampos.keys():
            self.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(s))
            i+=1

        # Se acopla el menú contextual genérico de las tablas
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pos: self.menuIfTabla(pos))
        self.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(lambda pos: self.menuIfTabla(pos))

        # Asigna los tratamientos especiales para teclas de control de movimiento
        # QtWidgets.QShortcut(QtCore.Qt.Key_Tab, self.ifc, activated=lambda: self.trataTab(campo))
                
        # porc_col = .98/len(self.campos)
        #self.ifc.setColumnWidth(i,self.ifc.width()*porc_col)
        #self.ifc.setSizeAdjustPolicy(Qt5.QtWidgets.QAbstractScrollArea.AdjustToContents)
        #self.ifc.resizeColumnsToContents()
        cabecera = self.horizontalHeader() 
        for i in range(self.columnCount()-1):
            cabecera.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        i += 1
        cabecera.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        
        self.itemChanged.connect(lambda: self.conMst().__setitem__(self.campoMst, self.getValor()))
        
        
    def menuIfTabla(self, posicion):
        menu = QtWidgets.QMenu()
        insertAction = menu.addAction("Inserta Fila")
        borraAction = menu.addAction("Borra Fila")
        agregAction = menu.addAction("Agrega Fila")
        action = menu.exec_(self.mapToGlobal(posicion))
        #self.senyalMaestro.deshabilitaSenyal(self.tipo_maestro, campo)
        fila = self.verticalHeader().logicalIndexAt(posicion)
        if action == insertAction:
            if self.currentRow() < 0:
                self.conMst().nuevaLinea(self.campoMst)                
            else:
                self.conMst().nuevaLinea(self.campoMst, fila)
        elif action == borraAction:
            if (self.currentRow() >= 0):
                self.conMst().borraLinea(self.campoMst, fila)
        elif action == agregAction:
            self.conMst().nuevaLinea(self.campoMst)

    def trataTab(self, campo):
        #event = Qt5.QtGui.QKeyEvent(Qt5.QtCore.QEvent.KeyPress, Qt5.QtCore.Qt.Key_Tab, Qt5.QtCore.Qt.NoModifier)
        #Qt5.QtCore.QCoreApplication.postEvent(self, event)
        qtw = self
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
        self.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(args[0]))
        
    def nombreCol(self, pos):
        return self.campos[pos]
            
    def getValor(self, lin, col):
        return self.cellWidget(lin, self.campos.index(col))
    
    def setValor(self, lin, col, valor):
        if isinstance(col, str):
            coln = self.campos.index(col)
        else:
            coln = col
            
        self.blockSignals(True)
        if isinstance(valor, bool):
            chkBox = QtWidgets.QCheckBox(parent=self)
            chkBox.setChecked(valor)
            chkBox.stateChanged.connect(self.trataPulsaBoton)
            self.setCellWidget(lin, coln, chkBox)          
        else:
            logger.warning('Alerta!, alerta!')     
            '''    
            if valor:
                self.ifc.setItem(lin, coln, QtWidgets.QTableWidgetItem(str(valor)))
            else:
                self.ifc.setItem(lin, coln, QtWidgets.QTableWidgetItem(''))
            '''
            q = QtWidgets.QLineEdit(parent=self)
            q.setStyleSheet("border: 0px;")
            q.setText('a')
            self.setCellWidget(lin, coln, q)
            
        self.blockSignals(False)
    
    def trataPulsaBoton(self):
        ch = self.sender()
        ix = self.indexAt(ch.pos())
        self.conMst.maestro[self.campoMst][ix.row()][self.nombreCol(ix.column())] = ch.isChecked()
    
    def conMstLinea(self):
        return self.conMst()[self.campoMst][self.currentRow()]
        
    def agregaFila(self, valores, n_fila=None):
        # Se cargan los ifCampos y sus desencadenadores al actualizarlos
        if n_fila == None:
            n_fila = self.rowCount()        
        self.insertRow(n_fila)
        i = 0
        for confCampo in self.confCampos.values():
            # Se cargan los ifCampos y sus desencadenadores al actualizarlos
            tipoIf= confCampo[0]
            campoMst= confCampo[-1]

            cmpEditable = nuevoIfCampo(self, tipoIf, self.conMstLinea, campoMst, param=confCampo[1:-1])
            cmpEditable.setValor(valores[campoMst])
            self.setCellWidget(n_fila, i, cmpEditable)
            self.setStyleSheet("border : 0px;")
            i += 1               

    def posActual(self):
        return (self.currentRow(), self.currentColumn())
  
    def posUltima(self):
        # Devuelve True si la posición actual es la última
        if (self.currentColumn() == self.columnCount()-1):
            return self.currentRow() == self.rowCount()-1
            
    def valorActual(self):
        pos = self.posActual()
        if type(self.cellWidget(pos[0], pos[1])) == QtWidgets.QCheckBox:
            return self.cellWidget(pos[0], pos[1]).isChecked()
            #return (self.ifc.item(pos[0],pos[1]).checkState() == 2)
        else:
            return self.item(pos[0],pos[1]).text()
    
    def limpia(self):
        for i in range(self.rowCount()-1, -1, -1):
            self.removeRow(i)

    def trataSenyal(self, fuente, senyal, *args):
        # Tratará las señales procedentes del maestro principal
        logger.info('ifMaestro.trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))

        # Se pasa la señal a todos los ifCampos unidos al campo maestro si los hay
        if (len(fuente)-1):
            nFila = fuente[1]
            if senyal == 'nf':
                self.agregaFila(self.conMst()[self.campoMst][nFila], nFila)
            elif senyal == 'bf':
                self.removeRow(nFila)
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
    
    param = kwargs.pop('param', [])
           
    ifCampo = eval(tipoIf+"(parent=if_widget)")
    ifCampo.inicializa(conMst, campoMst, param)
    '''
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
    '''    
    return ifCampo 
   

