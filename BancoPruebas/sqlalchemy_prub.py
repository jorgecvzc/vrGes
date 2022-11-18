from sqlalchemy import create_engine
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from Almacen.bdTblsArticulos import *   

engine = create_engine('postgresql://postgres:pVRB2018.@192.168.2.200:5432/bdVRGes') # , echo=True
        


'''from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('select "varRef" from "VariantesArt"'))
    print(result.all())

'''        

for column in ArticulosStock.__table__.columns:
    print (column)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

session = Session()
var1 = VariantesArt(ref='GEN', nombre='GENERAL')
print(var1.id)

reg = session.query(Pedidos).all()
print(reg[0].cliente)

#reg = session.query(Clientes).filter_by(id=2).first()
#print(reg.pedidos)

# session.commit()

a = Articulos()
a.ref = 'A'
print (a.__dict__.keys())