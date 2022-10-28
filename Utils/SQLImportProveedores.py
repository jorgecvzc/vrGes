from Manejadores import Control


if __name__ == '__main__':
    import pyodbc
        
    cnxn = pyodbc.connect("DRIVER={SQL Server};"
                          "SERVER=PCOF01\BASEGES;"
                          "DATABASE=00000001DISTRIBUCION;"
                          "UID=usuarios;"
                          "PWD=passusuarios;")
    

    cursor = cnxn.cursor()
    for row in cursor.tables():
        if 'PROV' in row.table_name:
            print(row.table_name)
    
    '''TPROVEEDORES1 As idpro, TPROVEEDORES2 As NombreFiscal, TPROVEEDORES4 As NombreHabitual, TPROVEEDORES5 As Direccion, TPROVEEDORES6 As CP, TPROVEEDORES7 As Poblacion, TPROVEEDORES8 As
    Provincia, TPROVEEDORES9 As Pais, TPROVEEDORES10 As Tlfno1, TPROVEEDORES11 As Tlfno2, TPROVEEDORES12 As Web, TPROVEEDORES13 As Mail, TPROVEEDORES14 As CIF'''
    cursor.execute('SELECT TPROVEEDORES1 As idpro, TPROVEEDORES2 As NombreFiscal, TPROVEEDORES4 As NombreHabitual, TPROVEEDORES5 As Direccion, TPROVEEDORES6 As CP, TPROVEEDORES7 As Poblacion, TPROVEEDORES8 As Provincia, TPROVEEDORES9 As Pais, TPROVEEDORES10 As Tlfno1, TPROVEEDORES11 As Tlfno2, TPROVEEDORES12 As Web, TPROVEEDORES13 As Mail, TPROVEEDORES14 As CIF FROM TPROVEEDORES')
               
    cm = Control('..')

    i, j, total = 0, 0, 0 
    for row in cursor.fetchall():
        total += 1
        idc= int(row[0])
        existe = cm.almacen.Inf.selecciona(['"Proveedores"'], ['*'], '"proRef"='+"'"+row[0].replace("'", "''")+"'", [], 1).fetchone()
        if not existe:
            i += 1
            cm.almacen.Inf.inserta(
                '"Proveedores"',
                ['"proRef"', '"proNombre"', '"proNombreFiscal"', '"proDireccion"'],
                ["'"+row[0].replace("'", "''")+"'", "'"+row[2].replace("'", "''")+"'", "'"+row[1].replace("'", "''")+"'", "'"+row[3].replace("'", "''")+"'"],
            )
            print(row)            
        else:
            if cm.almacen.Inf.actualiza(
                '"Proveedores"', 
                ['"proNombre"', '"proNombreFiscal"', '"proDireccion"'], 
                ["'"+row[2].replace("'", "''")+"'", "'"+row[1].replace("'", "''")+"'", "'"+row[3].replace("'", "''")+"'"],
                '"proId"=' + str(int(idc))
            ):
                j += 1
    
    nb = 0
    #nb = bdCon.borra("Proveedores", 'proNombre="###"')
            
    print ("Total Procesados: ", total, "", "Insertadas: ", i, "", "Sin Procesar: ", total-i-j, ". Borradas Locales: ", nb)  


