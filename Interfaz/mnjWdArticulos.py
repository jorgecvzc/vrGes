'''
Created on 19 dic. 2018

@author: cortesj
'''
from PyQt5 import QtWidgets, uic, QtCore
from Interfaces import ifMaestro

class ifArticulos(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Trabajos
    '''
    def __init__(self, *args, **kwargs):
        '''
        Inicia el maestro principal cuyos datos se van a tratar
        '''     
        super().__init__(*args, **kwargs, tipo_maestro="Articulo")
        uic.loadUi("Diseño/Articulos/wdArticulos.ui", self)

        '''
        Crea los ifCanpos que enlazaran los objetos del maestro con los de la interfaz
        '''
        self.nuevoIfCampo('ref', 'ifCadena', self.leRef)
        self.nuevoIfCampo('nombre', 'ifCadena', self.leNombre)
        self.nuevoIfCampo('descripcion', 'ifCadena', self.leDescripcion)

        mstPro = self.mnj.nuevoMaestro('Proveedor')
        cons = self.mnj.consultaMaestro(mstPro, None, ['id', 'nombre'], ["nombre"])
        self.nuevoIfCampo('proveedor', 'ifIdListaD', self.leProveedor, self.cbProveedor, list(cons['id']), list(cons['nombre']))
        
        self.nuevoIfCampo('observaciones', 'ifTexto', self.ptObs)
        self.nuevoIfCampo('manufacturado', 'ifVerificacion', self.chbManufacturado, [self.tbEscandallo])

        mstProc = self.mnj.nuevoMaestro('Proceso')
        consProc = self.mnj.consultaMaestro(mstProc, None, ['id', 'nombre'], ["nombre"])
        self.nuevoIfCampo('escandallo->proceso', 'ifListaD', self.cbProcesos, list(consProc['id']), list(consProc['nombre']))

        mstVar = self.mnj.nuevoMaestro('VarianteArt')
        consVar = self.mnj.consultaMaestro(mstVar, None, ['id', 'ref', 'nombre'], ["nombre"])
        self.nuevoIfCampo('numVariantes', 'ifCadena', self.leNumVariantes)        
        self.nuevoIfCampo('variante1', 'ifRefListaD', self.leVar1, self.cbVar1, list(consVar['id']), list(consVar['ref']), list(consVar['nombre']))        
        self.nuevoIfCampo('variante2', 'ifRefListaD', self.leVar2, self.cbVar2, list(consVar['id']), list(consVar['ref']), list(consVar['nombre']))  
        self.nuevoIfCampo('variante3', 'ifRefListaD', self.leVar3, self.cbVar3, list(consVar['id']), list(consVar['ref']), list(consVar['nombre']))  
                               
        twLineasCols = {'pieza':'Pieza','ref':'Ref','matRef':'Ref Material','matNombre':'Nombre', 'ancho':'Ancho', 'largo':'Largo','area':'Area'}
        self.nuevoIfCampo('escandallo->despiece', 'ifTabla', self.twDespiece, twLineasCols)
        
        twLineasTareas = {'refTarea':'Ref','nomTarea':'Tarea','tiempo':'Tiempo', 'coste':'Coste'}
        self.nuevoIfCampo('escandallo->procesoTareas', 'ifTabla', self.twTareas, twLineasTareas)        
                
        # Carga el primer maestro en la interfaz
        self.vePosicion('pri')        

    def trataSenyal(self, fuente, senyal, *args):
        super().trataSenyal(fuente, senyal, *args)


class ifVariantesArt(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, tipo_maestro="VarianteArt")
        uic.loadUi("Diseño/Articulos/wdVariantes.ui", self)

        '''
        Crea los ifCanpos que enlazaran los objetos del maestro con los de la interfaz
        '''
        self.nuevoIfCampo('ref', 'ifCadena', self.leRef)
        self.nuevoIfCampo('nombre', 'ifCadena', self.leNombre)

        # Carga el primer maestro en la interfaz
        self.vePosicion('pri')

    
class ifModificadoresArt(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, tipo_maestro="ModificadorArt")
        uic.loadUi("Diseño/Articulos/wdModificadores.ui", self)

        '''
        Crea los ifCanpos que enlazaran los objetos del maestro con los de la interfaz
        '''
        self.nuevoIfCampo('nombre', 'ifCadena', self.leNombre)
        self.nuevoIfCampo('ref', 'ifCadena', self.leRef)

        cons = self.mnj.nuevaConsultaMaestro('VarianteArt', campos_resultado=['id', 'ref', 'nombre'])
        cons = self.mnj.cargaConsultaMaestro(cons)
        self.nuevoIfCampo('variante', 'ifRefListaD', self.leVariante, self.cbVariante, list(cons.resultado('id')), list(cons.resultado('ref')), list(cons.resultado('nombre')))

        # Carga el primer maestro en la interfaz
        self.vePosicion('pri')

