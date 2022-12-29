'''
Created on 19 dic. 2018

@author: cortesj
'''
from Interfaz.Interfaces import ifMaestro

       
class ifTrabajos(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Proceso
    '''
    TipoMaestro="Trabajos.Trabajo"
    Interfaz = "wdArticulos"

    ListasMst = {
        'lProveedores': ('Articulos.Proveedor', ['id', 'nombre'])
    }       

    Campos = {
        'leRef': ('ref'),
        'leNombre': ('nombre'),
        'leDescripcion': ('descripcion'),
        'leProveedor': ('proveedor', 'id', 'lProveedores',),
        'cbProveedor': ('proveedor', 'nombre', 'lProveedores',),
        'ptObs': ('observaciones',),
        'chbManufacturado': ('manufacturado', ['tbEscandallo'],),
        'leNumVariantes': ('numVariantes',)
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
        'Tarea': ('ifRefExt', 'tarea', 'ref', 'lTareas', ),
        'Única': ('ifVerificacion', 'unica', [],),
        'Observaciones': ('ifCadena', 'observaciones'),
    }

    Campos = {
        'leRef': ('ref',),
        'leNombre': ('nombre',),
        'ptObs': ('observaciones',),
        'twTareas': ('tareas', linTarea,)
    }
    
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    


class ifTareas(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Tarea
    '''
    TipoMaestro="Trabajos.Tarea"
    Interfaz = "Trabajos/wdTareas"

    Campos = {
        'leRef': ('ref',),
        'leNombre': ('nombre',),
        'leDescripcion': ('descripcion',),
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])


class ifProcedimientos(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Proceso
    '''
    TipoMaestro="Trabajos.Procedimiento"
    Interfaz = "Trabajos/wdProcedimientos"

    ListasMst = {
        'lClientes': ('Personas.Cliente', ['ref', 'nombre'])
    }       

    Campos = {
        'reCliRef': ('cliente', 'ref', None),
        'ceCliNombre': ('cliente', 'nombre'),
        'cdNombre': ('nombre',),
    }

    BusquedaMaestro = (['nombre'], ['nombre'])
