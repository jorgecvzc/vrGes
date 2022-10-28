'''
Created on 31 oct. 2018

@author: cortesj
'''
from filecmp import cmp
from builtins import isinstance

import pandas as pd

from Maestros import ControlMaestro, Maestro
from DefMaestros import valorDefecto, tipoUInf
from Consultas import ConsultaY, ConsultaMaestros

from almacen import FunSQL as f

class Manejador(object):
    '''
    Clase para el manejo de maestros y almacenamientos, independientemente de la topología de estos últimos.
    '''
    def __init__(self, almConf, almInf, **kwargs):
        '''
        Constructor Manejador    
        '''
        self.almConf = almConf
        self.almInf = almInf

 
    ''' ------------------------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE LOS ÁRBOLES DE CONFIGURACIÓN
        ------------------------------------------------------------- ''' 
           
    def cargaMemoriaConfObjetos(self, **kwargs):
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

        
    ''' ---------------------------------------------------------------
        FUNCIONES INTERNAS PARA EL TRATAMIENTO DE LOS OBJETOS UNIDADINF 
        --------------------------------------------------------------- '''       
   
    def _cargaValoresUInf(self, uInf, **kwargs):
        ''' Carga los valores de una Unidad de Informacion dependiendo de los campos de consulta '''
        
        nivel_ext = kwargs.pop('nivel_ext', 0)

        uInf.deshabilitaTunelSalida()

        # Carga los registros directos de la UInf
        reglineas = self.almInf.cargaRegistrosUInf(uInf, **kwargs)
        
        # Vacia los valores de la unidad de inf, si los hubiera
        uInf._camposVal = uInf._camposVal[0:0]
        uInf.setId((None,))
        
        # Si se carga el id pasado por parámetro o el resultante de la carga si no hay el primero
        if 'mst_id' in kwargs:
            lid = kwargs['mst_id']
        else:        
            lid = []
            if reglineas:
                # Carga el valor del indice
                for idm in uInf._getCamposId():
                    lid.append(getattr(reglineas[0], idm))
            lid = tuple(lid)
            if (uInf.getTipo() == tipoUInf.CAMPO_LINEAS):
                # El índice de un campo líneas es el índice común de todas las lineas (campos del índice menos el último)
                lid = lid[:-1]
                       
        for fila in reglineas:
            reglin = fila.__dict__ 
            nfila = uInf.nuevaFila()
            lineaDatos = {}
            idLineaDatos =reglin['id']
            # Carga cada uno de los campos dependiendo de su tipo en la fila actual
            
            varNombres = uInf._camposConf.keys()
            for variable in varNombres:
                campo = uInf._camposConf[variable]
                tipoCampo = campo.tipo
                valor = valorDefecto.get(tipoCampo, None)
                 
                if (tipoCampo == 'l'):
                    cl = self.almConf.cargaCamposUInf(tipoUInf.CAMPO_LINEAS, uInf._camposConf[variable].objeto, t_senyal=uInf._tSenyales[0])
                    cl.setId(lid)
                    valor = self._cargaValoresUInf(cl, nivel_ext=nivel_ext)

                elif (tipoCampo == 'w'):
                    # Se carga el campo complemetario en caso de que exista definido el externo al que complementa.
                    #  Se necesita la id del maestro y del externo para cargar las lineas y sus complementarias
                    enlaceExt = campo.valor[0].id[0]
                    if (isinstance(lineaDatos[enlaceExt], tuple)):
                        lidw = lid+lineaDatos[enlaceExt]
                    else:
                        lidw = lid+lineaDatos[enlaceExt].getId()
                    valor = self.cargaCampoWLineas(variable, campo.valor, uinf_conf[enlaceExt].valor, lidw, nivel_ext=nivel_ext, t_senyal=uInf._tSenyales[0])
        
                elif (tipoCampo == 'e'):
                    valor = reglin[variable]
                    if valor and nivel_ext:
                        ext = self.nuevoMaestro(campo.objeto, etiqueta=(variable, nfila), t_senyal=uInf._tSenyales[0])
                        ext.setId(valor)
                        valor = self.cargaMaestro(ext, nivel_ext=nivel_ext-1)

                elif (tipoCampo == 'a'):
                    mstAdj = self.cargaMaestro(campo.valor.almacen, etiqueta=variable, mst_ref=tuple(lid), t_senyal=uInf._tSenyales[0], nivel_ext=nivel_ext)
                    if mstAdj:
                        valor = mstAdj
                    else:
                        # Si no hay datos en el almacén se le asigna el índice del maestro actual por si se generan nuevos para poderlo luego almacenar
                        valor = self.nuevoMaestro(campo.valor.almacen, etiqueta=variable, Id=tuple(lid), t_senyal=uInf._tSenyales[0], nivel_ext=nivel_ext)
                        valor.setId(tuple(lid))                                                     

                elif (tipoCampo == 'h'):
                    if reglin[campo.valor]:
                        valor = reglin[campo.valor]
                    else:
                        valor = False
                                            
                else:
                    valor = reglin[variable]                    
                    
                lineaDatos[variable] = valor
                
            uInf.setValoresFil(nfila, lineaDatos)
            uInf._setIdFila(nfila, idLineaDatos)
            
        uInf.setId(lid)      
        uInf._camposVal['_modif'] = False
        uInf._camposModif = [] 
        
        uInf.habilitaTunelSalida()
                
        return uInf
    
    def _almacenaValoresInf(self, uinf): # mst_id, maestro_lineas, nombre_ml, ml_arbol):
        self.almInf.almacenaValoresInf(uinf)
        result = 0

        camposSimples = [c for c in uinf.getNombresCampos() if ((uinf_conf[c].tipo not in ['a','l']) and (uinf_conf[c].valor) and (c in uinf._camposModif))]
        camposCompuestos = [c for c in uinf.getNombresCampos() if (uinf_conf[c].tipo in ['a','l']) and (c in uinf._camposModif)]
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
    
        
    ''' -------------------------------------------
        FUNCIKONES ESPECÍFICAS DE LOS CAMPOS LÍNEAS
        ------------------------------------------- 
    
    def nuevoCampoLineas(self, nombre_cl, def_cl, **kwargs):
    
        ml = ControlMaestro().nuevoCampoLineas(nombre_cl)  # Importante!! En la defición XML los índices deben estar en primer lugar para que no haya error
        
        self.almConf.cargaCamposUInf(ml, def_cl, **kwargs)

        return ml
    
    def cargaCampoLineas(self, nombre_cl, def_cl, mst_id, **kwargs):
        # -- Carga de una variable en formato objeto de CampoLineas
        
        ml = self.nuevoCampoLineas('cl', def_cl, etiqueta=nombre_cl, **kwargs)

        kwargs['mst_id'] = mst_id
                
        self._cargaValoresUInf(ml, def_cl, **kwargs)
        
        return ml'''

    def almacenaCampoLineas(self, mst_id, maestro_lineas, nombre_ml, ml_arbol):
        self.almacenaValoresInf(maestro_lineas, ml_arbol)

    ''' ------------------------------------------------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE LAS LÍNEAS DE LOS CAMPOS TIPO COMPLEMENTARIO-LÍNEAS
        ------------------------------------------------------------------------------------ '''
    
    def nuevoCampoWLineas(self, nombre_cl, def_me, def_cl, **kwargs):
        ''' Crea un nuevo campo de líneas complementarios. 
            Parámetros:
                def_me: arbol con la configuración del campo externo cuyo campo líneas seleccionado habrá qeu completar
                def_ml: arbol con la configuración de los camplos complementarios al líneas base
        '''
        # Carga el maestro externo solo con el campo lineas que se va a complementar
        objeto = self.arbolConf('Maestros', def_me.almacen)
        ml = self.nuevoCampoLineas('cw', objeto[def_cl[0].listaCampos[0]].valor, etiqueta=nombre_cl)
                
        # Completa el campo lineas con los campos definidos en el XML
        mlArbol = def_cl[1]
        for campo in def_cl[1].campos.keys():
            tipo = mlArbol[campo].tipo
            if (tipo=='e'):
                ml._nuevoCampo(campo, tipo, mlArbol[campo].valor.almacen)
            else:
                ml._nuevoCampo(campo, tipo)
                if (mlArbol[campo].expresion):
                    ml._nuevaFormula(campo, mlArbol[campo].expresion)
            if mlArbol[campo].busqueda:
                ml._nuevaBusqueda(campo, mlArbol[campo].busqueda)
        ml._mnj = self
        ml.asignaManejador(self)
        
        if 'etiqueta' in kwargs.keys(): ml.setEtiqueta(kwargs['etiqueta'])
        if 't_senyal' in kwargs.keys(): ml.asignaTunelSenyal(kwargs['t_senyal'])
        
        return ml        
            
    def cargaCampoWLineas(self, nombre_cl, def_cl, def_me, ids, **kwargs):
        ''' Carga un nuevo campo de líneas complementarios. 
            Parámetros:
                nombre_cl: nombre identificativo del campo
                ids: ids[0] - Id del maestro. ids[1] - Id del externo cuyas líneas hay que complementar
                def_me: arbol con la configuración del campo externo cuyo campo líneas seleccionado habrá quE completar
                def_cl: arbol con la configuración de los campos complementarios al líneas base
        '''        
        # Carga el campo lineas base
        objeto = self.arbolConf('Maestros', def_me.almacen)
        mlArbol = objeto[def_cl[0].listaCampos[0]].valor
        mlBase = self.cargaCampoLineas(nombre_cl, mlArbol, ids[1], **kwargs)
        
        # Carga el campo lineas complementario
        mlArbol = def_cl[1] 
        mlCompl = self.cargaCampoLineas(nombre_cl, mlArbol, ids[0], **kwargs)
        
        # Se acutualiza el Id al maestro que contiene el complementario
        mlBase.setId(mlCompl.getId())
        # Completa las configuraciones del campo líneas base con el complementario
        for (nombre, campo) in  mlCompl._camposConf.items():
            mlBase._camposConf[nombre] = campo
            mlBase._camposVal[nombre] = None
        
        for (nombre, formula) in  mlCompl._formulas.items():
            mlBase._formulas[nombre] = formula
                
        for nombre in mlCompl._camposInhab:
            if nombre not in mlBase._camposInhab:
                mlBase._camposInhab.append(nombre)

        # Completa los valores del campo líneas base con el complementario
        mlBase._camposVal.set_index(['_id'], inplace=True)
        mlBase._camposVal.update(mlCompl._camposVal.set_index(['_id']))
        mlBase._camposVal.reset_index(inplace=True)

        return mlBase


    ''' ---------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE LOS MAESTROS
        --------------------------------------------- '''     
     
    def nuevoMaestro(self, tipo_maestro, **kwargs):
        '''
        Devuelve el manejador del maestro dado por maestroç
        Parámetros:
         tipo_maestro
         kwargs:  lineas. Si lineas es False deja las variables lineas a None
                  t_senyal. Tunel para enviar señales  
        '''
        maestro = self.almConf.cargaCamposUInf(tipoUInf.MAESTRO, tipo_maestro, **kwargs)

        # Inicializa el Manejador y el TunelSenyal del maestro    
        maestro._mnj = self

        return maestro

    def cargaMaestro(self, maestro, **kwargs):
        '''
        Carga la información de un maestro desde el almacenaje
          - tipo_maestro: Tipo de maestro a cargar
          - etiqueta: nombre del maestro una vez cargado. Lo identificará en el resto de la aplicación.
          - **kwargs: campos modificadores de la carga. Podrán adoptar los siguientes nombres:
              * nivel_ext: Profundidad que se alcanza al cargar externos. Si es 0 no se cargará ninguno, 1 se llegará al primer nivel, etc. Con -1 se carga todo e árbol.
              * mst_ref: Índice de maestro o maestro cuyos campos se usarán para cargar el primer maestro cuyos campos coincidan con los campos modificados del mst_ref
              * cmp_busq: Diccionario con campos para realizar la carga del primer maestro que tenga dichos campos. Si existe mst_ref no se tendrán en cuenta
              * conidicion_busq: Tipo de búsqueda que se realizará (pi - Busca el primer maestro que cumpla con los patrones dados)
              * t_senyal: tunel por donde el maestro puede pasar información a otros maestros o interfaces
        '''
        
       
        ''' Trata las opciones propias de la carga de maestro '''

        almacen = maestro.getAlmacen()

        # Se inicia el maestro a devolver dependiendo del parametro sobreescribe
        if kwargs.pop('sobreescribe', True):
            mst = maestro
        else:
            mst = self.nuevoMaestro(almacen, lineas=False, **kwargs)

        # En los maestros siempre tiene que haber una linea 0 de valores        
        linea = mst._camposVal
        mst = self._cargaValoresUInf(mst, **kwargs) 
        if mst.getId():
            return mst
        else:
            # Si no se ha obtenido ningún resultado del almacen se carga en el maestro los valores que tenía. Últil si existe opción 'sobreescribe'
            mst._camposVal = linea
            return None


    def almacenaMaestro(self, maestro):
        '''
        Almacena el maestro partiendo de un maestro de referencia con las propiedades necesarias para buscar el nuevo
          - maestro: Maestro con los datos a almacenar 
          - opcion_almacén: Indica las opciones que tendrá el almacenamiento
        '''
        if isinstance(maestro, (type(None), tuple)) :
            return None
        
        self.almInf.almacenaRegistrosUInf(maestro)
           
        return maestro.getId()
    
    def borraMaestro(self, maestro):
        mArbol = self.arbolConf('Maestros', maestro.getTipo())
        
        # Borra los campos que tipo líneas y adjuntos, que son totalmente dependientes del maestro padre
        listaCampos = mArbol.nombresCampos()
        for campo in listaCampos:
            if (mArbol[campo].tipo == 'l'):
                pass ### Borra variables lineas
            elif (mArbol[campo].tipo == 'a'):
                pass ### Borra adjuntos si los hubiera
        
        # Procede a borrar el registro del maestro
        if (isinstance(maestro, Maestro)):
            idn = mArbol.getId()
            sqlBorra = ' And '.join(map(lambda i: str(mArbol.idn[i]) + '=' + str(idn[i]), range(len(idn))))
        elif (isinstance(maestro, int)):
            sqlBorra = str(mArbol.id[0]) + '=' + str(maestro)
        elif (isinstance(maestro, tuple)):
            sqlBorra = ' And '.join(map(lambda i: str(mArbol.id[i]) + '=' + str(maestro[i]), range(len(maestro))))
        else:
            sqlBorra = ''        

        return self.almacen.Inf.borra(mArbol.almacen, sqlBorra)
        
    def minIdMaestro(self, tipo_maestro):
        return self.almacen.numId(self.arbolConf('Maestros', tipo_maestro), 'm')
            
    def maxIdMaestro(self, tipo_maestro):
        return self.almacen.numId(self.arbolConf('Maestros', tipo_maestro), 'M')
        
    def existeMaestro(self, mst_ref, tipo_maestro=''):
        if tipo_maestro:
            arbol = self.arbolConf('Maestros', tipo_maestro)
        else:
            arbol = self.arbolConf('Maestros', mst_ref.getTipo())
        if self.almacen.cargaMaestro(arbol, mst_ref, ""):
            return 1
        else:
            return 0
  
  
    ''' -----------------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE CONSULTAS DE MAESTRO
        ----------------------------------------------------- '''
    
    def nuevaConsultaMaestro(self, tipo_maestro, **kwargs):
        '''
        Devuelve el manejador del maestro dado por maestroç
        Parámetros:
         tipo_maestro
         kwargs:  lineas. Si lineas es False deja las variables lineas a None
                  t_senyal. Tunel para enviar señales  
        '''
        cmpsResultado = kwargs.pop('campos_resultado', None)
        
        # Inicializa el objeto consulta
        if cmpsResultado:
            cons = self.almConf.cargaCamposUInf(tipoUInf.CONS_MAESTRO, tipo_maestro, campos=cmpsResultado)
        else:
            cons = self.almConf.cargaCamposUInf(tipoUInf.CONS_MAESTRO, tipo_maestro)
            
        # Inicializa el Manejador y el TunelSenyal del maestro    
        cons._mnj = self

        return cons

    def cargaConsultaMaestro (self, cons, **kwargs):
        # Carga los valores de la consulta 
        cons = self._cargaValoresUInf(cons)
        cons._camposModif = [] 
        
        return cons


    ''' ---------------------------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE CONSULTAS DE RANGO DE MAESTROS
        --------------------------------------------------------------- '''

    def cargaConsultaRangoMaestros (self, mstIni, mstFin, **kwargs):
        pass


        
    ''' ------------------------------------------
        FUNCIONES PARA EL TRATAMIENTO DE CONSULTAS
        ------------------------------------------ '''
       
    def __nuevaConsultaMaestro(self, nombre):
        cstArbol = self.arbolConf('Consultas', nombre)
        # carga una consulta vacia

        if cstArbol.tipo == 'mst':
            consulta = ConsultaY(cstArbol.tipo, cstArbol.maestro)
        else:
            consulta = ConsultaY(cstArbol.tipo, cstArbol.nombre)
        # Inicializa los campos de la consulta

        # Carga los campos de búsqueda
        consulta._campos = cstArbol.busqueda
        consulta._filtros = cstArbol.filtro
        consulta._valores = [None]*(len(consulta._campos))
            
        # Genera las columnas de la tabla de resultados
        for campo in cstArbol.resultado:
            consulta._resultado[campo] = None
        
        # Carga los campos de orden si los hubiera
        if cstArbol.orden:
            consulta._orden = list(cstArbol.orden)
                
        return consulta
           
    def cargaConsulta(self, **kwargs):
        '''
        Carga una consulta definida en el Almacen de Definiciones
        '''
        '''
                if 'id' in campos:
            # Hay que añadir los campos que forman el índice a la consulta
            cmpid = []
            for icmp in m_arbol.id:
                cmpid += [er.Campo(icmp)]
            campos_cons = cmpid + campos_cons

        campos_orden = [er.Campo(m_arbol[corden].valor) for corden in orden] 

        '''
        # Procesa los parámetros para inicializar la consulta
        cons = None
        nombresParam = kwargs.keys()
        if ("consulta" in nombresParam):
            cons = kwargs["consulta"]
        elif ("tipo" in nombresParam):
            cons = self.nuevaConsulta(kwargs["tipo"])
        else:
            raise NameError('Manejador->cargaConsulta. Parámetro "consulta" o "tipo" necesario')
        if ("filtro" in nombresParam):
            cons.actualizaFiltro(kwargs["filtro"])
        else:
            raise NameError('Manejador->cargaConsulta. Parámetro "filtro" necesario')
                
        listaCamposResultado = cons._resultado.columns.values
        listaCamposOrden = cons._orden
           
        if cons.getTipo() == 'mst':
            mstArbol = self.arbolConf('Maestros', cons.getEtiqueta())
        else:
            mstArbol = self.arbolConf('Consultas', cons.getEtiqueta())
            
        # Inicializa los campos de la consulta
        er = self.almacen.ER
        cond = []
        for tupla in cons.getCamposBusq():
            cond += [eval('er.'+tupla[1]+'(mstArbol[tupla[0]].valor, tupla[2])')]

        if len(cond) > 0:
            cond = er.Y(cond)

        # Inicializa los campos resultadoç
        camposResult = [mstArbol[campo].valor for campo in listaCamposResultado if campo != 'id']
        if 'id' in listaCamposResultado:
            camposResult = [campo for campo in list(mstArbol.id)] + camposResult
        
        # Inicializa el orden
        camposOrden = [mstArbol[corden].valor for corden in listaCamposOrden if corden != 'id']

        # Carga el resultado en la consulta según sus parámetros
        if cons.getTipo() == 'cns':        
            tablas = [t for t in mstArbol.almacen.keys()]
        else:
            tablas = [mstArbol.almacen]

        if cond:    
            conssql = self.almacen.Inf.selecciona(tablas, campos=camposResult, condiciones=cond, orden=camposOrden)
        else:
            conssql = self.almacen.Inf.selecciona(tablas, campos=camposResult, orden=camposOrden)
            
        if (conssql.rowcount > 0):
            cons._resultado = pd.DataFrame(conssql, columns=cons._resultado.columns)
        else:
            cons._resultado = pd.DataFrame(columns=cons._resultado.columns)
        
        return cons
    
    def consultaMaestro(self, maestro, campos, resultado, orden = []):
        '''
        Genera un objeto de tipo consulta a partir de un maestro. Siempre cargará con el operador Li 
         Su nombre siempre empezará por mst para saber que se ha construido a través de un maestro   
        '''
     
        er = self.almacen.ER
        m_arbol = self.arbolConf('Maestros', maestro.getTipo())

        cond = []

        filtro = []
        camposBusqueda = []
        valoresBusqueda = []
        # Carga las condiciones inferiores si las hay
        for datoCarga in maestro._camposModif:
            filtro.append('Li')
            camposBusqueda.append(datoCarga)            
            if (m_arbol[datoCarga].tipo == 'e'):                cond += [er.Li(m_arbol[datoCarga].valor, maestro[datoCarga].getIdNum())]
                valoresBusqueda.append(maestro[datoCarga].getIdNum())
            elif (m_arbol[datoCarga].tipo != 'l'):
                cond += [er.Li(m_arbol[datoCarga].valor, maestro[datoCarga])]                valoresBusqueda.append(maestro[datoCarga])

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
        if cond:            conssql = self.almacen.Inf.selecciona([m_arbol.almacen], campos=campos_cons, condiciones=cond, orden=campos_orden)
        else:
            conssql = self.almacen.Inf.selecciona([m_arbol.almacen], campos=campos_cons, orden=campos_orden)
        if (len(conssql) > 0):
            cons = ConsultaMaestros('cm'+maestro.getTipo(), maestro.getEtiqueta())
            cons._filtro = filtro
            cons._campos = camposBusqueda
            cons._valores = valoresBusqueda
            cons._resultado = pd.DataFrame(conssql)
            cons._resultado.columns = resultado  
            return cons
        else:
            return None

            
    def consultaRangoMaestros(self, maestro_ini, maestro_fin, campos, resultado, orden = []):
        '''
        Devuelve un objeto de tipo consulta con los campos seleccionados de los maestros entre un inicio y un fin    
        '''
        m_arbol = self.arbolConf('Maestros', maestro_ini.getTipo())

        if (maestro_ini and maestro_fin and (maestro_ini.getTipo() != maestro_fin.getTipo())):
            raise NameError('Error - Manejador->consultaMaestros. Los tipos no coinciden ')
        
        cons = ConsultaY('cmr'+maestro_ini.getTipo(), maestro_ini.getEtiqueta())
        
        # Carga las condiciones inferiores y superiores
        for datoCarga in maestro_ini._campos:
            # Se carga los valores de los campos de rango inferior
            cons._campos.append(datoCarga)
            cons._filtros.append('Mi')
            if datoCarga == 'id':
                cons._valores.append(maestro_ini.getId())
            elif (m_arbol[datoCarga].tipo == 'e'):
                cons._valores.append(maestro_ini[datoCarga].getIdNum())
            elif (m_arbol[datoCarga].tipo != 'l'):
                cons._valores.append(maestro_ini[datoCarga])

            # Se carga los valores de los campos de rango superior
            cons._campos.append(datoCarga)
            cons._filtros.append('mi')
            if datoCarga == 'id':
                cons._valores.append(maestro_fin.getId())
            elif (m_arbol[datoCarga].tipo == 'e'):
                cons._valores.append(maestro_fin[datoCarga].getIdNum())
            elif (m_arbol[datoCarga].tipo != 'l'):
                cons._valores.append(maestro_fin[datoCarga])
                                
        return self.cargaConsulta(conulta=cons)

class ManejadorConf(Manejador):
    def nuevoMaestro(self, tipo_maestro, **kwargs):
        '''
        Devuelve el manejador del maestro dado por maestroç
        Parámetros:
         tipo_maestro
         kwargs:  lineas. Si lineas es False deja las variables lineas a None
                  t_senyal. Tunel para enviar señales  
        '''
        m_arbol = self.arbolConf('Maestros', tipo_maestro)        
        maestro = ControlMaestro().nuevoMaestro(m_arbol.nombre)

        return maestro    
    

if __name__ == '__main__':
    
    from Control import Control
    cn = Control('.')
    mnj = cn.nuevoManejador()
 
    prov = mnj.nuevoMaestro('ModificadorArt')
    prov['variante'] = 1
    print (prov)

    mnj.almacenaMaestro(prov)
    cons = mnj.nuevaConsultaMaestro('VarianteArt')
    cons = mnj.cargaConsultaMaestro(cons)
    print(list(cons.resultado('id')), list(cons.resultado('nombre')))
    
 
       
    '''
    prov = mnj.nuevoMaestro('ModificadorArt')
    prov = mnj.cargaMaestro(prov, mov='pri')
    if prov.getId():
        print(prov)
    else:
        print ('No hay elemento')
    '''