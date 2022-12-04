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
        self.leRef.inicializa()
        
        # Asigna atajos de teclado y comandos correspondientes
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

    