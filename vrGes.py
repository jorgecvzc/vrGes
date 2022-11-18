'''
Created on 27 dic. 2018

@author: Jorante
'''
import sys
import configparser

from Utils import BDMantenimiento

from almacen import ControlUinfs
from Interfaz.mnjMwVRGES import MainWindow, QtWidgets


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
        BDMantenimiento.CreaTablas(g.cUInf.bd)

    elif 'borrabd' in sys.argv:
        BDMantenimiento.BorraTablas(g.cUInf.bd)
        
    else:
        app = QtWidgets.QApplication(sys.argv)
        ui = MainWindow(g.cUInf)
        ui.show()
        sys.exit(app.exec_())        


if __name__ == "__main__":
    main()
