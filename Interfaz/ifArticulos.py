'''
Created on 19 dic. 2018

@author: cortesj
'''
from PyQt5 import QtWidgets, uic, QtCore
from Interfaz.Interfaces import ifMaestro
from Interfaz.Campos import cConf

class ifArticulos(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Trabajos
    '''
    TipoMaestro="Articulos.Articulo"
    Interfaz = "Articulos/wdArticulos"

    ListasMst = {
        'lProveedores': ('Articulos.Proveedor', ['id', 'nombre'])
    }       

    Campos = {
        'ref': ('ifCadena', 'leRef'),
        'nombre': ('ifCadena', 'leNombre'),
        'descripcion': ('ifCadena', 'leDescripcion'),
        'proveedor': ('ifRefListaD', 'leProveedor', 'cbProveedor', 'lProveedores'),
        'observaciones': ('ifTexto', 'ptObs'),
        'manufacturado': ('ifVerificacion', 'chbManufacturado', ['tbEscandallo']),
        'numVariantes': ('ifCadena', 'leNumVariantes')
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])    
     

class ifPosiciones(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase Posiciones
    '''
    TipoMaestro="Articulos.Posicion"
    Interfaz = "Articulos/wdPosiciones"

    Campos = {
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre'),
    }
    

class ifVariantesArt(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro="Articulos.Variante"
    Interfaz = "Articulos/wdVariantes"
    
    linModificador = {
        'Ref': ('ifCadena', 'ref'),
        'Nombre': ('ifCadena', 'nombre'),
    }
    
    Campos = {
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre'),
        'twModificadores': cConf('modificadores', linModificador,)
    }

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])
    
    
class ifModificadoresArt(ifMaestro):
    '''
    Clase para el manejo de la interfaz de la clase ModificadoresArt
    '''
    TipoMaestro = "Articulos.Modificador"
    Interfaz = "Articulos/wdModificadores"
 
    ListasMst = {
        'lVariantesArt': ('Articulos.Variante', ['nombre', 'ref'])
    }   
    
    Campos = {
        'leRef': cConf('ref'),
        'leNombre': cConf('nombre'),
        'leVariante': cConf('variante', 'ref', 'lVariantesArt'),
        'cbVariante': cConf('variante', 'nombre', 'lVariantesArt')
    }    

    BusquedaMaestro = (['ref', 'nombre'], ['ref', 'nombre'])


