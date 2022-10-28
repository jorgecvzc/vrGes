from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import select, func, and_, or_, text, asc, desc
from sqlalchemy.orm import sessionmaker

from unidadesInf import tipoUInf

from .tblsArticulos import *


class FunSQL ():
    select = select
    func = func
    or_ = or_
    and_ = and_
    select = select

class Inf ():
    
    def __init__(self, confConexion):

        self.bd = create_engine(confConexion["Motor"]+'://'+ 
                                confConexion["Usuario"]+':'+confConexion["Clave"]+'@'+
                                confConexion["Servidor"]+':5432/'+confConexion["NombreBD"], echo=False)
        Session = sessionmaker(bind=self.bd)
        self.session = Session()

    def procesaOperador(self, tabla, campo1, operador, campo2):
        if operador == '==':
            return (getattr(tabla, campo1) == campo2)
        elif operador == '>=':
            return (getattr(tabla, campo1) >= campo2)
        
    #----------------------------
    # Funciones de consulta genericsa sobre Maestros
    #---          
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
            return self.session.execute(stmt).fetchall()
        except:
            sql =  "F-Selecciona. Error al ejecutar la sentencia SQL \n" + stmt + "'"
            raise NameError(sql)
            return None
        
        
    def cargaRegistro(self, tabla, condiciones, **kwargs):
        '''
        Devuelve los campos solicitados del primer registro de una tabla del almacén que coincide con las condiciones dadas.
        '''
        kwargs['condiciones'] = condiciones
        return self.selecciona([tabla], **kwargs)[0]


    def cargaRegistros(self, tabla, condiciones, **kwargs):
        '''
        Devuelve los campos solicitados de una tabla del almacén que coincide con las condiciones dadas.
        '''
        kwargs['condiciones'] = condiciones
        return self.selecciona([tabla], **kwargs)

    
    ''' ---------------------------------------------------------------
        FUNCIONES DE APOYO PARA EL TRATAMIENTO DE LOS OBJETOS UNIDADINF 
        --------------------------------------------------------------- '''
                  
    def cargaRegistrosUInf(self, uInf, **kwargs):
        
        ''' Genera la consulta para almacen y devuelve los valores dependiendo de los parámetros pasados '''
        
        tabla = eval(uInf.getAlmacen())
        stmt = select(tabla)
        
        # Trata los campos de búsqueda si existen y ejecuta la carga desde el almacen
        # Se recorreran los parámetros de búsqueda de forma que si hay varios ejecutará del más prioritario al menos hasta
        #  encontrar un valor o devolver None
        
        # Se carga el movimiento. Por defecto ninguno.
        mov = kwargs.pop('mov', 'ig')
        tipo = uInf.getTipo()
        
        # Se iniciliza la lista de Campos y Valores para la posterior búsqueda
        campos = []

        # Si el índice aparece como modificado se obvia el resto
        if uInf._camposModif:
            if 'id' in uInf._camposModif:
                campos = [(getattr(tabla, 'id'), uInf.getId()[0])]
            else:
                campos = [(getattr(tabla, campo), uInf[campo]) for campo in uInf._camposModif]
                            
        # Se cargan los parámentros de búsqueda según los campos que estén modificados.
        # Si se trata de un objeto tipo Consulta de Maestro se procesas sus campos de búsqueda.
        #  Si no sus campos normales
        if tipo == tipoUInf.CONS_MAESTRO:
            filtro = and_(*[campo[0].ilike(campo[1]) for campo in campos])
            stmt = stmt.filter(filtro)
            
        else:        
                       
            # Dependiendo del tipo de movimiento se usará un operador u otro
            if mov == 'sig':
                filtro = and_(*[campo[0] > campo[1] for campo in campos])
                #filtro = and_([getattr(tabla, campo) > uInf[campo] for campo in campos])
            elif mov == 'ant':
                filtro = and_(*[campo[0] < campo[1] for campo in campos])
            else:
                filtro = and_(*[campo[0] == campo[1] for campo in campos])
            
            # Dependiendo del movimiento se añadirá orden y limite
            if mov in ['sig','ult']:
                stmt = stmt.filter(filtro).order_by(tabla.id.desc()).limit(1)
            elif mov in ['ant','pri']:
                stmt = stmt.filter(filtro).order_by(tabla.id.asc()).limit(1)
            else:
                stmt = stmt.filter(filtro)
            
        return self.session.scalars(stmt).fetchall()
    
    def almacenaRegistrosUInf(self, uinf): # mst_id, maestro_lineas, nombre_ml, ml_arbol):
        result = 0

        camposSimples = [c for c in uinf.getNombresCampos(tipos=['a', 'l'], condicion=False) if (c in uinf._camposModif)]
        camposCompuestos = [c for c in uinf.getNombresCampos(tipos=['a', 'l']) if(c in uinf._camposModif)]
        camposIdsPadre = []
        idsPadre = []
        
        # Obtiene el índice de la  Unidad de Inf
        aCons = [] 
        mstId = uinf.getId()
        for i in range(len(mstId)):
            camposIdsPadre.append(uinf_conf.id[i])
            idsPadre.append(mstId[i])
            aCons += [(self.er.Ig(uinf_conf.id[i], mstId[i]))]
        erCons = self.er.Y(aCons) if (aCons) else aCons
                            
        # Obtiene el número de líneas almacenadas y del objeto
        tablaBD = uinf_conf.almacen
        campoOrden = uinf_conf.orden
        
        campoIdF =  uinf_conf.id[-1]
        paramSQL = {'campos': [self.er.Alias(self.er.Max(campoIdF), 'maxid')]}
        if erCons:
            paramSQL['condiciones'] = erCons
        regMaxIdLineas = self.almacen.Inf.selecciona([tablaBD], **paramSQL)[0]
        idFilaAlm= regMaxIdLineas['maxid']+1 if regMaxIdLineas['maxid'] else 1
        
        # Se borran del almacen las lineas borradas del objeto
        for idFila in uinf._idFilasBorradas[:]:
            if idFila:
                self.almacen.Inf.borra(tablaBD, self.er.Y(erCons,self.er.Ig(campoIdF, idFila)))
            uinf._idFilasBorradas.remove(idFila)
        
        campos = []
        valores = []
        for linea in uinf._camposVal.query('_modif==True').itertuples():
            numFila = linea[0]
            idFila = linea[1]
            
            # Si existe un orden se añade para guardarlo en el almacen
            if campoOrden:
                campos = [campoOrden[-1]]
                valores = [numFila]
                
            for k in camposSimples:
                valorEnt = uinf.getValor(numFila, k)

                valorSal = [None]                
                if (uinf_conf[k].tipo == 'e'):
                    campos += [s for s in uinf_conf[k].valor.id]
                    cid = uinf.getValor(numFila,k)
                    if cid and (isinstance(cid, Maestro)):
                        self.almacenaMaestro(cid)                            
                        mid= cid.getId()
                        if mid:
                            valorSal = [str(x )for x in mid]                    
                else:
                    campos += [uinf_conf[k].valor]
                    if valorEnt:
                        valorSal = [valorEnt]

                valores += valorSal
            
            if pd.isna(idFila):
                # Hay que crear la fila en almacén con el orden correspondiente
                idFila = idFilaAlm
                idFilaAlm += 1
                self.almacen.Inf.inserta(tablaBD, camposIdsPadre+[campoIdF]+campos, idsPadre+[idFila]+valores)
                uinf._camposVal.at[numFila,'_id'] = idFila
            elif valores:
                # La fila existe y ha de actualizarla en almacén  con el orden correspondiente
                self.almacen.Inf.actualiza(tablaBD, campos, valores, self.er.Y(erCons, self.er.Ig(campoIdF, idFila)))
            uinf._camposVal.at[numFila,'_modif'] = False
            result += 1
                
            for c in camposCompuestos:
                if (uinf_conf[c].tipo == 'a'):
                    # Procesamiento de los campos tipo adjunto
                    if not uinf[c].getId():
                        uinf[c].setId(c.getId())
                    self.almacenaMaestro(uinf[c])
                else:
                    self.almacenaCampoLineas(idsPadre + [idFila], uinf.getValor(i, c), c, uinf_conf[c].valor)                    

        # Vacía la lista de campos modificados
        uinf._camposModif = []

        return result
    
    
    def consultaComoUInf (self, uinf):
        
        tabla = eval(uInf.getAlmacen())
        stmt = select(tabla)
        cond = []

        filtro = []
        camposBusqueda = []
        valoresBusqueda = []
        # Carga las condiciones inferiores si las hay
        for datoCarga in maestro._camposModif:
            filtro.append('Li')
            camposBusqueda.append(datoCarga)            
            if (m_arbol[datoCarga].tipo == 'e'):
                cond += [er.Li(m_arbol[datoCarga].valor, maestro[datoCarga].getIdNum())]
                valoresBusqueda.append(maestro[datoCarga].getIdNum())
            elif (m_arbol[datoCarga].tipo != 'l'):
                cond += [er.Li(m_arbol[datoCarga].valor, maestro[datoCarga])]
                valoresBusqueda.append(maestro[datoCarga])

        if len(cond) > 0:
            cond = er.Y(cond)
        
        campos_cons = [m_arbol[campo].valor for campo in resultado if campo != 'id']

        if 'id' in resultado:
            # Hay que añadir los campos que forman el índice a la consulta
            cmpid = []
            for icmp in m_arbol.id:
                cmpid += [icmp]
            campos_cons = cmpid + campos_cons

        campos_orden = [m_arbol[corden].valor for corden in orden] 
        
        if cond:
            conssql = self.almacen.Inf.selecciona([m_arbol.almacen], campos=campos_cons, condiciones=cond, orden=campos_orden)
        else:
            conssql = self.almacen.Inf.selecciona([m_arbol.almacen], campos=campos_cons, orden=campos_orden)
        if (len(conssql) > 0):
            cons = ConsultaMaestros('cm'+maestro.getAlmacen(), maestro.getEtiqueta())
            cons._filtro = filtro
            cons._campos = camposBusqueda
            cons._valores = valoresBusqueda
            cons._resultado = pd.DataFrame(conssql)
            cons._resultado.columns = resultado  
            return cons
        else:
            return None
