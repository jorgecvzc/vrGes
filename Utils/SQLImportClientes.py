from Manejadores import Control

if __name__ == '__main__':
    import pyodbc
    from configparser import ConfigParser
    
    cnxn = pyodbc.connect("DRIVER={SQL Server};"
                          "SERVER=192.168.2.2\BASEGES;"
                          "DATABASE=00000001DISTRIBUCION;"
                          "UID=usuarios;"
                          "PWD=passusuarios;")
    

    cursor = cnxn.cursor()
    for row in cursor.tables():
        if 'CLIENT' in row.table_name:
            print(row.table_name)
    
    '''TCLIENTES1 As idcli, TCLIENTES2 As NombreFiscal, TCLIENTES4 As NombreHabitual, TCLIENTES5 As Direccion, TCLIENTES6 As CP, TCLIENTES7 As Poblacion, TCLIENTES8 As
    Provincia, TCLIENTES9 As Pais, TCLIENTES10 As Tlfno1, TCLIENTES11 As Tlfno2, TCLIENTES12 As Web, TCLIENTES13 As Mail, TCLIENTES14 As CIF'''
    cursor.execute('SELECT TCLIENTES1 As idcli, TCLIENTES2 As NombreFiscal, TCLIENTES4 As NombreHabitual, TCLIENTES5 As Direccion, TCLIENTES6 As CP, TCLIENTES7 As Poblacion, TCLIENTES8 As Provincia, TCLIENTES9 As Pais, TCLIENTES10 As Tlfno1, TCLIENTES11 As Tlfno2, TCLIENTES12 As Web, TCLIENTES13 As Mail, TCLIENTES14 As CIF FROM TCLIENTES')
               
    # Crea un manejador para añadir los productos
    cm = Control('..')
    mnj = cm.nuevoManejador()
    cliente_busqueda = mnj.nuevoMaestro('Cliente')

    i, j, k, total = 0, 0, 0, 0
    for row in cursor.fetchall():
        total += 1

        idc= int(row[0]) 
        cliente_busqueda['ref'] = str(idc) 
        cliente = mnj.cargaMaestro('Cliente', mst_ref=cliente_busqueda)
        if not cliente:
            cliente = mnj.nuevoMaestro('Cliente')
            i += 1
        else:
            j += 1
        cliente['ref'] = str(idc) 
        cliente['nombre'] = row[2].replace("'", "''")
        cliente['nombreFiscal'] = row[1].replace("'", "''")
        if not cliente['nombre']:
            cliente['nombre'] = cliente['nombreFiscal']        
        cliente['direccion'] = row[3].replace("'", "''")
        mnj.almacenaMaestro(cliente)
     


        # bdCon.actualiza("Clientes", ["cliNombre", "cliNombreFiscal", "cliDireccion"], [row[2].replace('"', '\\"'), row[1].replace('"', '\\"'), row[3].replace('"', '\\"')], 'cliId=' + str(int(idc))):
    
    print ("Total Procesados: ", total, "", "Insertadas: ", i, "", "Actualizados: ", j, ". Borradas Locales: ", 0)  


