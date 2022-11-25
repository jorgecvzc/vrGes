from sqlalchemy import (
    Column,
    Float,
    Text,
    Integer,
    SmallInteger,
    String,
    Boolean
)
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from .uInfs import Base, Maestro, MaestroLineas


''' Sección de los Trabajos sobre Artículos '''

class Tarea (Maestro, Base):
    __tablename__ = 'Tareas'
    
    id = Column('tarId', Integer, primary_key=True)
    ref = Column('tarRef', String(3), nullable=False)
    nombre = Column('tarNombre', String(100), nullable=False)
    descripcion = Column('tarDescripcion', String(150), nullable=True)
    
    def __str__ (self):
        return '<Tarea (Ref="%s", Nombre="%s")' % (self.ref, self.nombre)
    
class Proceso (MaestroLineas, Base):
    __tablename__ = 'Procesos'
    
    id = Column('proId', Integer, primary_key=True)
    nombre = Column('proNombre', String(50))
    ref = Column('proRef', String(3))
    observaciones= Column('proObs', String(150), nullable=True)
    
    tareas = relationship('ProcesoTarea', 
                          order_by="ProcesoTarea.orden", collection_class=ordering_list('orden'),
                          cascade="all, delete")
    
    def __str__ (self):
        return '<Proceso (Ref="%s", Nombre="%s")' % (self.ref, self.nombre)    

class ProcesoTarea (Maestro, Base):
    __tablename__ = 'ProcesosTareas'
    
    procesoId = Column('protaProceso', Integer, ForeignKey("Procesos.proId"), primary_key=True)
    id = Column('protaId', SmallInteger, primary_key=True)
    orden = Column('protaOrden', SmallInteger)
    tareaId = Column('protaTarea', SmallInteger, ForeignKey('Tareas.tarId'))
    tareaRef = Column('protaTareaRef', String(3))
    observaciones = Column('protaObs', String(150), nullable=True)
    unica = Column('protaUnica', Boolean, default=False, nullable=False)

    def __str__ (self):
        return '<Tarea de Proceso (Línea="%s", Tarea="%s")' % (self.orden, self.tareaRef)


