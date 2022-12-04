from PyQt5.Qt import QTableWidget, QLineEdit

'''
CLASES DE UNION ENTRE INTERFAZ Y CAMPOS DE UN MAESTRO
'''
class ifCampo(object):
    # Clase madre de los campos de interfaz que se relacionan con un campo de maestro
    def __init__(self, ):
        self.bloqueado = False
        self.campo = None
        
    def trataSenyal(self, fuente, senyal, *args):
        # Tratará las señales procedentes del maestro principal
        logger.info('ifCampo['+self.campo+'].trataSenyal ' + str(fuente) + ' - ' + senyal + ' - ' + str(args))
        
        # Se pasa la señal al siguiente campo si está representado en la interfaz
        if (len(fuente) == 1):
            self.setValor(args[0])
        else:
            self[fuente[1]].trataSenyal(fuente[1:], senyal, args)        

    
class ifCadena(QLineEdit, fCampo):
        
    '''
    Objetos de interfaz para mostrar una cadena
    '''
    def __init__(self, campo_qt, conMst, campo):
        super().__init__(campo_qt, campo)
        
        self.ifc.editingFinished.connect(lambda: conMst().__setitem__(self.campo, self.getValor())) 
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

class ifRefExt(QLineEdit, ifCampo):
    '''
    Objetos de interfaz para mostrar una cadena asociada a un campo de tipo Externo
    '''
    def __init__(self, campo_qt, lista_mst, campo_lista, con_mst, campo):
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
        self.conMst().__setitem__(self.campo, self.getValor())        

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
        self.conMst().__setitem__(self.campo, valor)
                                
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
   


class aa():
    a = 'a'

    def __init__(self):
        pass

    def __setitem__(self, a, b):
        print('aa',a, b)

class a (QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('Aqui')
        self.campo = None
        self.getValor = None
        self.editingFinished.connect(lambda: self.conMst().__setitem__(self.campo, self.getValor)) 

    def inicializa(self):
        self.conMst = aa
        self.campo = ''

