'''
Created on 4 mar. 2019

@author: cortesj
'''
import sys

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMessageBox, QShortcut

from Interfaz.Dialogos import ifDgMst, ifDgMstBusqueda
from Interfaz.Campos import ifTabla

from Señales import TunelSenyal

import log
logger = log.get_logger(__name__)

 
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
    Botones = {}
    BusquedaMaestro = ()
    keyPressed = QtCore.pyqtSignal(int)    
    
    def __init__(self, control_uinfs, *args, **kwargs):
        # Inicializa ControlUinf, Manejador, Tunel de Señales y Maestro
        self.cuinf = control_uinfs
        self.mnj = control_uinfs.mnjMaestros()
        self.mnjListas = control_uinfs.mnjListas()
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
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)          
        
        # Carga la interfaz gráfica
        uic.loadUi('Interfaz/Diseño/'+self.Interfaz+'.ui', self)
        
        # Se crean los campos de interfaz
        for campoIf, campoConf in self.Campos.items():
            ifCampo = self.agregaIfCampo(campoIf, campoConf)
            if not ifCampo.campoMst in self.cmpEditables:
                self.cmpEditables[ifCampo.campoMst] = [ifCampo]
            else:
                self.cmpEditables[ifCampo.campoMst].append(ifCampo)
            
        # Asigna los procedimeintos de los botones si los hubiera
        for b in self.Botones.keys():
            ifCampo = getattr(self, self.Botones[b][0])
            args = self.Botones[b][1].params
            kwargs = self.Botones[b][1].paramsDic
            func = getattr(ifCampo, self.Botones[b][1].func)
            boton = getattr(self, b)
            boton.clicked.connect(lambda: func(*args, **kwargs))
            
        # Asigna atajos de teclado y comandos correspondientes
        self.shortcut_open = QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcut_open.activated.connect(lambda: self.procesaAtajo('BC')) 
        self.keyPressed.connect(self.on_key)
        
        self.nuevo()

    def __del__(self):
        print(f'Delete {self!s}')
        
    def keyPressEvent(self, event):
        super(ifMaestro, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())
         
    def on_key(self, key):
        '''
        Remite la tecla al ifCampo actual para que la procese
        '''
        if (key == 16777220) and (self.focusWidget()):
            pfw = self.focusWidget().parent().parent()
            if isinstance(pfw, ifTabla):
                if pfw.posUltima():
                    pfw.maestro.nuevaLinea(pfw.campoMst)
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
    
    def agregaIfCampo(self, campo, conf):
        # Se cargan los ifCampos y sus desencadenadores al actualizarlos
        qtCamp = getattr(self, campo)
        qtCamp.inicializa(conf)
        '''
        for acc in conf.acciones:
            args = acc.params+[qtCamp]
            kwargs = acc.paramsDic
            func = getattr(self, acc.func)
            qtCamp.itemDoubleClicked.connect(lambda: func(*args, **kwargs))                    
        '''
        return qtCamp
       
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
    
    def guardarSiCambios (self, automatico=False):
        if self.maestro and self.maestro.modificado():
            if not automatico:
                buttonReply = QMessageBox.question(self, 'Datos Modificados', "Datos modificados. ¿Desea guardarlos?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Cancel:
                    return 0
                elif buttonReply == QMessageBox.Yes:
                    self.mnj.almacena()
                    return 1
            else:
                self.mnj.almacena()
                return 1
        return 2          
    
    '''
     Operaciones del usuario sobre el maestro
    '''
    # primeraAccion a procesar llamada por la página principal
    def primeraAccion (self):
        # Carga el primer maestro en la interfaz
        if not self.cargaMaestro('pri'):
            self.nuevo()

    # Se asigna un maestro directameten
    def setMaestro(self, mst):
        if mst != self.maestro:
            self.logImp()
            self.mnj.descarta(self.maestro)
            valor = self.mnj.agregaExterno(mst)
            self.maestro = valor
            self.cargaIfCampos()
            
    # Fucniones de navegación sobre los maestros almacenados
    def cargaMaestro(self, mov):
        if self.guardarSiCambios():
            idm = self.maestro.getId()
            if mov not in ['pri', 'ult']:
                mst = self.mnj.cargaMaestro(
                    tipo=self.TipoMaestro, 
                    filtro={'campos': {'id': idm}}, 
                    mov=mov)
            else:
                mst = self.mnj.cargaMaestro(
                    tipo=self.TipoMaestro, 
                    mov=mov) 
            if mst:
                if mst != self.maestro:
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
            self.mnj.descarta()        
            self.maestro = self.mnj.nuevoMaestro(self.TipoMaestro, etiqueta=self.TipoMaestro)
            # Habilita el tunel entre el Maestro y la Interfaz del maestro
            self.maestro.asignaTunelSenyal(self.senyalMaestro)
            self.senyalMaestro.habilitaTunel()        

    def almacena(self):
        return self.mnj.almacena()

    def borra(self):
        buttonReply = QMessageBox.question(self, 'Eliminación', "¿Desea eliminar el registro actual?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            if self.mnj.borra(self.maestro):
                self.vaciaIfCampos()    

    def abrirIfMaestroIfCampo(self, if_mst_clase, if_campo, **kwargs):
        # Se carga el ifUinf de edicion
        if isinstance(if_campo, str):
            campo = getattr(self, if_campo)
        else:
            campo = if_campo
        ifMst = if_mst_clase(self.cuinf)
        if kwargs.pop('nuevo', None):
            pass
        else:
            valor = campo.getValor()
            if valor:
                ifMst.setMaestro(valor)
                # Se añade el uinf a un diálogo
        dmst = ifDgMst(self)
        dmst.dw.setWidget(ifMst)
        if dmst.exec():
            print (ifMst.maestro['nombre'])
        
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
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowModality(QtCore.Qt.WindowModal)
            error_dialog.showMessage("Error inesperado: " + 
                                     str(sys.exc_info()[0]) +'\n' + 
                                     str(sys.exc_info()[1]))                        

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

    