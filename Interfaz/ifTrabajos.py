'''
Created on 19 dic. 2018

@author: cortesj
'''
from PyQt5 import QtWidgets, uic, QtCore
from Interfaz.Interfaces import ifMaestro

class ifTrabajos(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Proceso
    '''
    TipoMaestro="Articulos.Articulo"
    Interfaz = "wdArticulos"

    ListasMst = {
        'lProveedores': ('Articulos.Proveedor', ['id', 'nombre'])
    }       

    Campos = {
        'leRef': ('ifCadena', 'ref'),
        'leNombre': ('ifCadena', 'nombre'),
        'leDescripcion': ('ifCadena', 'descripcion'),
        'leProveedor': ('ifCadenaRef', 'lProveedores', 'id', 'proveedor'),
        'cbProveedor': ('ifListaRef', 'lProveedores', 'nombre', 'proveedor'),
        'ptObs': ('ifTexto', 'observaciones'),
        'chbManufacturado': ('ifVerificacion', ['tbEscandallo'], 'manufacturado'),
        'leNumVariantes': ('ifCadena', 'numVariantes')
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])

    '''
    Clase para el manejo de la interfaz de la clase Trabajos
    '''
    def __init__(self, *args, **kwargs):
        '''
        Inicia el maestro principal cuyos datos se van a tratar
        '''             
        super().__init__(*args, **kwargs, tipo_maestro="Trabajo")
        uic.loadUi("wdTrabajos", self)

        '''
        Crea los ifCanpos que enlazaran los objetos del maestro con los de la interfaz
        '''
        self.nuevoIfCampo('nombre', 'ifCadena', self.leNombre)
        
        mstCli = self.mnj.nuevoMaestro('Cliente')
        consCli = self.mnj.consultaMaestro(mstCli, None, ['id', 'nombre'], ["nombre"])        
        self.nuevoIfCampo('cliente', 'ifIdListaD', self.leCliente, self.cbCliente, list(consCli['id']), list(consCli['nombre']))
        
        self.nuevoIfCampo('artRef', 'ifCadena', self.leArtRef)
        self.nuevoIfCampo('artNombre', 'ifCadena', self.leArtNombre)
        self.nuevoIfCampo('observaciones', 'ifTexto', self.ptObs)
                
        self.twLineasCols = {'nomPosicion':'Posicion','refProceso':'Proceso', 'nomProceso':'Nombre', 'observaciones':'Observaciones'}
        self.nuevoIfCampo('procesos', 'ifTabla', self.twProcesos, self.twLineasCols)
        
        # Carga el primer maestro en la interfaz
        self.vePosicion('p')            


class ifProcesos(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Procesos
    '''

    TipoMaestro="Trabajos.Proceso"
    Interfaz = "wdProcesos"

    #twLineasCols = {'tareaRef':'Tarea','tareaNombre':'Nombre', 'unica':'Tarea Única', 'observaciones':'Observaciones'}
    twLineasCols = {'tareaRef':'Tarea','unica':'Tarea Única', 'observaciones':'Observaciones'}
    
    Campos = {
        'leRef': ('ifCadena', 'ref'),
        'leNombre': ('ifCadena', 'nombre'),
        'ptObs': ('ifTexto', 'observaciones'),
        'twTareas': ('ifTabla', twLineasCols, 'tareas')
    }
    
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    

    '''
    Crea los ifCanpos que enlazaran los objetos del maestro con los de la interfaz

    
    self.nuevoIfCampo('tareas', 'ifTabla', self.twTareas, self.twLineasCols)

    # Carga el primer maestro en la interfaz
    self.vePosicion('p')
        
    def actualizaMaestro(self, nombre_campo, valor):
        # Si se ha modificado un referencia de tarea en la lista de tareas se deshabilita su señal para que no hayan bucles
        #  se carga la nueva linea a traves de los dependientes de la clave principal y se propaga la señal inicial
        if (nombre_campo == 'tareas'):
            tabla = self.cmpEditables[nombre_campo]
            pos = tabla.posActual()
            if (tabla.campos[pos[1]] == 'refTarea'):
                mst = self.conMst.mnj.nuevoMaestro('Tarea')
                mst['ref'] = tabla.valorActual()
                mst = self.conMst.mnj.cargaMaestro('Tareas', nombre_campo, mst, condicion='pi')                
                self.maestro[nombre_campo].setValor(pos[0], 'tarea', mst.getId())            
            else:
                super().actualizaMaestro(nombre_campo, valor)
        else:
            super().actualizaMaestro(nombre_campo, valor)
    
    '''
class ifTareas(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Tarea
    '''
    TipoMaestro="Trabajos.Tarea"
    Interfaz = "wdTareas"

    Campos = {
        'leRef': ('ifCadena', 'ref'),
        'leNombre': ('ifCadena', 'nombre'),
        'leDescripcion': ('ifCadena', 'descripcion'),
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    

       
class ifPosiciones(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Posiciones
    '''
    TipoMaestro="Trabajos.Tarea"
    Interfaz = "wdPosiciones"

    Campos = {
        'leNombre': ('ifCadena', 'nombre'),
        'leDescripcion': ('ifCadena', 'descripcion'),
    }
