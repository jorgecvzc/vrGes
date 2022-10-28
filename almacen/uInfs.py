'''
Created on 27 oct. 2022
@author: jorante

Clases para las funcionalidades internas de los diferentes Unidades de Información
'''

from sqlalchemy import orm

class UInf (object):
    
    def __init__ (self):
        self.etiqueta = 'Prueba'
        self._camposModif = []
        
    @orm.reconstructor
    def init_on_load(self):
        self.__init__ ()        
        
    def __setitem__(self, key, valor):
        setattr(self, key, valor)
        self._camposModif.append(valor)
                
    def __getitem__ (self, key):
        getattr(self, key)
        
    def getCamposModif(self):
        return self._camposModif