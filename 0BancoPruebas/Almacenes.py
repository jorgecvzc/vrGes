'''
Created on 1 feb. 2019

@author: cortesj
'''
import configparser
from almacen.AlmBDCon import BDConMySQL, BDConPostgreSQL
from almacen.AlmXMLCon import XMLCon
from builtins import str

from sqlalchemy import func as f

class Almacen(object):
    '''
    Clase para la interconexión de un maestro con la base de datos
    '''    
    #----------------------------
    # Funciones estnadar de manejo de objetos
    #---    
    
    def __init__(self, ruta_ini):
        '''
        Constructor Almacen. El almacen dispondrá a información de tipo CONF (por defecto almacenada en XML), y de tipo INF (que se almacenará en BD)
        '''
        # Carga los archivos de configuracion que almacenara en memoria
        if (ruta_ini[-1] != '/'):
            ruta_ini = ruta_ini + '/'
        self.iniConfig = configparser.ConfigParser()
        self.iniConfig.read(ruta_ini+'config.ini')

        # Carga la variable Conf de acceso a estructuras y configuraciones
        iniXML = self.iniConfig["XML"]
        self.Def = XMLCon(ruta_ini+iniXML["Ruta"], iniXML["Indices"])
        
        # Carga las variables Inf de acceso a datos y ER de acceso a la estandarización de datos 
        iniBD = self.iniConfig["BD"]
        tipo_bd = iniBD["Motor"]
        bdcon = None
        if tipo_bd == 'MySQL':        
            bdcon = BDConMySQL(iniBD["Servidor"], iniBD["NombreBD"], iniBD["Usuario"], iniBD["Clave"])
        elif tipo_bd == 'postgresql':
            bdcon = BDConPostgreSQL(iniBD["Servidor"], iniBD["NombreBD"], iniBD["Usuario"], iniBD["Clave"])
        self.Inf = bdcon
        self.ER = self.Inf.er
        
    def __str__(self):
        return str(self.Def) + '\n' + str(self.Inf)
    
    #----------------------------
    # Funciones de consulta genericsa sobre MaestMaestros #---          

    def cargaRegistro(self, tabla, condiciones, orden=[], campos=['*']):
        '''
        Devuelve los campos solicitados del primer registro de una tabla del almacén que coincide con las condiciones dadas.
        '''
        return self.Inf.selecciona([tabla], {'condiciones': condiciones, 'campos': campos})[0]

    def cargaRegistros(self, tabla, condiciones, **kwargs):
        '''
        Devuelve los campos solicitados de una tabla del almacén que coincide con las condiciones dadas.
        '''
        kwargs['condiciones'] = condiciones
        return self.Inf.selecciona([tabla], **kwargs)
    
    def numId(self, m_arbol, tipo_busqueda, m_id=0):
        '''
        Devuelve el número de indice por su posicióon a partir de uno dado
        '''
        if len(m_arbol.id) > 1:
            raise "Error. La consulta de numId sólo se puede usar sobre indices unitarios"
        
        er = self.Inf.er
        if (tipo_busqueda == 'm'):
            consRegs = self.Inf.selecciona([m_arbol.almacen], campos=[er.Alias(er.Min(m_arbol.id[0]), 'id')], limite=1)[0]
        elif (tipo_busqueda == 'M'):
            consRegs = self.Inf.selecciona([m_arbol.almacen], campos=[er.Alias(er.Max(m_arbol.id[0]), 'id')], limite=1)[0]
        elif (tipo_busqueda == 's'):
            consRegs = self.Inf.selecciona([m_arbol.almacen], campos=[er.Alias(er.Min(m_arbol.id[0]), 'id')], condiciones = er.Mq(m_arbol.id[0], m_id), limite=1)[0]
        elif (tipo_busqueda == 'a'):
            consRegs = self.Inf.selecciona([m_arbol.almacen], campos=[er.Alias(er.Max(m_arbol.id[0]), 'id')], condiciones = er.mq(m_arbol.id[0], m_id), limite=1)[0]
            
        if consRegs:
            return(consRegs['id'])
        else:
            return -1

