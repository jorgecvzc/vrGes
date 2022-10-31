'''
Created on 27 dic. 2018

@author: Jorante
'''
import sys
import configparser

from almacen import ControlUinfs

class Gestion(object):
    
    def __init__(self, ruta):
        #import os, inspect
        #dirconf = os.path.dirname(inspect.getfile(inspect.currentframe()))
        import pathlib

        dirconf = str(pathlib.Path(__file__).parent.absolute())
        
        # Ruta de la aplicación de donde se podrán extraer todas las configuraciones y accesos a elementos propios
        if dirconf and (dirconf[-1] != '/'):
            dirconf = dirconf + '/'        
        self.rutaApp = dirconf + '/' + ruta + '/'

        # Carga el archivo de configuración
        self.iniConfig = configparser.ConfigParser()
        self.iniConfig.read(self.rutaApp+'config.ini')
        self.cUInf = ControlUinfs(self.iniConfig["BD"])

def main():
    g = Gestion('..')

    if 'generabd' in sys.argv:
        g.cUInf.generaBD()


if __name__ == "__main__":
    main()

    def imps():
        print('== '+str(mnj.session)+' ==')
        for s in mnj.session:
            print (s)
        print('============================')
    g = Gestion('..')    
        
    mnj = g.cUInf.mnjMaestros()
    mst = mnj.nuevoMaestro('VarianteArt')

    #res = mnj.buscaMaestro(mst)[0]
    
    #print(res.variante)
        
    mst['ref'] = 'TGEN'
    mst['nombre'] = 'TALLA GENÉRICA'
    
    imps()
    '''
    

    
    mnj.guardaCambios()

    imps()
        
    
    mst = mnj.nuevoMaestro('VarianteArt')
    mst._camposVal['ref'] = 'ref11'
    print(mst._camposVal._camposModif)

    mst.CargaDatos()
    mst._camposVal[0]['ref'] = 'ref22'
    imps()

    
    mst = mnj.nuevoMaestro('ModificadorArt')
    mst._camposVal['ref'] = 'PRUB'
    mst.CargaDatos()
    #mst._camposVal[0].nombre='aa'
    mst._camposVal[0].variante.nombre='dD'

    print(mst._camposVal[0].variante)
    
    #mst.GuardaDatos()
    # mst._mnj.almInf.session.commit()


    '''
