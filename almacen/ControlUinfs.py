#
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#
from .Manejadores import MnjMaestros


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
        self.Session = sessionmaker(bind=self.bd)

    def mnjMaestros(self):
        # Establece el almacen por defecto
        return MnjMaestros(self.Session())


