from sqlalchemy import (
    Float,
    Text,
    Integer,
    SmallInteger,
    String,
    Boolean
)
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from .uInfs import Base, Maestro, MaestroGrupoOrdenado


''' Sección para los Personas físicas y juídicas '''

class Cliente (Maestro, Base):
    __tablename__ = 'Clientes'
    
    id = mapped_column(Integer, primary_key=True, info={})
    ref = mapped_column(String(20), nullable=False, unique=True)
    nombre = mapped_column(String(100), nullable=False, unique=False)
    nombreFiscal = mapped_column(String(150))
    direccion = mapped_column(String(150))
    
    # RelationsShip
    procedimientos = relationship('Procedimiento')
    #pedidos = relationship('Pedidos', back_populates='cliente')


class Proveedor (Maestro, Base):
    __tablename__ = 'Proveedores'
    
    id = mapped_column(Integer, primary_key=True)
    ref = mapped_column(String(20), nullable=False, unique=True)
    nombre = mapped_column(String(100), nullable=False, unique=False)
    nombreFiscal = mapped_column(String(150))
    direccion = mapped_column(String(150))
    
    # RelationsShip
    #pedidos = relationship('Pedidos', back_populates='cliente')  
    
    def __str__ (self):
        return '<Proveedor (Ref="%s", Nombre="%s")' % (self.ref, self.nombre)
    
