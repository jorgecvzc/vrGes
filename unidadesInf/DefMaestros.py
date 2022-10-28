'''
Created on 15 ene. 2019

@author: cortesj
Modulo DefMaestros
    El módulo DefMaestros contiene las clases padre para el trabajo con objetos de tipo maestro que representan los elelmentos reales que debe procesar la aplicación. 
'''

from .UnidadesInf import tipoUInf, UnidadInf, Campo
from Señales import TunelSenyal
import pandas as pd

import log

           
class CampoLineas(UnidadInf):
    '''
    Clase especial de campo donde se almacena un conjuto de datos de forma variable/linea referenciado por un camopo de un objeto tipo Maestro.
        No tendrá indice para el objeto ya que sus objetos siempre irán asociadas a un Maestro con indice.
        Se comporta como una matriz donde las columnas representan diferentes variables y las filas un conjunto único con un valor por variable.
        Cada fila tendrá un índice numérico único que la diferenciara del resto y cada columna un nombre de variable.
    '''

    def __init__(self, almacen, manejador=None):
        super().__init__(tipoUInf.CAMPO_LINEAS, almacen, manejador=None)
              
    ''' ----->
      Métodos de manejo de los valores individuales
      - Si se pasa un texto manejan los datos por variable.
      - Si se pasa un entero manejan cada una de las filas de datos. 
    '''
    def getValor (self, campo1, campo2):
        if isinstance(campo1, str):
            fil = campo2
            col = campo1
        else:
            fil = campo1
            col = campo2
        return super().getValor(fil, col)

    def setValor (self, campo1, campo2, valor):
        if isinstance(campo1, str):
            fil = campo2
            col = campo1
        elif isinstance(campo2, str):
            fil = campo1
            col = campo2
        else:
            fil = campo1
            col = list(self._camposConf.keys())[campo2]
        super().setValor(fil, col, valor)
                     
    ''' ----->
     Fucniones de representacion 
    '''
    def __str__(self):
        sres = ''
        for parcv in self.__dict__.items():
            if (parcv[0]=='_camposConf'):
                sres = sres + '\n_Conf Campos:\t'
                i = 1
                for key in parcv[1].keys():
                    sres += '{:23}  '.format(str(key))
                sres += '\n\t\t '
                srt2 = ''
                srt3 = ['','','','','','','']
                for fila in parcv[1].values():
                    srt = str(fila).split(' : [')
                    sres += '{:23}  '.format(srt[0])
                    srt2 = '{:23}  '.format(srt[1][:-1])
                    it = 0
                    for srt in srt2.split(';'):
                        srt3[it] += '{:23.23}  '.format(srt.replace(' ', '').split(':')[0][0:3]+'-'+srt.split(':')[1])
                        it += 1
                    for j in range(it, len(srt3)-1):
                        srt3[j] += '{:23.23}  '.format(' ')
                for srt in srt3:
                    if srt != '':
                        sres += '\n\t\t ' + srt
                i += 1 
                sres = sres[:-2]
            
            elif (parcv[0] == '_camposVal'):
                sres = sres + '\n_camposVal:\t['
                i = 1
                for fila in parcv[1].itertuples():
                    sres += '\n\t\t '+'*LINEA '+str(i-1)+'* [{}, {} - '.format(str(fila[1]), str(fila[2]))  # Primero se pone el Id y si está modificada la fila y luego los valores
                    for campo in self._camposConf.keys():
                        if (isinstance(getattr(fila, campo), (Maestro, CampoLineas))):
                            sres += '{'+ '\n\t\t   '.join(str(getattr(fila, campo)).splitlines()) + "\n\t\t  }, " 
                        else:
                            sres += str(getattr(fila, campo)) + ", "
                    i += 1 
                    sres = sres[:-2]+ ']'
                sres += '\n\t\t]'
            else:
                sres += '\n{}:\t{}'.format(parcv[0], parcv[1]) 
        return '\n\t'.join([line for line in sres.split('\n')])


''' ---------------------------------
    DEFINICIONES DE LAS CLASE MAESTRO
    ---------------------------------'''
   
