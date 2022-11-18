#
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
#
from .Manejadores import MnjMaestros, MnjConsultas

class ControlUinfs (object):

    '''
    Clae de creacion y acceso a manejadores
    '''    
    def __init__(self, conf_conexion):
        '''
        Constructor ControlUinfs    
        '''
        self.bd = create_engine(conf_conexion["Motor"]+'://'+ 
                                conf_conexion["Usuario"]+':'+conf_conexion["Clave"]+'@'+
                                conf_conexion["Servidor"]+':5432/'+conf_conexion["NombreBD"], echo=False)
        
    def mnjMaestros(self):
        # Devuelve un Manejador de Maestros
        session = sessionmaker(bind=self.bd)
        return MnjMaestros(session())

    def mnjConsultas(self):
        # Devuelve un Manejador de Consultas
        return MnjConsultas(self.bd)
        