from Almacen import mstArticulos, mstTrabajos
from sqlalchemy import orm

def CreaTablas(bd):
    mstArticulos.Base.metadata.create_all(bd)


def BorraTablas(bd):
    Base = orm.declarative_base()
    tablas = [
        # Tablas asociaciones "Many To Many"
        mstTrabajos.asocProcedimientoProcProceso,
        
        # Tablas Maestras
        mstArticulos.Pedido.__table__,
        mstArticulos.PedidoLineas.__table__,
        mstArticulos.Posicion.__table__,

        mstArticulos.EscandalloDespiece.__table__,
        mstArticulos.Escandallo.__table__,
        
        mstTrabajos.ProcesoTarea.__table__,
        mstTrabajos.Tarea.__table__,
        mstTrabajos.Proceso.__table__,
        mstTrabajos.ProcProcDetalle.__table__,
        mstTrabajos.ProcProceso.__table__,
        mstTrabajos.Procedimiento.__table__,

        mstArticulos.Articulo.__table__,        
        mstArticulos.Variante.__table__,
        mstArticulos.Modificador.__table__,
        mstArticulos.ArticuloStock.__table__,

        mstArticulos.Cliente.__table__,
        mstArticulos.Proveedor.__table__,
        
    ]
    Base.metadata.drop_all(bind=bd, tables=tablas)