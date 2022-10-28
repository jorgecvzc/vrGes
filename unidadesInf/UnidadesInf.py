from enum import Enum, unique

from Señales import TunelSenyal
import pandas as pd

import log


''' ------------------------
    DEFINICIÓN DE CONSTANTES
    ------------------------'''
    
@unique
class tipoUInf(Enum):
    MAESTRO = 0
    CAMPO_LINEAS = 1
    CONS_MAESTRO = 2
    CONS_RANGO_MSTS = 3

valorDefecto = {'z': 0, 'r':0.0, 't':'', 'e':(None,), 'l':None, 'b':False, 'h':False, 'a': (None,), 'o': 0}
    
''' -----------------------------------
    DEFINICIONES DE LAS CLASES DE CAMPO
    -----------------------------------'''
   


class Campo(object):
    ''' Clase que almacena valor y características de cada campo del maestro ''' 
    def __init__(self, tipo, **kwargs):
        
        if ('valor' in kwargs.items()):
            self.valor = kwargs.pop('valor')
        else:
            self.valor = valorDefecto[tipo]
            
        self.tipo = tipo  # Almacena información acerca de los tipos de cada campo
        self.dependientes = [] # Lista con los nombres de campos dependientes del actual, cuya modificación implicará la actualización de los otros a través de fórmulas. Se define a vacía si no tiene dependientes para facilitar la progarmación del rastreo de los mismos.
        
        for (llave, valor) in kwargs.items():
            # Se crean los diferentes parámetros del campo. Pueden ser del tipo:
            #  objeto:  Nombre del objeto referenciados por los campos de tipo "e"ç
            #  busqueda: Campos de busqueda de un maestro externo. Se buscará el primero que empieze por el valor indicado independientemente de las mayúsculas o minúsculas
            #  dependientes
            #  habilitados:Indica si el campo habilita o deshabilita un conjunto de campos
            #  formula: Indica si el campo tiene una formula asociada de cálculo en el maestro
            
            self.setParametro(llave, valor)    
    
    ''' Indica si existe o no un parámetro '''
    def parametro(self, nombre):
        return hasattr(self, nombre) and self.__dict__[nombre]
    
    ''' Modifica un parámetro y si no existe lo crea '''
    def setParametro(self, nombre, valor):
        self.__dict__[nombre] = valor    
    
    def __str__(self):
        strr = str(self.tipo) + ' - '
        if self.tipo == "t":
            strr += '"' + str(self.valor) + '" : ['
        else:
            strr += str(self.valor) + ' : ['
        for parcv in self.__dict__.items():
            if parcv[0] not in ['valor', 'tipo']:
                strr +=  parcv[0] + ': '+str(parcv[1])+'; '
        if strr[-1] != '[':
            strr = strr[:-2]
        strr += ']' 
        return strr
    
    def __sizeof__(self):
        tam= super().__sizeof__() 
        for (n, v) in self.__dict__.items():
            tam += n.__sizeof__() + v.__sizeof__()
        return tam

''' ----------------------------------------------------------
    DEFINICIONES DE LAS CLASE DE OBJETOS CON INFORMACIÓN MADRE
    ---------------------------------------------------------- '''
   
