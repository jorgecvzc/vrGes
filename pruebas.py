
from vrGes import Gestion
if __name__ == "__main__":
    def imps(mnj):
        print('== '+str(mnj.session)+' ==')
        for s in mnj.session:
            print (s)
        print('============================')
    
    
    g = Gestion('..')    
    mnj = g.cUInf.mnjMaestros()
    mnjc = g.cUInf.mnjConsultas()
    sss = mnj.session
    
    mst = mnj.nuevoMaestro('Trabajos.Proceso')
    mst.nuevaLinea('tareas')
    mst['tareas'][0]['tareaRef'] = 'a'

    for l in mst.tareas:
        print (l)
