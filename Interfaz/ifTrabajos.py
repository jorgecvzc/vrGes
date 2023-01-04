'''
Created on 19 dic. 2018

@author: cortesj
'''
from Interfaz.Interfaces import ifMaestro
from Interfaz.Campos import cConf
       
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
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre'),
        'leDescripcion': cConf('descripcion'),
        'leProveedor': cConf('proveedor', 'id', 'lProveedores'),
        'cbProveedor': cConf('proveedor', 'nombre', 'lProveedores'),
        'ptObs': cConf('observaciones',),
        'chbManufacturado': cConf('manufacturado', ['tbEscandallo']),
        'leNumVariantes': cConf('numVariantes')
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
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre'),
        'ptObs': cConf('observaciones'),
        'twTareas': cConf('tareas', linTarea,)
    }
    
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    


class ifTareas(ifMaestro):
    '''
    Clase para el manejo de la interfaz del maestro Tarea
    '''
    TipoMaestro="Trabajos.Tarea"
    Interfaz = "Trabajos/wdTareas"

    Campos = {
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre'),
        'leDescripcion': cConf('descripcion'),
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
        'reCliRef': cConf('cliente', 'ref', None),
        'ceCliNombre': cConf('cliente', 'nombre'),
        'cdNombre': cConf('nombre'),
    }

    BusquedaMaestro = (['nombre'], ['nombre'])
