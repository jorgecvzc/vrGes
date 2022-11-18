'''
Created on 25 oct. 2018

@author: cortesj
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, or_, text
import os
from builtins import isinstance

class BDER(object):
    '''
    Clase generica para el manejo de expresiones regulares en las diferentes bases de daotos.
     Se definendiferentes clases por cada opoerador y tipo de valor
    '''
    def __init__(self):
        pass

    class Tabla(object):
        def __init__(self, valor):
            self.valor = valor
            
        def __str__(self):
            return '"'+self.valor+'"'
        
    class Campo(object):
        def __init__(self, valor):
            self.valor = valor
        def __str__(self):
            return '"'+self.valor+'"'
        
    class Vacio(object):
        def __init__(self):
            self.valor = None
            
        def __str__(self):
            return ''

    class Bool(object):
        def __init__(self, valor):
            self.valor = valor
            
        def __str__(self):
            if self.valor:
                return 'True'
            else:
                return 'False'
        
    class Cad(object):
        def __init__(self, valor):
            self.valor = valor
            
        def __str__(self):
            return '"' + self.valor + '"'
        
    class Num(object):
        def __init__(self, valor):
            self.valor = valor
            
        def __str__(self):
            return str(self.valor)

    class Nulo(object):
        def __init__(self):
            pass
            
        def __str__(self):
            return 'NULL'        

    class Y(object):
        def __init__(self, valor1, *args):
            if isinstance(valor1, list):
                self.valor = valor1
            else:
                self.valor = [valor1]
            for v in args:
                self.valor.append(v)

        def __str__(self):
            res = str(self.valor[0])
            for i in range(len(self.valor)-1):
                res += ' and ' + str(self.valor[i+1])
            return res
            
            
    class Ig(object):
        def __init__(self, er1, er2):
            self.er1 = er1
            self.er2 = er2
            
        def __str__(self):
            if isinstance(self.er1, str):
                return '"'+self.er1+'"='+str(self.er2)
            else:
                return str(self.er1)+'='+str(self.er2)
        
    # Clase para la operacion Like (Busqueda con patron)
    class Li(object):
        def __init__(self, er1, er2):
            self.er1 = er1
            self.er2 = er2
            
        def __str__(self):
            return '(lower("'+str(self.er1)+'") like'+" lower('"+str(self.er2)[:-1]+"%'))"
        
    class Mq(object):
        def __init__(self, er1, er2):
            self.er1 = er1
            self.er2 = er2
            
        def __str__(self):
            return '("'+str(self.er1)+'">'+str(self.er2)+')'

    class Mi(object):
        def __init__(self, er1, er2):
            self.er1 = er1
            self.er2 = er2
            
        def __str__(self):
            return '("'+str(self.er1)+'">='+str(self.er2)+')'

    class mq(object):
        def __init__(self, er1, er2):
            self.er1 = er1
            self.er2 = er2
            
        def __str__(self):
            return '("'+str(self.er1)+'"<'+str(self.er2)+')'

    class mi(object):
        def __init__(self, er1, er2):
            self.er1 = er1
            self.er2 = er2
            
        def __str__(self):
            return '("'+str(self.er1)+'"<='+str(self.er2)+')'
                        
    class Min(object):
        def __init__(self, er):
            self.er = er

        def __str__(self):
            return 'Min("'+str(self.er)+'")'
        
        def repr(self, tabla):
            return func.min(tabla.c[self.er])
        
    class Max(object):
        def __init__(self, er):
            self.er = er

        def __str__(self):
            return 'Max("'+str(self.er)+'")'

    class Alias(object):
        def __init__(self, er, alias):
            self.er = er
            self.alias = alias

        def __str__(self):
            return str(self.er)+" As "+str(self.alias)
        
        def repr(self, tabla):
            a = self.er.repr(tabla)
            return a.label(self.alias)        


class BDCon(object):
    def __init__ (self, servidor, bd, usuario, password):
        '''
        Constructor
        '''
        from xml.dom import minidom
        
        self.er = BDER()
        
        # -- Configura las constantes y valores por defecto
        self.constJoin = {'L':'LEFT JOIN', 'R': 'RIGHT JOIN', 'I':'INNER JOIN'}
        
        # -- Carga las relaciones de Clave Externa de la Base de Datos
        xmlClaves = minidom.parse(os.path.dirname(os.path.abspath(__file__))+"/../Config/TablasRel.xml")
        xmlClaves = xmlClaves.getElementsByTagName("ClavesExternas")[0]
        xmlTablas = xmlClaves.getElementsByTagName('Tabla')
        self.fks ={}
        for xmlTabla in xmlTablas:
            sTablaFK = xmlTabla.getAttribute('nombre')
            
            xmlTablasRel = xmlTabla.getElementsByTagName('TablaRel')
            for xmlTablaRel in xmlTablasRel:
                xmlTablaRel.getElementsByTagName('Relacion')[0]
                self.fks[sTablaFK] = {xmlTablaRel.getAttribute('nombre'):(xmlTablaRel.getElementsByTagName('Relacion')[0].firstChild.data, 
                                                                          xmlTablaRel.getElementsByTagName('ClaveExterna')[0].firstChild.data,
                                                                          xmlTablaRel.getElementsByTagName('ClavePrincipal')[0].firstChild.data)}
                
    def __del__ (self):
        pass
    
    def inserta (self, tabla, campos, valores):
        ''' BORRAR
        if campos and (len(campos) == len(valores)):
            consSQL = 'INSERT INTO ' + str(self.er.Tabla(tabla)) + ' (' + ', '.join(map(lambda c : str(c), campos))  + ')'
            consSQL += ' VALUES (' + ', '.join(map(lambda v : str(v).replace('"', '\"') if (v != None) else "Null", valores)) + ');'
            
        else:
            raise NameError('No se puede insertar líneas sin valores en la BD')
        '''
        md = MetaData()
        table = Table(tabla, md, autoload_with=self.bd)
        
        # Se generan el diccionario con los campos a insertar
        campos = dict(zip(campos, valores))
                
        try:
            idIns = self.cursor.execute(table.insert(), campos).inserted_primary_key
        except:
            sql =  "F-Inserta. Error al ejecutar la sentencia SQL\n '" + campos + "'"
            raise NameError(sql)
        self.cursor.commit()
        
        return idIns
        
    def actualiza (self, tabla, campos, valores, condiciones):
        consSQL = 'UPDATE ' + str(self.er.Tabla(tabla)) + ' SET '
        datosAct = ""
        if (len(campos) == len(valores)):
            for i in range(len(campos)):
                if (valores[i] != None):
                    datosAct += str(self.er.Campo(campos[i]))+"='"+str(valores[i]).replace('"', '\"') + "', "
                else:
                    datosAct += str(self.er.Campo(campos[i]))+'=Null, '
            datosAct = datosAct[:-2] 
            consSQL += datosAct + ' WHERE ' + str(condiciones)
        try:
            self.cursor.execute(consSQL)
            self.cursor.commit()
            return 1
        except:
            sql =  "F-Actualiza. Error al ejecutar la sentencia SQL \n" + consSQL
            raise NameError(sql)
        
    def borra (self, tabla, condiciones):
        consSQL = 'DELETE FROM ' + str(tabla) + ' WHERE ' + str(condiciones)
        try:
            self.cursor.execute(consSQL)
            rc = self.cursor.rowcount
            self.bd.commit()
            return rc
        except:
            sql =  "F-Borra. Error al ejecutar la sentencia SQL \n" + consSQL + "'"
            raise NameError(sql)
         
    def selecciona(self, tablas, **kwargs):
        ''' campos=["*"]
            condiciones=None 
            orden=[] 
            limite=None
        '''
           
        sJoin = ''
        if not isinstance(tablas, list):
            raise NameError('El parámetro tabla debe ser una lista.')
        else:
            sTablaBase = self.er.Tabla(tablas[0])
            sJoin = ''
            tablasJoin = tablas[1:]
            for sTablaJoin in tablasJoin:
                camposJoin = self.fks[self.er.Tabla(sTablaJoin)][sTablaBase]
                sJoin += ' ' + self.constJoin[camposJoin[0]] + ' ' + self.er.Tabla(sTablaJoin) + ' On ' + camposJoin[1] + '=' + camposJoin[2]

        md = MetaData()
        tabla = Table(tablas[0], md, autoload_with=self.bd)

        if 'campos' in kwargs:
            stmt = select()
            for campo in kwargs['campos']:
                if isinstance(campo, str):
                    stmt = stmt.add_columns(tabla.c[campo])
                else:
                    stmt = stmt.add_columns(campo.repr(tabla))
        else:
            stmt = select(tabla)

        if 'condiciones' in kwargs:
            stmt = stmt.filter(text(str(kwargs['condiciones'])))
  
        if 'orden' in kwargs:
            stmt = stmt.order_by(*(tabla.c[campo] for campo in kwargs['orden']))

        if 'limite' in kwargs:
            limite = kwargs['limite']     
            if isinstance('limite', tuple):
                limite = kwargs['limite']
                stmt = stmt.slice(limite[0], limite[1])
            else:
                stmt = stmt.limit(kwargs['limite'])

        try:
            return self.cursor.execute(stmt).fetchall()
        except:
            sql =  "F-Selecciona. Error al ejecutar la sentencia SQL \n" + stmt + "'"
            raise NameError(sql)
            return None
                

    def filtroAnd(self, tabla, campos, valores):
        return self.filtro(tabla, campos, valores, 'And')

    def filtroOr(self, tabla, campos, valores):
        return self.filtro(tabla, campos, valores, 'Or')
        
    def filtro(self, tabla, campos, valores, conjuncion='And', orden=[]):
        sqlTabla = tabla
        sqlCampos = ''
        sqlCondiciones = ''
        sqlOperadorComp = ''
        sqlOperadorUni = ''
        sqlOrden = ''
        
        for i in range(len(campos)):
            sqlCampos += campos[i] + ', '
            if (i<len(valores)):
                if (valores[i] is not None ):
                    valores[i] = str(valores[i]).replace('*', '%')
                    sqlOperadorComp = ' LIKE ' if ('%' in valores[i]) else ' = '
                    sqlCondiciones += sqlOperadorUni + campos[i] + sqlOperadorComp + '"' + str(valores[i]) + '"'
                    sqlOperadorUni = ' ' + conjuncion + ' '
        sqlCampos = sqlCampos[:-2]

        if (len(orden) > 0):
            sqlOrden = ', '.join(orden)

        return self.selecciona(sqlCampos, sqlTabla, sqlCondiciones, sqlOrden)

class BDConMySQL(BDCon):
    def __init__ (self, servidor, bd, usuario, passw):
        '''
        Constructor
        '''
        super().__init__(servidor, bd, usuario, passw)
        # -- Establece la conexion con la Base de Datos
        try:
            self.bd = None # pymysql.connect(host=servidor, user=usuario, passwd=passw, db=bd, cursorclass=pymysql.cursors.DictCursor)
        except:
            raise NameError('Problema en la conexión con la base de datos')
        self.cursor = self.bd.cursor()
        
        
class BDConPostgreSQL(BDCon):
    
    class ER(BDER):
        class Tabla(BDER.Tabla):
            def __init__(self, valor):
                self.valor = valor
            
            def __str__(self):
                return '"'+self.valor+'"'
        
        class Campo(BDER.Campo):
            def __init__(self, valor):
                self.valor = valor
            
            def __str__(self):
                return '"'+self.valor+'"'
                                
        class Cad(BDER.Cad):
            def __init__(self, valor):
                if isinstance(valor, str):
                    self.valor = valor
                else:
                    raise("Error. BDCon->ER->Cad->__init__: El valor tiene que ser una cadena")
            
            def __str__(self):
                return "'"+self.valor+"'"
    
    
    def __init__ (self, servidor, bd, usuario, passw):
        '''
        Constructor
        '''
        super().__init__(servidor, bd, usuario, passw)

        self.er = self.ER()
        
        # -- Establece la conexion con la Base de Datos
        try:
            #self.bd = psycopg2.connect(host=servidor, database=bd, user=usuario, password=passw)
            self.bd = create_engine('postgresql://'+usuario+':'+passw+'@'+servidor+':5432/'+bd, echo=False)
            Session = sessionmaker(bind=self.bd)
            self.cursor = Session()
        except:
            raise NameError('Problema en la conexión con la base de datos')

if __name__ == '__main__':
    from Manejadores import Control
    cn = Control('..')
    mnj = cn.nuevoManejador()
    
    mnj.almacen.Inf.selecciona(['Articulos'], condiciones=mnj.almacen.ER.Ig('artId', 1), orden=['artRef', 'artId'])
    
    
    bd = BDConPostgreSQL("192.168.2.200", "bdVRGes", "postgres", "pVRB2018.")
    Session = sessionmaker(bind=bd.bd)    
    #result = bd.inserta('VariantesArt', ('varRef','varNombre'), ('TGEN','TALLA GENÉRICA'))
    #result = bd.inserta('VariantesArt', ('varRef','varNombre'), ('CGEN','COLOR GENÉRICO'))
    
    md = MetaData()
    table = Table('Articulos', md, autoload_with=bd.bd)

    from sqlalchemy import func
    session = Session()
    result = select()
    result = result.add_columns(func.min(table.c['artRef']).label('id'))
    print(result)
    result = result.where(table.c['artRef']=='3LSUPEROILEXTRA')
    print (result)
    result = session.execute(result)
    
    
    # result = bd.selecciona(['VariantesArt'])
    for reg in result.all():
        print(reg)
        # print (isinstance(reg[4], bool))
    

    
    

