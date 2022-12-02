from almacen import mstArticulos, mstTrabajos
from sqlalchemy import orm

def CreaTablas(bd):
    mstArticulos.Base.metadata.create_all(bd)


def BorraTablas(bd):
    Base = orm.declarative_base()
    tablas = [
        mstArticulos.Variante.__table__,
        mstArticulos.Modificador.__table__,
        mstArticulos.EscandalloDespiece.__table__,
        mstArticulos.Escandallo.__table__,
        mstArticulos.Articulo.__table__,
        
        mstTrabajos.ProcesoTarea.__table__,
        mstTrabajos.Proceso.__table__,
        mstTrabajos.Tarea.__table__,
    ]
    Base.metadata.drop_all(bind=bd, tables=tablas)