class Maestro(UnidadInf):
    '''
    Clase madre de los maestros. Almacena información de cada uno de los objetos de gestión de la aplicación.
       Cada objeto tendrá un índice proporcionado por los manejadores que será único o estará vacío y una etiqueta que identificara el tipo de objeto.
       
       Variables definitorias: Los maestros constan de un identifiador entero  __id interno que junto a campo tipo cadena  __etiqueta forman una definición única 
       y global de cada objeto.
       El identificador  __id es controlado por los manejadores a través de las funciones setId y getId. El campo __etiqueta lo crea el Controlador de     s y se 
       puede recuperar con getTipo. Un objeto maestro no puede cambiar su Etiqueta pero sí su Identificador.   
       
       Variables de campo: Es un conjunto de variables de tipo Campo encerradas en la variable interna de diccionario _camposConf que define las características del 
       elemento real y cuyos valores se almacenaran en la primera fila de la variable _camposVal siendo accedidas mediante las funciones mágicas __getitem__ y __setitem__
       A Variables de Campo se asocia la variable _campoosModif que indica los campos modificados últimamente.
       
    '''
        
    ''' -----> 
        Funciones específicas de la clase Maestro
    '''      
    def __init__(self, almacen, manejador=None):
        super().__init__(tipoUInf.MAESTRO, almacen, manejador)
        # Crea una nueva vila que será la única y contendrá los campos del maestro

        #self.nuevaFila() # Crea la fila 0 donde se almacenarán los campos del Maestro

  
    ''' ---->
        Funciones de acceso al valor de los campos
    '''
    def __getitem__(self, campo):
        return(super().getValor(0, campo))
    
    def __setitem__(self, campo, valor):
        super().setValor(0, campo, valor)


    ''' ---->
        Función para el tratamiento de senyales
    '''
    def trataSenyal(self, fuente, senyal, *args):
        # Antes de tratar la señal habrá que quitar el número de fila si se trata de un campo directo
        if isinstance(fuente[0], tuple) and (fuente[0][0] in self._camposConf.keys()):  
            fuente[0] = fuente[0][0]
        super().trataSenyal(fuente, senyal, *args)

            
    '''' ----->
     Función de manejo de los campos informativos del objeto
    '''
    def _nuevoCampo(self, nombre_campo, tipo, **kwargs):
        # En el caso de los maestros al crear un nuevo campo se le podrá indicar que inicie su valor a un dato dado
        if (nombre_campo == 'id'):
            raise NameError("Maestro->nuvoCampo: Nombre de campo Id reservado.")
        
        valor = valorDefecto[tipo]
        if ('valor' in kwargs.keys()):
            valor = kwargs.pop('valor')
        super()._nuevoCampo(nombre_campo, tipo, **kwargs)
        self._camposVal.at[0, nombre_campo] = valor
   
    def _cargaValorCampo(self, nombre_campo, valor):
        '''Cambbia el valor del campo sin ejecutar ningún tipo de función o dependencia existente'''
        super()._cargaValorCampo(0, nombre_campo, valor)
        
    
    '''----->
     Funciones de representación
    '''
    def __str__(self):
        sres =  '{:20}:\t{:}'.format('_UINF__TIPO: ', self.getTipo()) + '\n'
        sres =  '{:20}:\t{:}'.format('_UINF__ALMACEN: ', self.getAlmacen()) + '\n'
        for parcv in self.__dict__.items():
            if (parcv[0] in ['_Maestro__tipo', '_Maestro__almacen']):
                pass 
            elif (parcv[0] == '_camposConf'):
                sres += '\n{:20}:{:}'.format(parcv[0],'\t{')
                for cCampoLin in parcv[1].items():
                    if not isinstance(cCampoLin[1].valor, (Maestro, CampoLineas)):
                        sres += '\n\t{:}: {:}'.format(cCampoLin[0], '\t'+str(cCampoLin[1]))
                    else:
                        sres += '\n\t{:}: {}{:}{}'.format(cCampoLin[0], '{','\t   '.join(map(lambda s: s+'\n', str(cCampoLin[1]).splitlines())),'\t\t}')
                sres += '\n}'
            elif (parcv[0] == '_camposVal'):
                sres += '\n{:20}:{:}'.format(parcv[0],'\t{')
                for nCampo in self._camposConf.keys():
                    if not isinstance(self._camposVal.at[0, nCampo], (Maestro, CampoLineas)):
                        sres += '\n\t{:}: {:}'.format(nCampo, '\t'+str(self._camposVal.at[0, nCampo]))
                    else:
                        sres += '\n\t{:}: {}{:}{}'.format(nCampo, '{','\t   '.join(map(lambda s: s+'\n', str(self._camposVal.at[0, nCampo]).splitlines())),'\t\t}')
                sres += '\n}'
            else:
                sres += '\n{:20}:\t{:}'.format(parcv[0], parcv[1]) 
        return sres        
    
    def __sizeof__(self):
        from sys import getsizeof
        total = 56
        total += getsizeof(self.__tipo)
        total += getsizeof(self.__etiqueta) 
        total += getsizeof(self._campos)
        total += getsizeof(self._tiposCampos)
        total += getsizeof(self._camposModif)
        for i in range(len(self._camposModif)):
            total += getsizeof(self._camposModif[i])
        return total
    
    
