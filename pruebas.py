
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
    
    mst = mnj.nuevoMaestro('Articulos.Modificador', almacenar=False)

    mstl1 = mnj.cargaLista(mst_ref=mst)

    mst2 = mnj.nuevoMaestro('Articulos.Variante', almacenar=False)

    mstl2 = mnj.cargaLista(mst_ref=mst2)
    
    print (mstl1)

    mnj.cargaLista(tipo='Articulos.Variante', campos_lista=['ref', 'nombre'])