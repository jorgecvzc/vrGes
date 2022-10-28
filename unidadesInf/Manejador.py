'''
Created on 13 nov. 2018

@author: cortesj

Modulo Maestros
    El módulo Maestros contiene todas las clases para el trabajo con objetos que representan los elelmentos reales que debe procesar la aplicación, tales como
    artículos, clientes, proveedores... En este módulo no se engloban los diferentes documentos que tienen su propio módulo 
'''

from .DefMaestros import Maestro, CampoLineas, ConsultaMaestro, tipoUInf
        
class Pedido(Maestro):
    '''
    Maestro de Pedidos Clientes. Funciones y opreaciones especiales
    '''
    def __init__(self, etiq, mnj=None):
        Maestro.__init__(self, 'Pedido', mnj)

    # Cálculo del total sin IVA de todas las lineas del Pedido
    def totalSinIVA(self):
        total = 0
        lineas = self['lineas']
        for i in range(self['lineas'].numeroFilas()):
            if (lineas['cantidad'][i] != None) and (lineas['precio'][i] != None):
                total += float(lineas['cantidad'][i])*float(lineas['precio'][i])
        return total
        

class MnjUInfs(object):
    maestrosDef = ['Pedido']
    
    def __init__ (self, manejador_almacen):
        self.mnjAlm = manejador_almacen
    
    def nuevoMaestro(self, tipo):
        if (tipo in self.maestrosDef):
            return eval(tipo + '('+str(self.mnjAlm)+')')
        else:
            return Maestro(tipo, self.mnjAlm)
        
    def nuevoCampoLineas(self, nombre, manejador=None):
        return CampoLineas(nombre, manejador)

    def nuevaConsultaMaestro(self, nombre, manejador=None):
        return ConsultaMaestro(nombre, manejador)    

### Zona de pruebas
if __name__ == '__main__':
    pass
