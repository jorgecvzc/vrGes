'''
Created on 19 dic. 2018

@author: cortesj
'''
from PyQt5 import QtWidgets, uic, QtCore
from Interfaz.Interfaces import ifMaestro
from Interfaz.ifTrabajos import ifProcedimientos

class ifProveedores(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro = "Personas.Proveedor"
    Interfaz = "Personas/wdProveedores"
    
    Campos = {
        'leRef': ('ifCadena', 'ref'),
        'leNombre': ('ifCadena', 'nombre'),
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
        'leRef': ('ref',),
        'leNombre': ('nombre',),
        'lwProcedimientos': ('procedimientos', 'nombre',)
    }    
    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])

    Botones = {
        'pbAgregaProc': (ifProcedimientos,)
        }

