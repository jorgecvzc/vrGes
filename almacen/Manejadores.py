'''
Created on 27 oct. 2022

@author: cortesj
'''
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import select, func, and_, or_, text, asc, desc
from sqlalchemy.orm import sessionmaker


from .tblsArticulos import *


class MnjUInfs (object):
    '''
    Clase para el manejo de maestros y almacenamientos, independientemente de la topología de estos últimos.
    '''
    def __init__ (self, session, **kwargs):

        '''  Constructor Manejador '''    
        self.session = session

    def __del__ (self):
        self.session.rollback()

    def nuevoMaestro (self, nombre_maestro):
        mst = eval(nombre_maestro+'()')
        self.session.add(mst)
        return mst
 
    def guardaCambios(self):
        return self.session.commit()
        

class MnjMaestros (MnjUInfs):
    
    ''' ------------------------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE LOS ÁRBOLES DE CONFIGURACIÓN
        ------------------------------------------------------------- ''' 
           
    def cargaMemoriaConfObjetos (self, **kwargs):
        for clase in kwargs.keys():
            for tipmst in kwargs[clase]:
                if not(tipmst in self.confArboles[clase]):
                    self.confArboles[clase][tipmst] = self.almacen.Def.cargaArbolDef(clase, tipmst)
        
    def borraMemoriaConfObjetos(self, clase, tipos_maestros):
        for tipmst in tipos_maestros:
            if (tipmst in self.confArbols[clase]):
                self.confArbols[clase].pop(tipmst)
    
    
    def arbolConf(self, clase, tipo):
        if tipo in self.confArboles[clase]:
            arbolConf = self.confArboles[clase][tipo]
        else:
            arbolConf = self.almacen.Def.cargaArbolDef(clase, tipo)
            self.confArboles[clase][tipo] = arbolConf
            
        return arbolConf

        
