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

from .uInfs import Base, Maestro


''' Sección para los Artículos '''

class Variante (Maestro, Base):
    __tablename__ = 'VariantesArt'
    
    id = Column('varId', Integer, primary_key=True)
    ref = Column('varRef', String(6), nullable=False, info={'t':'t'})
    nombre = Column('varNombre', String(50), info={'t':'t'})

    def __str__(self):
        return "<mst: Articulo.Variante (Ref='%s', Nombre='%s')>" % (self.ref, self.nombre)


class Modificador (Maestro, Base):
    __tablename__ = 'ModificadoresArt'
    
    id = Column('moaId', Integer, primary_key=True)
    ref = Column('moaRef', String(6), nullable=False)
    nombre = Column('moaNombre', String(50))
    varianteId = Column('moaVariante', Integer, ForeignKey("VariantesArt.varId"))
    
    variante = relationship('Variante')

    def __str__(self):
        return "<mst: Articulo.Modificador (Ref='%s', Nombre='%s', id_variante='%s')>" % (self.ref, self.nombre, str(self.varianteId))
        

class Articulo (Maestro, Base):
    __tablename__ = 'Articulos'
 
    id = Column('artId', Integer, primary_key=True)
    ref = Column('artRef', String(20), nullable=False, unique=True)
    refAsociada = Column('artRefAsociada', String(20), nullable=True)
    nombre = Column('artNombre', String(100), default='')
    descripcion = Column('artDescripcion', String(250), nullable=True)
    precio = Column('artPrecio', Float(6), default = 0.0)
    beneficio = Column('artBeneficio', Float(6), nullable=True)
    precioCompra = Column('artPrecioCompra', Float(6), nullable=True)
    observaciones = Column('artObservaciones',Text, nullable=True)
    proveedorId = Column('artProveedor', Integer, ForeignKey("Proveedores.proId"))
    
    proveedor = relationship('Proveedor')
    
    numVariantes = Column('artNumVariantes', SmallInteger, default=0)
    variante1 = Column('artVariante1', Integer, ForeignKey("VariantesArt.varId"))
    variante2 = Column('artVariante2', Integer, ForeignKey("VariantesArt.varId"))
    variante3 = Column('artVariante3', Integer, ForeignKey("VariantesArt.varId"))
    
    #manufacturado = Column('artManufacturado', Boolean, server_default=false(), nullable=False)
    manufacturado = Column('artManufacturado', Boolean, default=False)
    escandallo = relationship('Escandallo', back_populates="articulo", uselist=False)
    
    '''Column('moaVariante', Integer, ForeignKey("VariantesArt.varId"), info={'t':'e', 'e':'VarianteArt'})
    
    variante = relationship('Variante')
    
    control = Column('artControl', SmallInteger, default=0)
    
    '''
    def __str__(self):
        return "<Articulo (Ref='%s', Nombre='%s')>" % (self.ref, self.nombre)    


class Escandallo (Base):
    __tablename__ = 'ArtEscandallos'
    
    articuloId = Column('areId', Integer, ForeignKey("Articulos.artId"), primary_key=True)
    articulo = relationship('Articulo', back_populates="escandallo")
    proceso = Column('areProceso', Integer, ForeignKey("Procesos.proId"))
    despiece = relationship('EscandalloDespiece')


class EscandalloDespiece (Base):
    __tablename__ = 'ArtEscDespieces'
    
    escandalloId = Column('aredeEscandallo', Integer, ForeignKey("ArtEscandallos.areId"), primary_key=True)
    id = Column('aredeId', Integer, primary_key=True)
    orden = Column('aredeOrden', SmallInteger)
    ref = Column('aredeRef', String(3))
    pieza = Column('aredePieza', String(30))
    materialId = Column('aredeMaterial', Integer, ForeignKey("Articulos.artId"))
    medida1 = Column('aredeMedida1', Float(6))
    medida2 = Column('aredeMedida2', Float(6))
    area = Column('aredeArea', Float(6))
    descripcion = Column('aredeDescripcion', String(50))
    
    def __str__ (self):
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
    

class Proveedor (Maestro, Base):
    __tablename__ = 'Proveedores'
    
    id = Column('proId', Integer, primary_key=True)
    ref = Column('proRef', String(20), nullable=False, unique=True, info={'t':'t'})
    nombre = Column('proNombre', String(100), nullable=False, unique=False, info={'t':'t'})
    nombreFiscal = Column('proNombreFiscal', String(150), info={'t':'t'})
    direccion = Column('proDireccion', String(150), info={'t':'t'})
    
    # RelationsShip
    #pedidos = relationship('Pedidos', back_populates='cliente')    
    
