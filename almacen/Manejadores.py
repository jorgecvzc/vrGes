'''
Created on 27 oct. 2022

@author: cortesj
'''
import importlib

from sqlalchemy import select, func, and_, or_, text, asc, desc
from sqlalchemy.orm import load_only

import pandas as pd

from almacen.uInfs import Consulta, ListaMaestro

'''
Función que devuelve un maestro partiendo de su módulo y nombre 
'''
def _maestro(nombre_maestro):
    ruta = nombre_maestro.split('.')
    if (len(ruta) == 3):
        m = importlib.import_module('.mst'+ruta[1], ruta[0])
        return getattr(m, ruta[2])
    else:
        m = importlib.import_module('.mst'+ruta[0], 'almacen')
        return getattr(m, ruta[1])

class Mnj (object):
    '''
    Clase madre de los manejadores
    '''
    def __init__(self, session, **kwargs):
        self.session = session

    def __del__(self):
        self.session.rollback()
        self.session.expunge_all()


class MnjMaestros (Mnj):
    '''
    Clase para el manejo de maestros y almacenamientos, independientemente de la topología de estos últimos.
    '''
    def nuevoMaestro(self, tipo_maestro, **kwargs):
        mst = _maestro(tipo_maestro)()

        if kwargs.pop('almacenar', True):
            self.session.add(mst)
        return mst

    def cargaMaestro(self, **kwargs):
        # Carga un maestro del almacén según las opciones:
        #  mst_ref: Usará un maestro para la carga.
        #  tipo: Usará un nombre para la carga. Si no hay mov devolverá el primero existente.
        #  mov: Movimiento dentro de 'ig', 'sig', 'ant', pri', 'ult'

        # Se iniciliza la lista de Campos y Valores para la posterior búsqueda
        campos = []
        
        mov = kwargs.pop('mov', 'ig')

        # Si el filtro es una uInf se busca según sus campos modificados
        ref = None
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
            tabla = _maestro(kwargs['tipo'])
            filtro = kwargs.pop('filtro', {'campos':{}})
            if filtro:
                campos = [(getattr(tabla, campo), valor) for campo, valor in filtro['campos'].items() if valor != None]
        
        else:
            raise NameError ('MnjMaestro->cargaMaestro: Debe haber un "mst_ref" o "tipo"')
        
        print(tabla)
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
        self.session.expunge_all()
        result = self.session.scalars(stmt).first()
        if result:
            return result
        else:
            return None

    def buscaMaestro(self, **kwargs):
        # Busca el primer maestro del almacén que cumpla las opciones:
        #  mst_ref: Usará un maestro para la carga.
        #  tipo: Usará un nombre para la carga. Si no hay mov devolverá el primero existente.
        #  mov: Movimiento dentro de pri', 'ult'
                
        # Se iniciliza la lista de Campos y movimiento para la posterior búsqueda
        campos = []
        mov = kwargs.pop('mov', 'pri')

        # Si el filtro es una Unidad de Información se busca según sus campos modificados
        ref = None
        if 'mst_ref' in kwargs:
            ref = kwargs['mst_ref]']
            tabla = ref.__class__
            # Si el maestro tiene Id se buscará con respecto a el.
            # Si no se recuperarán los campos modificados, si los hubiera,  como campos de búsqueda. 
            if ref._camposModif:
                campos = [(getattr(tabla, campo), ref[campo]) for campo in ref._camposModif]

        # En caso contrario será una tupla con la información
        elif 'tipo' in kwargs:
            tipo = kwargs['tipo']
            tabla = _maestro(tipo)
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
            if ref:
                self.session.expunge(ref)            
            return result[0]
        else:
            return None

    def almacena(self):
        rst = self.session.commit()
        for mst in self.session:
            mst._camposModif = []
        return rst
        
    def descarta (self, mst=None):
        if not mst:
            self.vacia()
        elif mst in self.session:
            self.session.expunge(mst)

    def vacia(self):
        self.session.expunge_all()


class MnjListas (Mnj):
    '''
    Carga listas de consulta
    '''
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
            tabla = _maestro(kwargs['tipo'])
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

    def borraLineas(self, lsts):
        for lst in lsts:
            if lst in self.session:
                self.session.delete(lst)
        return self.session.commit()

    def vacia(self):
        self.session.expunge_all()


class MnjConsultas (object):
    def __init__(self, conn):
        self.con = conn
        
    def nuevaConsulta (self, nombre_consulta):
        pass
    
    def generaConsulta(self, maestros, campos_busqueda, campos_resultado):
        if not isinstance(maestros, list):
            maestros = [maestros]

        maestros = [_maestro(m) for m in maestros]
        
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
