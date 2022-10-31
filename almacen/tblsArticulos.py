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
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from .uInfs import UInf

Base = declarative_base()

''' Sección para los Artículos y sus procesos '''

class Proceso (Base):
    __tablename__ = 'Procesos'
    
    id = Column('proId', Integer, primary_key=True)
    nombre = Column('proNombre', String(50))
    ref = Column('proRef', String(3))
    observaciones= Column('proObs', String(150))
     
class Tarea (Base):
    __tablename__ = 'Tareas'
    
    id = Column('tarId', Integer, primary_key=True)
    ref = Column('tarRef', String(3), nullable=False)
    nombre = Column('tarNombre', String(100), nullable=False)
    descripcion = Column('tarDescripcion', String(150))

    def __str__ (self):
        return '<Tarea (Ref="%s", Nombre="%s")' % (self.ref, self.nombre)
    
class Articulo (Base):
    __tablename__ = 'Articulos'
 
    id = Column('artId', Integer, primary_key=True)
    ref = Column('artRef', String(20), nullable=False, unique=True)
    refAsociada = Column('artRefAsociada', String(20))
    nombre = Column('artNombre', String(100))
    descripcion = Column('artDescripcion', String(250))
    precio = Column('artPrecio', Float(6))
    beneficio = Column('artBeneficio', Float(6))
    precioCompra = Column('artPrecioCompra', Float(6))
    observaciones = Column('artObservaciones',Text)
    proveedor = Column('artProveedor', Integer)
    numVariantes = Column('artNumVariantes', SmallInteger, default=0)
    variante1 = Column('artVariante1', Integer, ForeignKey("VariantesArt.varId"))
    variante2 = Column('artVariante2', Integer, ForeignKey("VariantesArt.varId"))
    variante3 = Column('artVariante3', Integer, ForeignKey("VariantesArt.varId"))
    control = Column('artControl', SmallInteger, default=0)
    manufacturado = Column('artManufacturado', Boolean)

    def __str__(self):
        return "<Articulo (Ref='%s', Nombre='%s')>" % (self.artRef, self.artNombre)    


class VarianteArt (UInf, Base):
    __tablename__ = 'VariantesArt'
    
    id = Column('varId', Integer, primary_key=True)
    ref = Column('varRef', String(6), nullable=False, info={'t':'t'})
    nombre = Column('varNombre', String(50), info={'t':'t'})

    def __str__(self):
        return "<VarianteArt (Ref='%s', Nombre='%s')>" % (self.ref, self.nombre)


class ModificadorArt (UInf, Base):
    __tablename__ = 'ModificadoresArt'
    
    id = Column('moaId', Integer, primary_key=True)
    ref = Column('moaRef', String(6), nullable=False, info={'t':'t'})
    nombre = Column('moaNombre', String(50), info={'t':'t'})
    varianteId = Column('moaVariante', Integer, ForeignKey("VariantesArt.varId"), info={'t':'e', 'e':'VarianteArt'})
    
    variante = relationship('VarianteArt')

    def __str__(self):
        return "<ModificadorArt (Ref='%s', Nombre='%s', id_variante='%s')>" % (self.ref, self.nombre, str(self.varianteId))

    
class ArtEscandallo (Base):
    __tablename__ = 'ArtEscandallo'
    
    articulo = Column('areArticulo', Integer, ForeignKey("Articulos.artId"), primary_key=True)
    proceso = Column('areProceso', Integer, ForeignKey("Procesos.proId"), primary_key=True)


class ArticuloDespiece (Base):
    __tablename__ = 'ArticulosDespieces'
    
    articuloId = Column('artdeArticulo', Integer, ForeignKey("Articulos.artId"), primary_key=True)
    id = Column('artdeId', Integer, primary_key=True)
    orden = Column('artdeOrden', SmallInteger)
    ref = Column('artdeRef', String(3))
    pieza = Column('artdePieza', String(30))
    materialId = Column('artdeMaterial', Integer, ForeignKey("Articulos.artId"))
    medida1 = Column('artdeMedida1', Float(6))
    medida2 = Column('artdeMedida2', Float(6))
    area = Column('artdeArea', Float(6))
    descripcion = Column('artdeDescripcion', String(50))
    
    def __repr__ (self):
        return '<ArticuloDespiece (Articulo=%s, Ref=%s, Material=%s)>'  % (self.articuloId, self.ref, self.materialId)
    
class ArticuloStock (Base):
    __tablename__ = 'ArticulosStock'
    
    artstId = Column(Integer, primary_key=True)
    artstArticulo = Column(Integer)
    artstModificador1 = Column(Integer)
    artstModificador2 = Column(Integer)
    artstModificador3 = Column(Integer)
    artstStock = Column(SmallInteger)
    
    def __repr__(self):
        return "<Stock (Articulo='%s', Modificador='%s')>" % (self.artstArticulo, self.artstModificador1)
    


''' Sección para clientes y su documentación '''

class Cliente (Base):
    __tablename__ = 'Clientes'
    
    id = Column('cliId', Integer, primary_key=True)
    ref = Column('cliRef', String(20), nullable=False, unique=True, info={'t':'t'})
    nombre = Column('cliNombre', String(100), nullable=False, unique=False, info={'t':'t'})
    nombreFiscal = Column('cliNombreFiscal', String(150), info={'t':'t'})
    direccion = Column('cliDireccion', String(150), info={'t':'t'})
    
    # RelationsShip
    #pedidos = relationship('Pedidos', back_populates='cliente')
    
class Pedido (Base):
    __tablename__ = 'Pedidos'
    
    id = Column('pedId', Integer, primary_key=True)
    cliente = Column('pedCliente', Integer, ForeignKey("Clientes.cliId"), nullable=False, info={'t':'e', 'e':'Cliente'})
    contacto = Column('pedContacto', String(75), info={'t':'t'})
    telefono = Column('pedContTelefono', String(12), info={'t':'t'})
    mail = Column('pedContMail', String(100), info={'t':'t'})
    
    lineas = relationship("PedidoLineas", info={'t':'l'})
    
    def __repr__(self):
        return "<Pedidos (id='%s', Clliente='%s')>" % (self.id, self.cliente)
    
class PedidoLineas (Base):
    __tablename__ = 'PedidosLineas'
    
    Pedido = Column('pedliPedido', Integer, ForeignKey("Pedidos.pedId"), nullable=False, primary_key=True)
    id = Column('pedliId', Integer, primary_key=True)
    orden = Column('pedliOrden', SmallInteger, info={'t':'o'})
    articulo = Column('pedliArticulo', Integer, ForeignKey("Articulos.artId"), nullable=False, info={'t':'e', 'e':'Articulo'}) 
    artRef = Column('pedliArtRef', String(20), info={'t':'t'})
    

class Proveedor (Base):
    __tablename__ = 'Proveedores'
    
    id = Column('proId', Integer, primary_key=True)
    ref = Column('proRef', String(20), nullable=False, unique=True, info={'t':'t'})
    nombre = Column('proNombre', String(100), nullable=False, unique=False, info={'t':'t'})
    nombreFiscal = Column('proNombreFiscal', String(150), info={'t':'t'})
    direccion = Column('proDireccion', String(150), info={'t':'t'})
    
    # RelationsShip
    #pedidos = relationship('Pedidos', back_populates='cliente')    
    
