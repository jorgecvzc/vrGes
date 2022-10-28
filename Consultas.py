'''
Created on 05 mar. 2019

@author: cortesj

Modulo DefConsultas
    Contiene las clases necesarias para almacenar vistas de los datos contenidos en los almacenes. 
'''
import pandas as pd

class ConsultaY(object):
    '''
    Clase Consulta: clase madre para todo tipo de consultas
    '''    
    def __init__(self, tipo, etiqueta= None):
        # Inicializa los valores de la consulta
        self.__tipo = tipo
        self.__etiqueta = etiqueta
        self._campos = []  # Es la lista de campos con los que se podrá realizar la búsqueda. Podrán estar repetidos con diferentes operadores.  
        self._filtros = [] # Lista con cada uno de los operadores aplicados a cada campo
        self._valores = [] # Valores dados a los diferentes campos para realizar la búsqueda 
        self._resultado = pd.DataFrame() # Tabla donde se guardarán los resultados
        self._orden = [] # Lista con los campos que marcarán el orden de los registros resultantes

    def getTipo(self):
        return self.__tipo

    def getEtiqueta(self):
        return self.__etiqueta
        
    def _agregaFila(self, fila):
        self.valores.loc[len(self._datos)] = fila

    # ----------------------------
    #  Métodos especiales para asignar y recuperar valores. En la consulta __setitem__ y __getitem__ actuarán sobre estructuras direferentes:
    #   - 'Set': actuará actualizando un valor de los campos de búsqueda
    #   - 'Get': actuará devolviendo una columna de los valores de resultado 
    # ---
    
    def __getitem__(self, key):
        if (isinstance(key, int)): # Si la clave es un entero se devuelve una fila de daots
            return self._resultado.iloc(key)
        else: # En caso contrario se devuelve la columna de datos cuya cabecera coincida 
            return self._resultado[key]
    
    def __setitem__(self, clave, valor):
        if (isinstance(clave, int)):
            self._valores[clave] = valor
        else: # Canbia el valor del primer campo cuyo nombre coincida con clave
            self._valores[self._campos.index(clave)] = valor
    
    def actualizaFiltro(self, campos):  # Actualiza el filtro según un diccionario de campos:valores
        self._valores = [None]*(len(self._campos))
        for (campo, valor) in campos.items():
            self._valores[self._campos.index(campo)] = valor
    
    def getCamposBusq(self): # Devuelve una lista de tuplas con los campos, operadores y valores de la búsqueda que contengan algún valor 
        return [(self._campos[i], self._filtros[i], self._valores[i])  for i in range(len(self._campos)) if self._valores[i]]

    def nombresCamposBusq(self): # Devuelve el nombre de los campos de busqueda
        return self._campos
    
    def nombresCamposResult(self): # Devuelve el nombre de los campos resultado
        return list(self._resultado.columns.values)
    
    def operador(self, campo):
        return self._filtro(campo)
            
    def __str__(self):
        sres =  '{:15}:\t{:}\n'.format('Consulta Tipo', self.__tipo)
        sres +=  '{:15}:\t{:}\n'.format(' CamposBusq: ',  (", ".join([str(self._campos[campo]) + ': ' + str(self._valores[campo]) for campo in range(len(self._campos))])))
        sres +=  '{:15}:\t{:}\n'.format(' Operadores: ',  (", ".join([str(self._campos[campo]) + ': ' + str(self._filtros[campo]) for campo in range(len(self._campos))])))
        sres +=  '{:15}:\t{:}\n'.format(' Orden: ',  (", ".join([str(campo) for campo in self._orden])))
        sres += '{:15}:\t{:}'.format(' Resultado:' , '[')
        i = 1
        for fila in self._resultado.itertuples():
            sres += '\n\t\t '+'*LINEA '+str(i-1)+'* ['
            for campo in fila:
                sres += str(campo) + ", "
            sres += ']'
            i += 1 
            sres = sres[:-2]+ ']'
        sres += '\n\t\t]'        
        return sres
    
    
class ConsultaMaestro(ConsultaY):
    '''
    Clase de Consulta que devuelve una serie de daotos correspondientes a maestros de un tipo qeu cumplan las condiciones de búsqueda
    '''
    def __init__(self, tipo,  manejador=None):
        super().__init__(tipo, manejador)


class ConsultaMaestros(ConsultaY):
    def __init__(self, tipo,  manejador=None):
        super().__init__(tipo, manejador)

