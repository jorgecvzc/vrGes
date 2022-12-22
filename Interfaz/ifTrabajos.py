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


class ifProcesos(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Procesos
    '''

    TipoMaestro="Trabajos.Proceso"
    Interfaz = "Trabajos/wdProcesos"

    ListasMst = {
        'lTareas': ('Trabajos.Tarea', ['nombre', 'ref'])
    }   

    linTarea = {
        'Tarea': ('ifRefExt', 'lTareas', 'ref', 'tarea'),
        'Única': ('ifVerificacion', [], 'unica'),
        'Observaciones': ('ifCadena', 'observaciones'),
    }

    Campos = {
        'leRef': ('ifCadena', 'ref'),
        'leNombre': ('ifCadena', 'nombre'),
        'ptObs': ('ifTexto', 'observaciones'),
        'twTareas': ('ifTabla', linTarea, 'tareas')
    }
    
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    


class ifTareas(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Tarea
    '''
    TipoMaestro="Trabajos.Tarea"
    Interfaz = "Trabajos/wdTareas"

    Campos = {
        'leRef': ('ifCadena', 'ref'),
        'leNombre': ('ifCadena', 'nombre'),
        'leDescripcion': ('ifCadena', 'descripcion'),
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    


