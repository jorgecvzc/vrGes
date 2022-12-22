from datetime import datetime
import pyodbc
from vrGes import Gestion

inicio = datetime.now()
    
cnxn = pyodbc.connect("DRIVER={SQL Server};"
                      "SERVER=PCOF01\BASEGES;"
                      "DATABASE=00000001DISTRIBUCION;"
                      "UID=usuarios;"
                      "PWD=passusuarios;")


cursor = cnxn.cursor()
for row in cursor.tables():
    if 'PROV' in row.table_name:
        print(row.table_name)

cursor.execute("SELECT COUNT(*) AS C FROM TPROVEEDORES")
total = cursor.fetchone()[0]

'''TPROVEEDORES1 As idpro, TPROVEEDORES2 As NombreFiscal, TPROVEEDORES4 As NombreHabitual, TPROVEEDORES5 As Direccion, TPROVEEDORES6 As CP, TPROVEEDORES7 As Poblacion, TPROVEEDORES8 As
Provincia, TPROVEEDORES9 As Pais, TPROVEEDORES10 As Tlfno1, TPROVEEDORES11 As Tlfno2, TPROVEEDORES12 As Web, TPROVEEDORES13 As Mail, TPROVEEDORES14 As CIF'''
cursor.execute('SELECT TPROVEEDORES1 As idpro, TPROVEEDORES2 As NombreFiscal, TPROVEEDORES4 As NombreHabitual, TPROVEEDORES5 As Direccion, TPROVEEDORES6 As CP, TPROVEEDORES7 As Poblacion, TPROVEEDORES8 As Provincia, TPROVEEDORES9 As Pais, TPROVEEDORES10 As Tlfno1, TPROVEEDORES11 As Tlfno2, TPROVEEDORES12 As Web, TPROVEEDORES13 As Mail, TPROVEEDORES14 As CIF FROM TPROVEEDORES')
           
# Crea un manejador para añadir los productos
mnj = Gestion('..').cUInf.mnjMaestros()
proveedor_busqueda = mnj.nuevoMaestro('Personas.Proveedor', almacenar=False)
almacena = False

i, j, k, progreso = 0, 0, 0, 0
for row in cursor.fetchall():
    idc= int(row[0])
    proveedor_busqueda['ref'] = str(idc) 
    proveedor = mnj.cargaMaestro(mst_ref=proveedor_busqueda, vaciado=False)
    if not proveedor:
        proveedor = mnj.nuevoMaestro('Personas.Proveedor')
        i += 1          
    else:
        j += 1
    proveedor['ref'] = str(idc)
    proveedor['nombre'] = row[2].replace("'", "''")
    proveedor['nombreFiscal'] = row[1].replace("'", "''")
    if not proveedor['nombre']:
        proveedor['nombre'] = proveedor['nombreFiscal']        
    proveedor['direccion'] = row[3].replace("'", "''")

    if not(progreso%100) or almacena:
        print('======== ' + str(total-progreso) + ' == Procesados: ', progreso,  '== Session: ' + str(len(list(mnj.session))))
        mnj.almacena()
        mnj.descarta()
        
    progreso += 1
 
print ("Total Procesados: ", total, "", "Insertadas: ", i, "", "Sin Procesar: ", total-i-j, datetime.now()-inicio)  


