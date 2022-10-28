if __name__ == '__main__':
    import pyodbc
    
    cnxn = pyodbc.connect("DRIVER={SQL Server};"
                          "SERVER=192.168.2.4\BASEGES;"
                          "DATABASE=00000001DISTRIBUCION;"
                          "UID=usuarios;"
                          "PWD=passusuarios;")
    

    cursor = cnxn.cursor()
    
    total = 0    
    for row in cursor.tables():
        if 'ARTICUL' in row.table_name:
            print(row.table_name)
            total += 1
    print ("Total Procesados: ", total)
        
    total = 0
    cursor.execute("SELECT * FROM TARTICULOS")
    for row in cursor.fetchall():
        print(row)
        total += 1
    print ("Total Procesados: ", total)  
           
 
    
                