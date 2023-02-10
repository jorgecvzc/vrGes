from sqlalchemy import select
from sqlalchemy.orm import object_session

from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import (
    QLineEdit, 
    QPlainTextEdit, 
    QCheckBox,
    QListWidget,
    QComboBox, 
    QTableWidget,
    )
from PyQt5.QtWidgets import QCompleter

from Interfaz.Dialogos import ifDgMst

import log
logger = log.get_logger(__name__)

'''
CLASES DE CONFIGURACIÓN DE LAS UNIONES ENTRE INTERFAZ Y CAMPOS DE MAESTRO
'''
class acConf(object):
    # Configuración de acciones
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.params = args
        self.paramsDic = kwargs
        
    def __str__(self):
        return 'Objeto acConf (Función: %s, Número parámetros: %s, %s)' % \
              (str(self.func), str(len(self.params)), str(len(self.paramsDic)))
        
class cConf(object):
    def __init__(self, *args, **kwargs):
        self.campo = args[0]
        self.conf = args[1:]
        self.acciones = kwargs.pop('accion', None)
        if not self.acciones:
            self.acciones = kwargs.pop('acciones', [])
        else:
            self.acciones = [self.acciones]
        self.params = kwargs
        
'''
CLASES DE UNION ENTRE INTERFAZ Y CAMPOS DE UN MAESTRO
'''
class ifCampo(object):
    # Clase madre de los campos de interfaz que se relacionan con un campo de maestro
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bloqueado = False
        self.campoMst = None
  
    def inicializa(self, c_conf):
        self.conf = c_conf
        self.campoMst = c_conf.campo
        self.acciones = c_conf.acciones
        self.cargaAccionesExtra()
          
    def cargaAccionesExtra(self):
        for acc in self.conf.acciones:
            args = acc.params
            kwargs = acc.paramsDic
            func = getattr(self, acc.func)
            self.itemDoubleClicked.connect(lambda: func(*args, **kwargs))
    
    def conMst(self):
        return self.parent().maestro            
          
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
 
    def inicializa(self, c_conf):
        super().inicializa(c_conf)
        self.editingFinished.connect(lambda: self.parent().maestro.__setitem__(self.campoMst, self.getValor())) 
           
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
            

class ifCadenaExt (QLineEdit, ifCampo):
    # Las Cadenas de tipo Ext solo podrán mostrar información, no actualizarla
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEnabled(False)
 
    def inicializa(self, c_conf):
        super().inicializa(c_conf)
        self.campoExt = c_conf.conf[0]
           
    def getValor(self):
        return self.text()
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.setText(str(valor[self.campoExt]))
            else:
                self.clear()
        
    def limpia(self):
        self.clear()

        
class ifTexto(ifCampo, QPlainTextEdit):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
    def inicializa(self, c_conf):
        super().inicializa(c_conf)
        self.textChanged.connect(
            lambda: self.parent().maestro.__setitem__(self.campoMst, self.getValor()))

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
    
    
class ifVerificacion(ifCampo, QCheckBox):
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
    def inicializa(self, c_conf):
        super().inicializa(c_conf)
        self.qtsHabil = c_conf.conf[-2]  # Campos dependientes de verificacion

        self.stateChanged.connect(
            lambda: self.actualizaValidador())

    def actualizaValidador(self):
        self.parent().maestro.__setitem__(self.campoMst, self.getValor())
        self.habilitaCampos()

    def getValor(self):
        return self.isChecked()
    
    def setValor(self, valor):
        if valor != self.getValor():
            self.blockSignals(True)
            if valor:
                self.setChecked(valor)
            else:
                self.setChecked(False)
            self.habilitaCampos()
            self.blockSignals(False)        
        
    def limpia(self):
        self.blockSignals(True)        
        self.setChecked(False)
        self.blockSignals(False)              
        
    def habilitaCampos(self):
        if self.qtsHabil:
            for elem in self.qtsHabil:
                elem.setEnabled(self.getValor())

    
