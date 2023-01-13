'''
Created on 19 dic. 2018

@author: cortesj
'''
from Interfaz.Interfaces import ifMaestro
from Interfaz.Campos import acConf, cConf
from Interfaz.ifTrabajos import ifProcedimientos

class ifProveedores(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro = "Personas.Proveedor"
    Interfaz = "Personas/wdProveedores"
    
    Campos = {
        'leRef': cConf('ifCadena', 'ref'),
        'leNombre': cConf('ifCadena', 'nombre'),
    }  
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])


class ifClientes(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro = "Personas.Cliente"
    Interfaz = "Personas/wdClientes"
    
    ListasMst = {
        'lProcedimientosCli': ('Trabajos.Procedimiento', ['nombre'])
    }

    Campos = {
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre',),
        'lwProcedimientos': cConf('procedimientos', 'nombre', 
                                  accion=acConf('abreIfMaestro', ifProcedimientos))
    }

    Botones = {
        'pbAgregaProc': ('lwProcedimientos', acConf('abreIfMaestro', ifProcedimientos, nuevo=True))
        }
    
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])
