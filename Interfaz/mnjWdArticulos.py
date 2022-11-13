'''
Created on 19 dic. 2018

@author: cortesj
'''
from PyQt5 import QtWidgets, uic, QtCore
from Interfaz.Interfaces import ifMaestro

class ifArticulos(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Trabajos
    '''
    TipoMaestro="Artiuclos.Articulo"
    Interfaz = "Diseño/Articulos/wdArticulos.ui"

    ListasMst = {
        'lProveedores': ('.Proveedor', ['id', 'nombre'])
    }       

    Campos = {
        'ref': ('ifCadena', 'leRef'),
        'nombre': ('ifCadena', 'leNombre'),
        'descripcion': ('ifCadena', 'leDescripcion'),
        'proveedor': ('ifIdListaD', 'leProveedor', 'cbProveedor', 'lProveedores'),
        'observaciones': ('ifTexto', 'ptObs'),
        'manufacturado': ('ifVerificacion', 'chbManufacturado')
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    
    '''
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
                
    def trataSenyal(self, fuente, senyal, *args):
        super().trataSenyal(fuente, senyal, *args)
    '''        

class ifVariantesArt(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro="Articulos.Variante"
    Interfaz = "wdVariantes.ui"
    
    Campos = {
        'ref': ('ifCadena', 'leRef'),
        'nombre': ('ifCadena', 'leNombre')
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])
    
    
class ifModificadoresArt(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro = "Articulos.Modificador"
    Interfaz = "wdModificadores.ui"
 
    ListasMst = {
        'lVarianteArt': ('Articulos.Variante', ['ref', 'nombre'])
    }   
    
    Campos = {
        'ref': ('ifCadena', 'leRef'),
        'nombre': ('ifCadena', 'leNombre'),
        'variante': ('ifRefListaD', 'leVariante', 'cbVariante', 'lVarianteArt')
    }    



