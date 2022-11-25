'''
Created on 14 ene. 2019

@author: cortesj
'''

class TunelSenyal(object):
    '''
    classdocs
    '''

    def __init__(self, nombre):
        '''
        Constructor
        '''
        self.nombre = nombre
        self._tunelHabilitado = 0
        self._senyalesApagadas = []
        self._tunel = None
        
    def asignaTunel(self, funcion):
        if funcion:
            self._tunel = funcion
        else:
            self._tunel = None
    
    def emiteSenyal (self, fuente, senyal, *args):
        # print(fuente, senyal, args)
        if self._tunelHabilitado and self._tunel:
            if not (tuple(fuente) in self._senyalesApagadas) or (('*', fuente[-1]) in self._senyalesApagadas) or ((fuente[0], '*') in self._senyalesApagadas):
                self._tunel(fuente, senyal, *args)

    def habilitaTunel(self):
        self._tunelHabilitado = 1

    def deshabilitaTunel(self):
        self._tunelHabilitado = 0
        
    def deshabilitaSenyal(self, fuente, senyal):
        if not (fuente, senyal) in self._senyalesApagadas: 
            self._senyalesApagadas.append((fuente, senyal))
        
    def habilitaSenyal(self, fuente, senyal):
        if (fuente, senyal) in self._senyalesApagadas:
            self._senyalesApagadas.remove((fuente, senyal))
        