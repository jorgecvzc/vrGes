'''
Created on 27 oct. 2022
@author: jorante

Clases para las funcionalidades internas de los diferentes Unidades de Información
'''

from sqlalchemy import orm
import pandas as pd


from Señales import TunelSenyal

class Maestro (object):
    
    def __init__ (self):
        self.etiqueta = ''
        self._camposModif = []

        self._tSenyales = [TunelSenyal(self.etiqueta), None] # Objeto con dos tuneles de señal. El primero el entrante para recibier señalesy el segundo el saliente para mandarlas.
        self._tSenyales[0].asignaTunel(self.trataSenyal)
        self._tSenyales[0].habilitaTunel()        
        
    @orm.reconstructor
    def init_on_load(self):
        self.__init__ ()        
        
    def setId(self, valor):
        self.id = valor
    def getId(self):
        if self.id:
            return self.id
        else:
            return None
    
    def __setitem__(self, key, valor):
        if valor != getattr(self, key):
            setattr(self, key, valor)
            self._camposModif.append(key)
                
    def __getitem__ (self, key):
        return getattr(self, key)

    def getTipoCampo(self, campo):        
        return ''
    
    def getCamposModif(self):
        return self._camposModif
    
    def vaciaCamposModif(self):
        self._camposModif = []
    
    def modificado(self):
        return len(self._camposModif)

    ''' ----->
     Funcion para la asignacion de del tunel de senyales salientes del objeto acutal, para la comunicación con otros objetos e interfaces.
    '''
    def asignaTunelSenyal(self, tunel_senyal):
        if tunel_senyal:
            if (isinstance(tunel_senyal, (TunelSenyal))):
                self._tSenyales[1] = tunel_senyal
            else:
                raise NameError('CampoLíneas->asignaTunelSenyal: la senyal ha de ser del tipo de la clase o superclase Senyal')
        else:
            self._tSenyales[1] = None
            
    ''' ----->
     Funciones para el tratamiento y emisión de senyales 
    '''

    def trataSenyal(self, fuente, senyal, *args):
        ''' trataSenyal tratará los datos de la senya si lo requiriera y la tramsmitirá al tunel de salida si éste está definido.
            Las senyales estarán formadas por los siguientes campos:
                fuente - indicador de quien emite la señal
                senyal - tipo de senyal emitida. Podrá tomar los siguientes valores:
                    mv: Modificación del valor de un campo o de una celda en campos de líneas
                    nf: nueva fila en los campos de líneas
                    bf: borra fila en los campos de líneas
                *args - Diferentes argumentos opcionales y específicos de la señal en curso
        '''      
        self.log.info('[' + self.getAlmacen() + '] ' + str(self.getEtiqueta()) + '->trataSenyal: ' + str(fuente) + ', ' + str(senyal) + ', ' + str(args))
        
        # Carga el campo a tratar
        fcampo = fuente[0]

        # Si no es una tupla se dará por supuesto que la fila será la 0
        if not isinstance(fcampo, tuple):
            campotrat = fcampo
            lineatrat = 0
        else:
            campotrat = fcampo[0]
            lineatrat = fcampo[1]
                    
        # Tratamiento para las señales de los campos de la Unidad de Información
        if (campotrat in self._camposConf.keys()):
            # Ejecuta las funciones dependientes si las hubiera
            if (senyal=='mv'):
                if (self._camposConf[campotrat].parametro('dependientes')):
                    self._procesaDependientes(lineatrat, campotrat)
    
            # Si es un campo el que emite la señal se añade a modificados
            if not (campotrat in self._camposModif):
                self._camposModif.append(campotrat)
                self._camposVal.at[0, '_modif'] = True
                    
        # Pasa la señal al siguiente receptor si lo hubiera
        if self._tSenyales[1]:
            self._tSenyales[1].emiteSenyal([self.getEtiqueta()]+fuente, senyal, *args)    
            
            
class ListaMaestro (list):
    def col(self, col):
        return [c[col] for c in self]


class Consulta (object):
    def __init__ (self, maestros, campos_busqueda, campos_resultado=['*']):
        self.maestros = maestros
        self.camposBusqueda = campos_busqueda # Contiene los campos por los que se puede buscar
        self.camposFiltro = {} # Contiene los datos por los que se buscará
        self.camposResultado = campos_resultado
        self.resultado =pd.DataFrame(columns=['id']+self.camposResultado)
        
    def __setitem__ (self, key, valor):
        if not valor:
            self.camposFiltro.pop(key, False)
        else:
            if key in self.camposBusqueda:
                self.camposFiltro[key] = valor
            else:
                raise NameError('uInfs.Consulta->ActualizaCampoBusqueda: El campo no es un campo de búsqueda.')
    
    def asignaResultados(self, pd):
        self.resultado = pd
        self.resultado.columns = self.camposResultado
             
    def lcol(self, col):
        return list(self.resultado.icol[:col])
    
    def __str__ (self):
        return '<cns: (Maestros: ' + str(self.maestros) + ' , Campos: '  + str(self.camposFiltro) + ')'
        
        