class UnidadInf(object):
    '''
    Clase representativa de todas las entidades con información.
    '''
   
    def __init__(self, tipo, almacen, manejador):
        self._mnj = manejador        
        self.__id = (None,) # Tupla que identifica a la unidad de información del resto de unidades. Tendrá el mismo prefijo entre unidades madre y sus componentes directos
        self.__camposId = (None,) # Tupla con los nombres de los campos que formaran el identificador        
        self.log = log.ini_logger(__name__)

        self.__tipo = tipo # Tipo de objeto que representa la Unidad de Inf
        self.__almacen = almacen # Tipo de objeto que representa la Unidad de Inf
        self.__etiqueta = '' # Etiqueta de uso abierto. Se podrá utilizar para diferenciar dos Unidades del mismo tipo.
        self._camposConf = {} # Diccionario que contendrá las definiciones de los campos
        self._camposVal = self._mnj.almConf.almacenUInf(almacen)
 
        self._camposModif = [] # Lista de campos modificados. Los cargados de almacen al iniciar una instancia de  ObjetoInf no se considerarán modificados
        self._idFilasBorradas = [] # Lista con los ids de las filas borradas para manejo del Manejador
        
        self._filtrado = None # Indica si el maestro solo contiene un conjunto de campos de todos los que le definen
        self._camposInhab = [] # Lista con campos inhabilitados y que por tanto deben ser inaccesibles.

        self._formulas = {} # Diccionarios que contiene las formulas de los campos que se calculan automáticamente a partir de otros campos.
        
        self._tSenyales = [TunelSenyal(tipo), None] # Objeto con dos tuneles de señal. El primero el entrante para recibier señalesy el segundo el saliente para mandarlas.
        self._tSenyales[0].asignaTunel(self.trataSenyal)
        self._tSenyales[0].habilitaTunel()

    
    '''
    Funciones v2.0
    '''
    def CargaDatos(self):
        self._camposVal = self._mnj.almInf.cargaRegistrosUInf(self)
        
    def GuardaDatos(self):
        self._mnj.almInf.session.commit()


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

    def deshabilitaTunelSalida(self):
        if self._tSenyales[1]:
            self._tSenyales[1].deshabilitaTunel()
    
    def habilitaTunelSalida(self):
        if self._tSenyales[1]:
            self._tSenyales[1].habilitaTunel()

    ''' ----->
     Funciones de consulta de las variables privadas y sus caractetrísticas
    '''
    def getTipo(self):
        return self.__tipo    

    def getAlmacen(self):
        return self.__almacen    

    ''' ----->
      Funciones de manipulación de la etiqueta
    '''
    def setEtiqueta(self, etiqueta):
        self.__etiqueta = etiqueta
    
    def getEtiqueta(self):
        return self.__etiqueta    

    ''' ----->
        Funciones de manejo el identificador único 
    '''
     
    def setId(self, valor):
        ''' Asigna la tupla única identificativa del objeto '''
        if type(valor) is tuple:
            self.__id = valor
        else:
            self.__id = (valor,)
        if not('id' in self._camposModif):
            self._camposModif.append('id')             

    def getId(self):
        '''  Devuelve la tupla única identificativa'''
        if self.__id == (None,):
            return ()
        else:
            return self.__id
        
    def getIdNum(self):
        ''' Devuelve el número que identifica el objeto dentro de su grupo '''
        return self.__id[-1]
     
    ''' ----->
      Funciones de manipulación de los identificadores de fila
    '''
   
    def _setIdFila(self, linea, idl):
        self._camposVal.at[linea,'_id'] = idl

    def _getIdFila(self, linea):
        return self._camposVal.at[linea,'_id']        

    def _getFilaId(self, idl):
        ''' Devuelve el número de fila correspondiente a un Id de fila dado '''
        linId = self._camposVal[self._camposVal['_id'] == idl].index
        return linId[0]
    
    ''' ----->
     Fucniones de creación, modificación y elimanción de campos y filas de uso exclusivo por los manejadores y el maestro propio
    '''    
    def _asignaCamposId (self, campos):
        self.__camposId = campos
    
    def _getCamposId (self):
        return self.__camposId
        
    def _nuevoCampo(self, nombre_campo, tipo, **kwargs):
        if not (nombre_campo in self._camposConf):
            # Trata los posibles parámetros con procedimientos especiales
            llaves = kwargs.keys()
            if ('expresion' in llaves):
                self._nuevaFormula(nombre_campo, kwargs['expresion'])
                kwargs['formula'] = True
                
            # Caga el nuevo campo
            self._camposConf[nombre_campo] = Campo(tipo, **kwargs)
            self._camposVal[nombre_campo] = None
                    
    def _modifCampo(self, nombre_campo, nombre_parametro, valor):
        '''Modifica o crea algún parámetro del campo dado'''
        if nombre_campo in self._camposConf.keys():
            self._camposConf[nombre_campo].setParametro(nombre_parametro, valor)
        else:
            raise NameError('Maestro->_modifCampo: campo "' + nombre_campo +  '" no existe')
        
    def _borraCampo(self, nombre_campo):
        if nombre_campo in self._camposConf.keys():
            self._camposConf.drop(columns=[nombre_campo], inplace=True)
            self._camposVal.drop(columns=nombre_campo, inplace=True)
        else:
            raise NameError("ManeajdorLineas->borraCampo: nombre de campo no existe")
        
        
    ''' ----->
     Funciones para la asignación de nuevas formulas y búsquedas
    '''
       
    def _nuevaFormula(self, campo_resultado, formula):
        
        trataFormula = formula.partition('[')[2]
        while trataFormula > '':
            datos = trataFormula.partition(']')
            campo = datos[0]
            if '>' in campo: campo = campo.partition('>')[0]
            if not campo_resultado in self._camposConf[campo].dependientes:
                self._camposConf[campo].dependientes.append(campo_resultado)            
                
            trataFormula = datos[2].partition('[')[2]
        self._formulas[campo_resultado] = lambda i, self=self: eval(formula.replace(']', '"]').replace('[', 'self.getValor(i, "').replace('>', '")["'))
    
    def _nuevaFilaValores(self, valores, orden=-1):
        orden = self.nuevaFila(orden)
        for campo in valores.keys():
            if valores[campo] != None:
                if self._camposConf[campo]['tipo'] == 'z':
                    self._camposVal.at[orden, campo] = int(valores[campo])
                else:
                    self._camposVal.at[orden, campo] = valores[campo]
            elif campo in self._formulas:
                self._camposVal.at[orden, campo] = self._formulas[campo](orden)
        return orden

    ''' ----->
      Funciones de ayuda al tratamiento de valores de los campos
    '''
   
    def _cargaValorCampo (self, fila, nombre_campo, valor):
        '''Cambbia el valor del campo sin ejecutar ningún tipo de función o dependencia existente'''
        self._camposVal.at[fila, nombre_campo] = valor
     
    def _procesaBusqueda(self, fila, nombre_campo, valor):
        ''' Se procesará la busqueda asociada a un campo dependiendo si lo que ha de buscar es un campo de tipo:
            -e: un maestro externo
            -l: que siempre representará a un campo de líneas completemntario
        '''
        campo = self._camposConf[nombre_campo]
        
        if campo.busqueda[0] in self._camposInhab: # Si el campo destino está deshabilitado no se hace nada
            return None

        insertarDependiente = False                   

        if ((self._camposConf[campo.busqueda[0]].tipo == 'e') and (self._mnj)):
            if nombre_campo in self._camposConf[campo.busqueda[0]].dependientes:
                # Se saca el campo de dependientes para que no entre en un bucle trataSenyal()
                self._camposConf[campo.busqueda[0]].dependientes.remove(nombre_campo)
                insertarDependiente = True
        
            # Se realiza el proceso de búsqueda cargando el maestro resultante, si lo hubiera, con los mismos campos que el cargado
            if valor:
                mst_dest = (self.getValor(fila, campo.busqueda[0]))
                camposBusqueda = {campo.busqueda[1]: valor}
                if mst_dest and mst_dest._filtrado:
                    mst = self._mnj.cargaMaestro(self._camposConf[campo.busqueda[0]].objeto, cmp_busq=camposBusqueda, condicion_busq='pi', lista_campos=list(mst_dest._campos.keys()))
                else:
                    mst = self._mnj.cargaMaestro(self._camposConf[campo.busqueda[0]].objeto, cmp_busq=camposBusqueda, condicion_busq='pi')
                if isinstance(mst_dest, Maestro) and mst_dest.getId() != mst.getId(): 
                    self.setValor(fila, campo.busqueda[0], mst)
        elif ((self._camposConf[campo.busqueda[0]].tipo == 'l') and (self._mnj)):
            # Carga el árbol de definiciones del maestro
            m_arbol = self._mnj.arbolConf('Maestros', self.__tipo)
            if isinstance(valor, tuMaestros):
                ids = (self.getId(), valor)
            else:
                ids = (self.getId(), (valor,))
            if (None,) in ids:
                mst = self._mnj.nuevoCampoWLineas(campo.busqueda[0], m_arbol[nombre_campo].valor, m_arbol[campo.busqueda[0]].valor, t_senyal=self._tSenyales[0])
            else:
                # mst = self.cargaCampoWLineas(variable, uinf_conf[variable].valor, uinf_conf[enlaceExt].valor, lidw, nivel_ext=nivel_ext, t_senyal=uinf._tSenyales[0])
                mst = self._mnj.cargaCampoWLineas(campo.busqueda[0], m_arbol[campo.busqueda[0]].valor, m_arbol[nombre_campo].valor, ids, t_senyal=self._tSenyales[0])
            self.setValor(fila, campo.busqueda[0], mst)
               
        if insertarDependiente:
            # Se vuelve a introducir el campo de busqueda en dependientes
            campo.dependientes.append(nombre_campo)
            
    def _procesaDependientes(self, fila, nombre_campo):            
        ''' Se procesarán los dependientes de un campo actualizando sus valores según las fórmulas creadas
        '''
        for campo in self._camposConf[nombre_campo].dependientes:
            busq = None
            # Si el campo dependiente también es de búsqueda se saca para que al cambiarlo no haga una búsqueda inútil
            if (self._camposConf[campo].parametro('busqueda')) and (self._camposConf[campo].busqueda[0] == nombre_campo):
                busq = self._camposConf[campo].busqueda
                self._camposConf[campo].busqueda = None
            A = self._formulas[campo](fila)
            self.setValor(fila, campo, A)
            if busq:
                self._camposConf[campo].busqueda = busq
        
                    
    def _procesaHabilitados(self, fila, nombre_campo, valor):
        ''' Habilita o deshabilita los campos incluidos en el valor "habilitados" según "valor" '''
        campo = self._camposConf[nombre_campo]
        # Si el campo es un campo habilitador se habilitan o deshabilitan los campos dependientes
        if valor: # Habilita los campos borrándolos de la lista _camposInhab
            for campoDep in campo.habilitados:
                if (campoDep in self._camposInhab):                        
                    self._camposInhab.remove(campoDep) 
                # Si el campo habilitado no tiene valor se le crea
                if not self._camposVal.at[fila, campoDep]: # Si es un adjunto el valor por defecto será el adjunto con sus campos ya creados
                    m_arbol = self._mnj.arbolConf('Maestros', self.__tipo)
                    self._camposVal.at[fila, Maestrossqueda[0]] = self.nuevoMaestro(m_arbol[nombre_campo].valor.almacen, nombre_campo, t_senyal=self._tSenyales[0])
        else: # InHabilita los campos añadiéndolos de la lista _camposInhab
            for campoDep in campo.habilitados:
                if not(campoDep in self._camposInhab): 
                    self._camposInhab.append(campoDep)
       
    ''' ---->
      Métodos especiales 'dict' de tratamiento de valores. 
       - Si se pasa un texto manejan los datos por variable.
       - Si se pasa un entero manejan cada una de las filas de datos. 
    '''
    
    def __getitem__(self, key):
        valores = []
        if (isinstance(key, int)):
            valores = self._camposVal.loc[key][2:] # Se devuelve un diccionario con los valores, exceptuando los campos _id y _modif
        elif (isinstance(key, str)):
            valores = self._camposVal[key]
        return valores
    
    def __setitem__(self, key, valores):
    # Si se va a actualizar una columna key será un string y valores un lista
    # En caso de una fila key será un entero y valores un diccionario de pares {nombres de columna : valor}
        if (isinstance(key, str) and isinstance(valores, list)):
            if (len(valores) != len(self._camposConf.axes[1])):
                raise NameError('CampoLíneas->__setitem__: No coincide el número de valores con las filas')
            for i in range(list(self._camposConf.keys())):
                self.setValor(key, i, valores[i])
            
        elif (isinstance(key, int)):
            if not ((key>=0) and (key<len(self._camposVal))):
                raise NameError('CampoLíneas->__setitem__: Índice key fuera de rango')
            #self._camposVal.loc[key] = [self._camposVal.loc[key]['_id'], True]+list(x.valor for x in self._camposConf.values())
            if  isinstance(valores, dict):
                for campo in valores.keys():
                    self.setValor(key, campo, valores[campo])
            elif isinstance(valores, list):
                for campo in range(len(valores)):
                    self.setValor(key, campo, valores[campo])
                
        else:
            raise NameError('CampoLíneas->__setitem__: Tipos de parámetros erróneos %s, %s' % (key, valores))

    ''' ----->
      Métodos de manejo de los valores
    '''
        
    def getValor (self, fila, campo):
        fil = fila
        col = campo
          
        if isinstance(self._camposVal.loc[fil][col], tuple) and (self._camposConf[col].tipo == 'e') and self._mnj:
            idkey = self._camposVal.loc[fil][col]
            mste = self._mnj.nuevoMaestro(self._camposConf[col].objeto, eitqueta=(col, fil))
            if (not None in idkey):
                self._camposVal[col] = self._camposVal[col].astype('object')
                mste.setId(idkey)
                self._camposVal.at[fil, col] = self._mnj.cargaMaestro(mste, etiqueta=(col, fil))
            
            self._camposVal.at[fil, col] = mste 
            self._camposVal.at[fil, col].asignaTunelSenyal(self._tSenyales[0])

        if self._camposVal.notnull().loc[fil][col]:
            return self._camposVal.loc[fil][col]
        else:
            return None
    
    def setValor (self, fila, nom_campo, valor):
        # Si el campo está deshabilitado no se hace nada. A no ser que sea un campo de tipo Adjunto, cuyo comportamiento es inverso:
        #  Los campos de tipo 'a" cuando están deshabilitados se pueden cambiar pero no acceder. Esto se hace para que el manejador siempre lo cargue ya que no 
        #  puede ser de tipo None
        if (nom_campo in self._camposInhab) and (self._camposConf[nom_campo].tipo != 'a'):
            return False

        fil = fila
        col = nom_campo
  
        # Se actualiza el valor en la tabla de valores
        setattr(self._camposVal, col, valor)
        self._camposModif += [col]
        '''      
        # Si el valor es el mismo que el que contiene el campo no se hace nada
        if (valor == self._camposVal.at[fil, col]):
            return None
        
        if self._camposConf[col].tipo == 'z':
            valor = int(valor)
        
        # Si el valor nuevo es igual al del campo no se hace nada. Ahorro computacional y rotura de entrada en bucles por campos de busqueda y formula        
        if (len(self._camposVal) > 0) and (self._camposVal.at[fil, col] == valor):
            return
        
        if (self._camposConf[col].tipo == 'e'):
            if isinstance(valor, int):
                self._camposVal[col] = self._camposVal[col].astype('object')
                valor = (valor,)
            elif (type(valor) is tuple):
                self._camposVal[col] = self._camposVal[col].astype('object')
            elif valor and not isinstance(valor, Maestro):
                raise NameError(self.__tipo+'->setValor ['+col+']: El tipo de una variable externa ha de ser un indice o un Maestro.')
    

#        self._camposVal.at[fil, col] = valor
#        self._camposVal.loc[fil, '_modif'] = True
        if not col in self._camposModif:
            self._camposModif += [col]

        # Si tiene busqueda asignada se procesa
        if self._camposConf[col].parametro("busqueda"):
            self._procesaBusqueda(fil, col, valor)

        # Si es un campo habilitador se procesan los habilitados
                           
        if self._camposConf[col].parametro("habilitados"):
            self._procesaHabilitados(fil, col, valor)
                                    
        self.trataSenyal([(col, fil)], 'mv', valor)
        '''
        
    def setValoresFil(self, fila, dic_campos):
        ''' Asigna un conjunto de valores. Si algún valor que se va asignar es dependiente o resultado de búsqueda prevalecerá el valor pasado '''
        
        # Lista de los campos que se deshabilitarán dentro de la función. Habrá que habilitarlos al terminar.
        camposDeshab = []

        # Deshabilita todos los campos que se van a modificar para que no se produzcan modificaciones secundarias sobre ellos        
        for campo in dic_campos.keys():
            if not campo in self._camposInhab:
                camposDeshab.append(campo)
                self._camposInhab.append(campo)
                            
        # Se recorre el diccionario para asignar el valor a cada campo 
        for (campo, valor) in dic_campos.items():
            # Si el campo estaba habilitado antes de entrar en la función lo habilita, modifica y vuelve a deshabilitar
            self._camposInhab.remove(campo)
            self.setValor(fila, campo, valor)
            self._camposInhab.append(campo)
            
        # Se vuelven ha habilitar los campos deshabilitados dentro de la función
        for campo in camposDeshab:
            if campo in self._camposInhab:
                self._camposInhab.remove(campo)
            
    ''' ------>
      Funciones informativas
    '''
    def modificado(self):
        '''Indica si existen modificaciones pendientes de almancenar'''
        return (len(self._camposModif) > 0)
        
    def getNombresCampos(self, **kwargs):
        '''Nombres de los campos. Se puede indicar ciertas condiciones '''
        campos = list(self._camposConf.keys())
        if 'tipos' in kwargs:
            if kwargs.pop('condicion', True): 
                campos = [c for c in campos if (c.tipo in kwargs['tipos'])]
            else:
                campos = [c for c in campos if (c.tipo not in kwargs['tipos'])]
        return campos
    
    def getTipoCampo(self, campo):
        if campo != 'id':
            return self._camposConf[campo].tipo
        else:
            return 'i'
        
    def campoModifExterno(self, campo):
        '''Indica si al modificar un campo se buscará un externo'''
        if hasattr(self._camposConf[campo], 'busqueda'):
            return self._camposConf[self._camposConf[campo].busqueda[0]].objeto # Devuelve el tipo de maestro del externo
        else:
            return None
    
    def getValoresCamposFila (self, i):
        ''''Diccionario con los campos y sus valores para una fila dada'''
        return dict(self._camposVal.loc[i])    

    def getTablaCampos (self, campos):
        '''Matriz con todas las filas para los campos indicados'''
        return (self._camposVal[campos].values.tolist())    
    
    def numeroFilas(self):
        return len(self._camposVal)

    def numeroCampos(self):
        return len(self._camposVal.keys()-2)
    
    ''' ----->
     Fucniones de creación y elimanción de filas
    '''
    
    def nuevaFila(self, orden=-1):
        if orden < 0: orden = len(self._camposVal)
        elif orden > len(self._camposVal): raise NameError("ManeajdorLineas->nuevaFila: Número de fila fuera de rango")
        else: self._camposVal.index = list(range(0,orden)) + list(range(orden+1,self._camposVal.index[-1]+2))
        
        self._camposVal.loc[orden] = [None,True]+list(x.valor for x in self._camposConf.values())
        self._camposVal.sort_index(inplace=True)
        self._camposVal.loc[orden:,'_modif'] = True 
        
        self.trataSenyal([(None, orden)], 'nf', orden)
         
        return orden
   
    def borraFila(self, num_fila):
        if ((num_fila<0) or (num_fila>=len(self._camposVal))):
            raise NameError('CampoLíneas->borraFila: num_fila fuera de rango. Fila no existe.')

        idfila = self._camposVal.loc[num_fila]['_id']
        self._camposVal = self._camposVal.drop(num_fila).reset_index(drop=True)
        
        self._idFilasBorradas.append(idfila)
        self._camposVal.loc[num_fila: , '_modif'] = True
        
        self.trataSenyal([(None, num_fila)], 'bf', num_fila)        
        
    ''' ----->
     Fucniones de cambio posicion filas 
    '''
    
    def cambiaPosFila(self, orig, dest):
    # Cambia una fila de posición redistribuyendo el resto
        if not ((orig>=0) and (orig<len(self._camposVal)) and
            (dest>=0) and (dest<len(self._camposVal))):
            raise NameError('Maestro->cambiaPosFila: Indice origen o destino fuera de rango')
        
        factor_pos = 0
        if (dest > orig):
            factor_pos = 1
        else:
            factor_pos = -1
        self._camposVal.rename(index={orig : dest+(0.5*factor_pos)}, inplace=True)
        self._camposVal = self._camposVal.sort_index().reset_index(drop=True)
        for i in range(orig,dest+factor_pos,factor_pos):
            self._camposVal.at[i, '_modif'] = True

    
    def cambiaFilas(self, num_orig, num_dest):
    # Cambia una fila por otra
        if not ((num_orig>=0) and (num_orig<len(self._camposVal)) and
            (num_dest>=0) and (num_dest<len(self._camposVal))):
            raise NameError('Maestro->cambiaFilas: Indice origen o destino fuera de rango')
            
        # Se cambian las filas de valores y la posicion de los indices
        self._camposVal.loc[num_orig], self._camposVal.loc[num_dest] = self._camposVal.loc[num_dest], self._camposVal.loc[num_orig]
        self._camposVal.loc[num_orig, '_modif'], self._camposVal.loc[num_dest, '_modif'] = True, True
                                      

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

    
    ''' ----->
     Fucniones de representacion 
    '''
                       
    def __str__(self):
        pass
 