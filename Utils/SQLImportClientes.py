from datetime import datetime
import pyodbc
from vrGes import Gestion

inicio = datetime.now()

cnxn = pyodbc.connect("DRIVER={SQL Server};"
                      "SERVER=192.168.2.2\BASEGES;"
                      "DATABASE=00000001DISTRIBUCION;"
                      "UID=usuarios;"
                      "PWD=passusuarios;")


cursor = cnxn.cursor()
for row in cursor.tables():
    if 'CLIENT' in row.table_name:
        print(row.table_name)
        
cursor.execute("SELECT COUNT(*) AS C FROM TCLIENTES")
total = cursor.fetchone()[0]

'''TCLIENTES1 As idcli, TCLIENTES2 As NombreFiscal, TCLIENTES4 As NombreHabitual, TCLIENTES5 As Direccion, TCLIENTES6 As CP, TCLIENTES7 As Poblacion, TCLIENTES8 As
Provincia, TCLIENTES9 As Pais, TCLIENTES10 As Tlfno1, TCLIENTES11 As Tlfno2, TCLIENTES12 As Web, TCLIENTES13 As Mail, TCLIENTES14 As CIF'''
cursor.execute('SELECT TCLIENTES1 As idcli, TCLIENTES2 As NombreFiscal, TCLIENTES4 As NombreHabitual, TCLIENTES5 As Direccion, TCLIENTES6 As CP, TCLIENTES7 As Poblacion, TCLIENTES8 As Provincia, TCLIENTES9 As Pais, TCLIENTES10 As Tlfno1, TCLIENTES11 As Tlfno2, TCLIENTES12 As Web, TCLIENTES13 As Mail, TCLIENTES14 As CIF FROM TCLIENTES')
           
# Crea un manejador para añadir los productos
mnj = Gestion('..').cUInf.mnjMaestros()
cliente_busqueda = mnj.nuevoMaestro('Personas.Cliente', almacenar=False)
almacena = False

i, j, k, progreso = 0, 0, 0, 0
for row in cursor.fetchall():
    idc= int(row[0]) 
    cliente_busqueda['ref'] = str(idc) 
    cliente = mnj.cargaMaestro(mst_ref=cliente_busqueda, vaciado=False)
    if not cliente:
        cliente = mnj.nuevoMaestro('Personas.Cliente')
        i += 1
    else:
        j += 1
    cliente['ref'] = str(idc) 
    cliente['nombre'] = row[2].replace("'", "''")
    cliente['nombreFiscal'] = row[1].replace("'", "''")
    if not cliente['nombre']:
        cliente['nombre'] = cliente['nombreFiscal']        
    cliente['direccion'] = row[3].replace("'", "''")

    if not(progreso%100) or almacena:
        print('==== Pendientes: ' + str(total-progreso) + ' == Procesados: ', progreso,  '== Session: ' + str(len(list(mnj.session))))    
        mnj.almacena()
        mnj.descarta()

    progreso += 1
        
print ("Total Procesados: ", total, "", "Insertadas: ", i, "", "Actualizados: ", j, "", "Sin Procesar: ", k, " Tiempo:", datetime.now()-inicio)   


