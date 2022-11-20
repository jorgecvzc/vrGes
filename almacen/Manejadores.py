'''
Created on 27 oct. 2022

@author: cortesj
'''
import importlib

from sqlalchemy import select, func, and_, or_, text, asc, desc
from sqlalchemy.orm import load_only

import pandas as pd

from almacen.uInfs import Maestro, Consulta, ListaMaestro
import almacen.mstArticulos as mstArticulos
import almacen.mstTrabajos as mstTrabajos

class MnjMaestros (object):
    '''
    Clase para el manejo de maestros y almacenamientos, independientemente de la topología de estos últimos.
    '''
    def __init__(self, session, **kwargs):
        self.session = session

    def __del__(self):
        self.session.rollback()
        self.session.expunge_all()

    def nuevoMaestro(self, nombre_maestro, **kwargs):
        m = importlib.import_module('.mstTrabajos', 'almacen')
        mst = getattr(m, 'Proceso')()
        # mst = eval('mst'+nombre_maestro+'()')
        if kwargs.pop('almacenar', True):
            self.session.add(mst)
        return mst

    def descarta (self, msts=None):
        if not msts:
            self.session.expunge_all()
        else:
            if not isinstance(msts, list):
                msts = [msts]
            for mst in msts:
                if mst in self.session:
                    self.session.expunge(mst)

    def almacena(self):
        rst = self.session.commit()
        for mst in self.session:
            mst._camposModif = []
        return rst
    
    def cargaMaestro(self, **kwargs):
        # Carga un maestro del almacén según las opciones:
        #  mst_ref: Usará un maestro para la carga.
        #  tipo: Usará un nombre para la carga. Si no hay mov devolverá el primero existente.
        #  mov: Movimiento dentro de 'ig', 'sig', 'ant', pri', 'ult'

        # Se iniciliza la lista de Campos y Valores para la posterior búsqueda
        campos = []
        
        mov = kwargs.pop('mov', 'ig')

        # Si el filtro es una uInf se busca según sus campos modificados
        if 'mst_ref' in kwargs:
            ref = kwargs['mst_ref']
            tabla = ref.__class__
            # Si el maestro tiene Id se buscará con respecto a el.
            # Si no se recuperarán los campos modificados, si los hubiera,  como campos de búsqueda.
            if not (mov in ['pri', 'ult']):
                if ref.getId():
                    campos = [(getattr(tabla, 'id'), ref.getId())]
                elif ref._camposModif:
                    campos = [(getattr(tabla, campo), ref[campo]) for campo in ref._camposModif]

        # En caso contrario será una tupla con la información
        elif 'tipo' in kwargs:
            tipo = kwargs['tipo']
            tabla = eval('mst'+tipo)
            filtro = kwargs.pop('filtro', {'campos':{}})
            if filtro:
                campos = [(getattr(tabla, campo), valor) for campo, valor in filtro['campos'].items()]
        
        else:
            raise NameError ('MnjMaestro->cargaMaestro: Debe haber un "mst_ref" o "tipo"')

        # Carga el objeto que mapea la tabla de almacén
        stmt = select(tabla)

        # Dependiendo del tipo de movimiento se usará un operador u otro
        if mov == 'sig':
            filtro = and_(*[campo[0] > campo[1] for campo in campos])
            # filtro = and_([getattr(tabla, campo) > uInf[campo] for campo in campos])
        elif mov == 'ant':
            filtro = and_(*[campo[0] < campo[1] for campo in campos])
        else:
            filtro = and_(*[campo[0] == campo[1] for campo in campos])

        # Dependiendo del movimiento se añadirá orden y limite
        if mov in ['ant', 'ult']:
            stmt = stmt.filter(filtro).order_by(tabla.id.desc()).limit(1)
        else:
            stmt = stmt.filter(filtro).order_by(tabla.id.asc()).limit(1)

        # Devuelve el resultado
        self.session.rollback()
        result = self.session.scalars(stmt).first()
        if result:
            return result
        else:
            return None

    def buscaMaestro(self, **kwargs):
        # Busca el primer maestrodel almacén que cumpla las opciones:
        #  mst_ref: Usará un maestro para la carga.
        #  tipo: Usará un nombre para la carga. Si no hay mov devolverá el primero existente.
        #  mov: Movimiento dentro de pri', 'ult'
                
        # Se iniciliza la lista de Campos y movimiento para la posterior búsqueda
        campos = []
        mov = kwargs.pop('mov', 'pri')

        # Si el filtro es una Unidad de Información se busca según sus campos modificados
        if 'mst_ref' in kwargs:
            ref = kwargs['mst_ref]']
            tabla = ref.__class__
            # Si el maestro tiene Id se buscará con respecto a el.
            # Si no se recuperarán los campos modificados, si los hubiera,  como campos de búsqueda. 
            if ref._camposModif:
                campos = [(getattr(tabla, campo), ref[campo]) for campo in ref._camposModif]
            self.session.expunge(ref)

        # En caso contrario será una tupla con la información
        elif 'tipo' in kwargs:
            tipo = kwargs['tipo']
            tabla = eval('mst'+tipo)
            filtro = kwargs.pop('filtro', [])
            campos = [(getattr(tabla, campo), valor) for campo, valor in filtro['campos'].items()]
        
        else:
            raise NameError ('MnjMaestro->cargaMaestro: Debe haber un "mst_ref" o "tipo"')        

        # Carga el objeto que mapea la tabla de almacén e inicializa el filtro según los campos            
        stmt = select(tabla)
        filtro = and_(*[campo[0].ilike(campo[1]) for campo in campos])

        # Dependiendo del tipo de movimiento se añadirá orden y limite
        if mov == 'ult':
            stmt = stmt.filter(filtro).order_by(tabla.id.desc()).limit(1)
        else:
            stmt = stmt.filter(filtro).order_by(tabla.id.asc()).limit(1)

        # Devuelve el resultado        
        result = self.session.scalars(stmt).first()
        if result:
            return result[0]
        else:
            return None
        
    def cargaLista(self, **kwargs):
        # Carga y devuelve una lista de maestros dependiendo de las opcioens:
        #  mst_ref:  Se cargará la lista en referencia a un maestro
        #  tipo: Se cargará la lista en referencia a un nombre de maestro
        #  filtro: Acompaña a tipo para indicar un filtro de búsqueda
        #  campos_lista: Indicará los campos a cargar 
        
        # Se iniciliza la lista de Campos y Valores para la posterior búsqueda
        campos = []

        # Si el filtro es una Unidad de Información se busca según sus campos modificados
        if 'mst_ref' in kwargs:
            mstRef = kwargs['mst_ref']
            tabla = mstRef.__class__
            if mstRef._camposModif:
                campos = [(getattr(tabla, campo), mstRef[campo]) for campo in mstRef._camposModif]
            
        # En caso contrario será una tupla con la información
        elif 'tipo' in kwargs:
            tabla = eval('mst'+kwargs['tipo'])
            filtro = kwargs.pop('filtro', {})
            campos = [(getattr(tabla, campo), valor) for campo, valor in filtro.items()]
        
        else:
            raise NameError ('MnjListasMaestros->cargaLista: Debe haber un "mst_ref" o "tipo"')
        
        # Carga el objeto que mapea la tabla de almacén e inicializa el filtro según los campos            
        stmt = select(tabla).\
               filter(and_(*[campo[0].ilike(campo[1]) for campo in campos]))
        
        if 'campos_lista' in kwargs:
            stmt = stmt.options(load_only(*kwargs['campos_lista']))

        if 'orden' in kwargs:
            stmt = stmt.order_by(getattr(tabla, kwargs.pop('orden')))
            
                                
        # Devuelve el resultado        
        result = self.session.scalars(stmt).all()
        if result:
            return ListaMaestro(result)
        else:
            return None

    def borraMaestro(self, msts):
        if not isinstance(msts, list):
            msts = [msts]
        for mst in msts:
            if mst in self.session:
                self.session.delete(mst)
        return self.session.commit()
        
class MnjConsultas (object):
    def __init__(self, conn):
        self.con = conn
        
    def nuevaConsulta (self, nombre_consulta):
        pass
    
    def generaConsulta(self, maestros, campos_busqueda, campos_resultado):
        if not isinstance(maestros, list):
            maestros = [maestros]

        maestros = [eval('mst'+m) for m in maestros]
        
        if not 'id' in campos_resultado:
            campos_resultado = ['id']+campos_resultado
        consulta = Consulta(maestros, campos_busqueda, campos_resultado)
                
        return consulta 
    
    
    def cargaConsulta (self, consulta):
        tabla = consulta.maestros[0]

        # Si el filtro es una Unidad de Información se busca según sus campos modificados
        filtro = consulta.camposFiltro 
        
        # Carga el objeto que mapea la tabla de almacén e inicializa el filtro según los campos
        filtro = and_(*[getattr(tabla, campo).ilike(valor) for (campo, valor) in filtro.items()])             
        stmt = select(tabla).filter(filtro)               
        
        if not '*' in consulta.camposResultado: 
            stmt = stmt.options(load_only(*consulta.camposResultado))
            
        # Devuelve el resultado
        consulta.asignaResultados(pd.read_sql(stmt, con=self.con))
                 
        return consulta
