from datetime import datetime
import pyodbc
import re
from vrGes import Gestion

inicio = datetime.now()

cnxn = pyodbc.connect("DRIVER={SQL Server};"
                      "SERVER=192.168.2.2\BASEGES;"
                      "DATABASE=00000001DISTRIBUCION;"
                      "UID=usuarios;"
                      "PWD=passusuarios;")


cursor = cnxn.cursor()
for row in cursor.tables():
    if 'ARTICUL' in row.table_name:
        print(row.table_name)

cursor.execute("SELECT COUNT(*) AS C FROM TARTICULOS ")
total = cursor.fetchone()[0]

'TARTICULOS1 As Ref, TARTICULOS2 As RefAsoc, TARTICULOS4 As Nombre, TARTICULOS5 As Distr, TARTICULOS6 As Descr, TARTICULOS10 As IVA, TARTICULOS11 As FechaUltModif, TARTICULOS12 As PTarifa, TARTICULOS14 As PUltCompra'
cursor.execute("SELECT TARTICULOS1, TARTICULOS4 As Nombre, TARTICULOS6 As Descr,TARTICULOS12 As PTarifa, TARTICULOS14 As PUltCompra, "
               "TARTICULOS17, TARTICULOS19, TARTICULOS21 FROM TARTICULOS ")

# Crea un manejador para añadir los productos
mnj = Gestion('..').cUInf.mnjMaestros()
articulo_busqueda = mnj.nuevoMaestro('Articulos.Articulo', almacena=False)
almacena = False

i, j, k, progreso = 0, 0, 0, 0
for row in cursor.fetchall():
    progreso += 1
    
    ref = ''
    if row[0][0:3] == 'ERR':
        pass
    
    elif row[0].find('_') > -1:
        ref = row[0][:row[0].find('_')]
        
    elif (re.search('^.*T[0-9][0-9]$', row[0])):
        # Referencias que terminen con una talla de tipo numérica
        ref = row[0][:len(row[0])-3]

    elif (row[0][0:3] in ['PBO', 'BOL']):
        ref = row[0]

    else:
        ref_unicas = ['ADVCHALECO', 'JHATEXAS', 'JOMGNINITRIBOG', 'JOMGPLPOLIDY']
        for ref_unica in ref_unicas:
            if (row[0][0:len(ref_unica)] == ref_unica):
                ref = row[0][0:len(ref_unica)]

    if ref:
        i += 1            
        articulo_busqueda['ref'] = ref 
        articulo = mnj.cargaMaestro(mst_ref=articulo_busqueda)

        if not articulo:
            articulo = mnj.nuevoMaestro('Articulos.Articulo')
            alnacena = True
            i += 1
        else:
            almacena = False
            j += 1

        articulo['ref'] = ref
        articulo['nombre'] = row[1].replace("'", "''")
        articulo['descripcion'] = row[2][0:200].replace("'", "''")
        articulo['precio'] = row[3]
        articulo['precioCompra'] = row[4]
        articulo['manufacturado'] = False
        #articulo['control'] = 1

        if not(progreso%100) or almacena:
            print('======== ' + str(total-progreso) + ' == Procesados: ', j,  '== Session: ' + str(len(list(mnj.session))))    

            mnj.almacena()
            mnj.descarta()
        
    elif (row[0][0:3] != 'ERR'):
        k += 1
        # print ('----->', row[0], row[1])
              
print ("Total Procesados: ", total, "", "Insertadas: ", i, "", "Actualizados: ", j, "", "Sin Procesar: ", k, " Tiempo:", datetime.now()-inicio)  
       


            