''' ----------------------------------
    DEFINICIONES DE LAS CLASE CONSULTA
    ----------------------------------'''

class ConsultaMaestro(UnidadInf):
    def __init__(self, almacen, manejador=None):
        super().__init__(tipoUInf.CONS_MAESTRO, almacen, manejador)
        # Crea una nueva vila que será la única y contendrá los campos del maestro

        self.setId((0,))
        self.setEtiqueta('consMst')
        self.camposConsulta = {}
        
    ''' ---->
        Funciones de acceso al valor de los campos
    '''
    def __setitem__(self, campo, valor):
        self.camposConsulta[campo] = valor
        self._camposModif.append(campo)

    def __getitem__(self, campo):
        return self.camposConsulta[campo]
        
    def resultado(self, key):
        if key == 'id':
            key = '_id'
        return super().__getitem__(key)     
        
              
    '''----->
     Funciones de representación
    '''
    def __str__(self):
        sres =  '{:20}:\t{:}'.format('_CONS_MAESTRO__TIPO: ', self.getTipo()) + '\n'
        for parcv in self.__dict__.items():
            if (parcv[0] == '_UInf__tipo'):
                pass 
            elif (parcv[0] == '_camposConf'):
                sres += '\n{:20}:{:}'.format(parcv[0],'\t{')
                for cCampoLin in parcv[1].items():
                    if not isinstance(cCampoLin[1].valor, (Maestro, CampoLineas)):
                        sres += '\n\t{:}: {:}'.format(cCampoLin[0], '\t'+str(cCampoLin[1]))
                    else:
                        sres += '\n\t{:}: {}{:}{}'.format(cCampoLin[0], '{','\t   '.join(map(lambda s: s+'\n', str(cCampoLin[1]).splitlines())),'\t\t}')
                sres += '\n}'
            elif (parcv[0] == '_camposVal'):
                sres = sres + '\n_camposVal:\t['
                i = 1
                for fila in parcv[1].itertuples():
                    sres += '\n\t\t '+'*LINEA '+str(i-1)+'* [{}, {} - '.format(str(fila[1]), str(fila[2]))  # Primero se pone el Id y si está modificada la fila y luego los valores
                    for campo in self._camposConf.keys():
                        if (isinstance(getattr(fila, campo), (Maestro, CampoLineas))):
                            sres += '{'+ '\n\t\t   '.join(str(getattr(fila, campo)).splitlines()) + "\n\t\t  }, " 
                        else:
                            sres += str(getattr(fila, campo)) + ", "
                    i += 1 
                    sres = sres[:-2]+ ']'
                sres += '\n\t\t]'
            else:
                sres += '\n{:20}:\t{:}'.format(parcv[0], parcv[1]) 
        return sres        
    
    
''' ------------------------------------------
    DEFINICIONES DE LAS CLASE BUSQUEDA-MAESTRO
    ------------------------------------------'''
   
class BusquedaMaestros(UnidadInf):
    '''
    Clase que contendrá datos para relizar una búsqueda los maestros de un tipo dado.
    Se basará en un maestro con los datos de entrada limitados y devolverá una lista de campos de cada maestro que cumpla con los requisitos.
    '''
    def __init__(self, maestro, campos_busq, campos_result, orden=None):
        self.mnt = maestro
        self.cBusqueda = campos_busq
        self.cResultado = campos_result
        self.cOrden = orden
        
    
''' ---------------
    ZONA DE PRUEBAS
    ---------------'''
                
if __name__ == "__main__":
    from Control import Control
    cm = Control('.')

    mnj = cm.nuevoManejador(Maestros=['Articulo'])
    mst = mnj.nuevoMaestro('Articulo')
    mst = mnj.cargaMaestro('Articulo', mst_ref=1)
    mst['manufacturado'] = 1
    print('---->')
    print(mst)
    print('---->')

    
 


    
