'''
Created on 25 oct. 2018

@author: cortesj
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.dom import minidom
from builtins import str
import log

def xmlRecorreHijos(xml_nodo):
    # Recorre los hijos de un arbol XML dado
    for child in xml_nodo.childNodes:
        if child.nodeType != child.TEXT_NODE: 
            yield(child)
            
def trataValor(nombre_campo, valor):
    # Los valores pueden ser simples o listas. Los segundos estarán definidos con un * al prinicipio. Además del nombre del campo puede implicar ciertos comportamientos
    #  extras sobre el valor
    if valor and (valor[0] == '*'):
        return valor[1:].split(', ')
             
    elif (isinstance(valor, str)) and (valor[0] == '$'):
        # Comprueba el valor del campo contiene una expresión y en caso afirmativo lo separa en expresión y valor deolviendo una tupla
        datos = valor[1:].partition('->')
        return (datos[0], datos[2])
        
    else:
        if nombre_campo in ['Orden', 'Busqueda', 'Filtro', 'Resultado']:    # Se comprueba campos que obligaroriamente tienen que ser una lista
            return [valor]
        else:
            return valor

class Campo(object):
    ''' Clase para almacenar la información de un campo de datos del maestro '''

    def __init__ (self, xml_campo):
        # Carga el tipo e inicializa todos los campos del objeto
        self.tipo = xml_campo.getAttribute('tipo')
        self.valor = None
        self.expresion = None
        self.busqueda = None    # Tupla con nombre y campo en externo sobre el cual se realizará la búsqueda según el valor del campo actual        

        # Si hay campo de busqueda lo actualiza
        cBusqueda = xml_campo.getAttribute('busqueda')
        if cBusqueda > '':
            datos = cBusqueda.partition('->')
            campoE = datos[0]
            campoB = datos[2]
            self.busqueda = (campoE, campoB)

        # Carga el valor del campo dependiendo del tipo de campo
        if (self.tipo == 'l'): #Campo Lineas
            self.valor = ArbolDef(xml_campo.tagName, xml_campo)
        
        elif (self.tipo == 'w'): #Campo Adjuntos Lineas
            # Carga los campos de enlace con las lineas
            x = ArbolDef("Externo", xml_campo.getElementsByTagName("Externo")[0])
            y = ArbolDef("Lineas", xml_campo.getElementsByTagName("Lineas")[0])
            '''
            x = xml_campo.firstChild
            while (x.nodeType != x.ELEMENT_NODE):
                x = x.nextSibling
            ''' 
            self.valor = (x, y)
            self.expresion = xml_campo.getElementsByTagName("Externo")[0].getAttribute('id')
            
        elif (self.tipo == 'h'):
            self.habilitados = []
            listaCampos = xml_campo.getElementsByTagName('Campos')[0].getElementsByTagName('Campo')
            for x in listaCampos:
                if x.nodeType != x.TEXT_NODE and x.tagName == 'Campo':
                    self.habilitados += [x.firstChild.data]
            self.valor = xml_campo.firstChild.data.strip()

        elif (self.tipo in ['e', 'a']): #Campo Externo o Adjunto
            self.valor = ArbolDef("Externo", xml_campo)
                          
        elif xml_campo.firstChild:
            valorProcesado = trataValor(self.tipo, xml_campo.firstChild.data)
            if isinstance(valorProcesado, tuple): # Si se ha devuelto una tupla se trata de una expresión y del valor
                self.expresion = valorProcesado[0]
                self.valor = valorProcesado[1]
            else:
                self.valor = valorProcesado            
                        
        else:          
            self.valor = None
    
    def modificadores(self):
        return dict(filter(lambda x: (x[0] not in ['valor', 'tipo']) and (x[1] != None),  self.__dict__.items()))
        
    def __str__(self):
        sResult = str(self.tipo) + ', b:'+str(self.busqueda)+ ', e:'+str(self.expresion)+' - '
        if (self.tipo in ['e','a']):
            sResult += '\n\t' + '\n\t'.join(str(self.valor).splitlines())
        elif (self.tipo in ['h','l']):
            sResult += '\n\t' + '\n\t'.join(str(self.valor).splitlines())
        elif self.tipo == 'w':
            sResult += '\n\t' + 'Campo Enlace:\n\t\t'
            sResult += '\n\t\t'.join(str(self.valor[0]).splitlines())
            sResult += '\n\tLíneas Complementarios:\n\t\t' 
            sResult += '\n\t\t'.join(str(self.valor[1]).splitlines())
        else:
            sResult += str(self.valor)
        sResult += '\n'
        return sResult
 

class ArbolDef(object):
    '''
    Clase donde se guardará un arbol con los parámetros de la definicón de un objeto de la aplicación
    '''

    ''' ----->
        Función inicio de la clase AlmacenMst
    '''
    def __init__ (self, nombre, xml_estructura):

        _dom =xml_estructura
        outputXml = ''.join([line.strip() for line in _dom.toxml().splitlines()])
        xml_estructura = minidom.parseString(outputXml).firstChild

        self.nombre = nombre
        if (xml_estructura.hasAttributes()):
            #self.almacen = xml_estructura.getAttribute('almacen')
            if (xml_estructura.hasAttribute('tipo')):
                self.tipo = xml_estructura.getAttribute("tipo")
        
        ids = []
        self.orden = [] # Siempre se definirá el campo orden para dar soporte a capas superiores
        
        for xmlCampo in xmlRecorreHijos(xml_estructura):
            if xmlCampo.firstChild.nodeType == xmlCampo.firstChild.TEXT_NODE: # Si el hijo es de tipo texto se crea una variable
                self.creaVariable(xmlCampo.tagName, xmlCampo.firstChild.data)
                            
            elif (xmlCampo.tagName == 'Indice'):
                for xmlCampo in xmlRecorreHijos(xmlCampo):
                    ids.append(xmlCampo.firstChild.data)
                    
            else:
                campo = xmlCampo.tagName
                variable = self.creaVariable(campo, {})
                for xmlCampo in xmlRecorreHijos(xmlCampo):
                    variable[xmlCampo.tagName] = Campo(xmlCampo)

        self.id = tuple(ids)

    ''' ----->
        La clase ArbolDef actuará como diccionario sobre sus campos
    '''    
    def __getitem__ (self, campo):
        return self.campos[campo]

    def __setitem__ (self, campo, valor):
        self.campos[campo] = valor

    ''' ----->
    Función para crear una nueva variable de configuración en el objeto
    '''
    def creaVariable (self, nombre, valor=None):
        self.__dict__[nombre[0].lower()+nombre[1:]] = trataValor(nombre, valor)
        variable = self.__dict__[nombre[0].lower()+nombre[1:]]
        return variable
        
    ''' ----->
        Campos: Devuelve lista con los nombres de campos
    '''
    def nombresCampos (self):
        return list(self.campos.keys())        
    
    def __str__ (self):
        # Se pasa a texto la cabecera del ArbolAlamcen
        sResult = "- " + self.nombre + " - \n" 
        if "almacen" in self.__dict__.keys():
            sResult += 'Almacen: '+self.almacen + '\n' 
        sResult += 'Id: ('+', '.join(self.id) + ')\n'

        for campo in self.__dict__.keys():
            if not campo in ('maestro', 'nombre', 'almacen', 'id'):
                if (isinstance(self.__dict__[campo], dict)):
                    campoDic = self.__dict__[campo]
                    sResult += campo+':\n'
                    for campo in campoDic.keys():
                        sResult += '   - '+str(campo)+' : ' +str(campoDic[campo])
                else:
                    sResult += str(campo) + ' : ' + str(self.__dict__[campo]) + '\n'


   
        return sResult


class Iterador(object):
    def __init__(self, bdcon, tablas, condiciones, orden, limite):
        self.bdcon = bdcon
        self.tablas = tablas
        self.condiciones = condiciones
        self.orden = orden
        self.limite = limite
        self.cursor = None
        
    def siguiente(self):
        self.cursor.fethone()


class XMLCon(object):
    '''
    Clase para la comunicación con archivos X
    '''
    def __init__(self, ruta, f_indices):
        self.log = log.ini_logger(__name__)
        if (ruta[-1] != '/'):
            ruta += '/'
        self.dirXML = ruta
        self.xmlsObjetos = minidom.parse(ruta+'/'+f_indices)
        
    def cargaArbolDef(self, clase, objeto):
        ''' Devuelve un objeto con las propiedades de un Estructura de Datos '''
        confMst = self.xmlsObjetos.getElementsByTagName(clase)[0].getElementsByTagName(objeto)[0]
        xmlMnjEstruc = minidom.parse(self.dirXML+confMst.getAttribute('fichero')+".xml")
        mArbol = ArbolDef (objeto, xmlMnjEstruc.getElementsByTagName(confMst.getAttribute('indice'))[0])
        
        self.log.info('[Alamcenes] AlmacenBD->cargaArbol: ' + str(clase) + ', ' + str(objeto))
        return mArbol  
    
    def clasesArbolesDef(self):
        '''Devuelve las diferentes clases de Estructuras de Datos '''
        listaConf = []
        for xmlCampo in xmlRecorreHijos(self.xmlsObjetos.getElementsByTagName('ConfIndices')[0]):
            listaConf += [xmlCampo.tagName]
        return listaConf
        