class ifRefExtLista(QLineEdit, ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena asociada a un campo de tipo Externo
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lista = None        
        self.lRef = None
           
    def inicializa(self, c_conf):
        super().inicializa(c_conf)
        if c_conf.conf[1]:
            self.lista = c_conf.conf[-1][c_conf.conf[1]] # lista_mst
        else:
            self.lista = []
        self.campoLista = c_conf.conf[0]
        
        self.lRef = [str(l[self.campoLista]) for l in self.lista]
        qCompleter = QCompleter(self.lRef)
        self.setCompleter(qCompleter)
    
    def getValor(self):
        valor = self.text()
        result = None
        if self.lRef:
            if valor in self.lRef:
                ext = self.lista[self.lRef.index(valor)]
                result = object_session(self.parent().maestro).merge(ext)
        else:
            mstExt = getattr(self.parent().maestro.__class__, self.campoMst)
            mstExt = mstExt.property.mapper.class_
            stmt = select(mstExt).where(getattr(mstExt, self.campoLista) == valor)
            ext = object_session(self.parent().maestro).execute(stmt).fetchone()
            if ext: result = object_session(self.parent().maestro).merge(ext[0])
        return result
    
    def setValor(self, valor):
        if valor != self.getValor():
            if valor:
                self.setText(str(valor[self.campoLista]))
            else:
                self.clear()
        
    def limpia(self):
        self.clear()
            

class ifDesplegableExt (ifCampo, QComboBox):
    '''
    Campo que almacena indices y nmuestra sus correspondencias en una lista desplegable
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campoMst = None
        self.lista = []        
        self.lRef = None

    def inicializa(self, c_conf):        
        # *args: nombre_lista_mst, campo_lista, listas
        super().inicializa(c_conf)
        
        self.clear()
        l = c_conf.conf[-1][c_conf.conf[1]]
        self.campoLista = c_conf.conf[0]
        if l: 
            self.lista = l
            self.addItems(['']+self.lista.col(self.campoLista))

        self.currentIndexChanged.connect(
            lambda: self.parent().maestro.__setitem__(self.campoMst, self.getValor()))

    def getValor(self):
        ci = self.currentIndex()
        if ci:
            return object_session(self.parent().maestro).merge(self.lista[ci-1])
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
  
    
class ifListaMst (ifCampo, QListWidget):
    '''
    Campo que muestra una lista de maestros y guarda la correlación de sus indices
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cammpoLst = None

    def inicializa(self, c_conf):        
        # *args: nombre_lista_mst, campo_lista, listas
        super().inicializa(c_conf)
        self.campoLst = self.conf.conf[0]
   
        #self.currentIndexChanged.connect(            lambda: self.conMst().__setitem__(self.campoMst, self.getValor()))

    def getValor(self):
        ci = self.currentRow()
        if ci >= 0:
            return self.conMst()[self.conf.campo][ci]
        else:
            return None
            
    def setValor(self, valor):
        if valor != self.getValor():
            self.blockSignals(True)
            if valor:
                self.setCurrentText(valor[self.campoLst])
            else:
                self.limpia()
            self.blockSignals(False)
     
    def limpia(self):
        self.clear()

    def trataSenyal(self, fuente, senyal, *args):
        # Tratará las señales procedentes del maestro principal
        logger.info('iflista.trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))

        if senyal == 'mv':
            self.limpia()
            for l in args[0]:
                self.addItem(l[self.campoLst])

    def abreIfMaestro(self, if_mst_clase, **kwargs):
        # Se carga el ifUinf de edicion
        ifMst = if_mst_clase(self.parent().cuinf)
        nuevo = kwargs.pop('nuevo', False)
        dmst = ifDgMst(self)
        dmst.dw.setWidget(ifMst)
                
        if nuevo:
            mst = self.conMst()
            ifMst.maestro['cliente'] = ifMst.mnj.session.merge(mst)
        else:
            valor = self.getValor()
            if valor:
                ifMst.setMaestro(valor)

        cambio = dmst.exec()
        if cambio:
            if nuevo:
                valor = self.parent().mnj.session.merge(ifMst.maestro)
                self.parent().mnj.session.refresh(mst)
            else:
                self.parent().mnj.session.refresh(valor)
            self.parent().cargaIfCampos()
            
        del(dmst)                
                        
class ifLineaTabla (object):
    def __init__(self, mst):
        self.maestro = mst
        
    def conMst(self):
        return self.maestro
    
    
class ifTabla (ifCampo, QTableWidget):
    '''
    Objetos de interfaz para el manejo de tablas
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confCampos = None
        self.valListas = None
        
    def inicializa(self, c_conf):
        super().inicializa(c_conf)        
        self.confCampos = c_conf.conf[0] # Configuraciones de cada uno de los campos de la tabla
        self.valListas = self.parent().valListas

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
        
        self.itemChanged.connect(lambda: self.parent().maestro.__setitem__(self.campoMst, self.getValor()))
        
        
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
                self.parent().maestro.nuevaLinea(self.campoMst)                
            else:
                self.parent().maestro.nuevaLinea(self.campoMst, fila)
        elif action == borraAction:
            if (self.currentRow() >= 0):
                self.parent().maestro.borraLinea(self.campoMst, fila)
        elif action == agregAction:
            self.parent().maestro.nuevaLinea(self.campoMst)

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
        self.parent().maestro[self.campoMst][ix.row()][self.nombreCol(ix.column())] = ch.isChecked()
    
    def conMstLinea(self):
        return self.parent().maestro[self.campoMst][self.currentRow()]
        
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

            cmpEditable = nuevoIfCampo(
                self, tipoIf, self.conMstLinea, campoMst, 
                *confCampo[1:-1], self.valListas)
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
        logger.info('ifTabla.trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))

        # Se pasa la señal a todos los ifCampos unidos al campo maestro si los hay
        if (len(fuente)-1):
            nFila = fuente[1]
            if senyal == 'nf':
                self.agregaFila(self.parent().maestro[self.campoMst][nFila], nFila)
            elif senyal == 'bf':
                self.removeRow(nFila)
            elif (len(fuente)-2):
                if (senyal == 'mv'): # Se ha modificado un valor concreto
                    self.setValor(nFila, fuente[2], args[0])                

        elif senyal == 'mv':
            self.limpia()
            for l in args[0]:
                self.agregaFila(l, l.orden)
                

def nuevoIfCampo(if_widget, tipoIf, padre, campoMst, *args):
    # Se cargan los ifCampos y sus desencadenadores al actualizarlos
    # Parámetros kwargs
    #  - campo_qt: Campo qt asociado al ifCampo. Si no existe se crea uno nuevo
    #  - param: Parámetros extra para la creación de cada ifCampo
    
    ifCampo = eval(tipoIf+"(parent=if_widget)")
    ifCampo.inicializa(campoMst, *args)
  
    return ifCampo 
   

