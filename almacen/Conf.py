from sqlalchemy.inspection import inspect
from sqlalchemy.orm import InstrumentedAttribute

from .tblsArticulos import *

from unidadesInf import tipoUInf


class Conf ():
    
    def __init__(self):
        pass
    
    def almacenUInf (self, nombre_uinf):
        return eval(nombre_uinf+'()')
        
    def cargaCamposUInf(self, tipo_uinf, nombre_uinf, **kwargs):
                       
        tabla = eval(nombre_uinf)
        tablaInf = inspect(tabla)
        
        # Inicia las listas de campos del maestro a cargar
        camposId = []
        listaCampos = kwargs.pop('lista_campos', tablaInf.attrs.keys())

        # Genera una nueva unidad de información con los parámetros restantes
        if (tipo_uinf == tipoUInf.MAESTRO):
            uinf = ControlMaestro().nuevoMaestro(nombre_uinf, kwargs)
        elif (tipo_uinf in [tipoUInf.CONS_MAESTRO, tipoUInf.CONS_RANGO_MSTS]):
            uinf = ControlMaestro().nuevaConsultaMaestro(nombre_uinf, kwargs)
        elif (tipo_uinf == tipoUInf.CAMPO_LINEAS):
            uinf = ControlMaestro().nuevoCampoLineas(nombre_uinf, kwargs)
        
        # Recorre los campos de la configuración y los crea en el objeto
        for nombreCampo in listaCampos:
            campo = getattr(tabla, nombreCampo)

            if getattr(campo, 'primary_key', False):
                camposId.append(nombreCampo)
            else:
                tipo = campo.info['t']
                
                # Se cargan los diferenctes parámetros dependiendo del tipo de campo
                parametros = {}
                    
                # Se carga el valor inicial para los campos especiales
                if (tipo == 'l'): # Campo de líneas
                    parametros['valor'] = self.cargaCamposUInf('cl', campo.prop.argument)
                    parametros["objeto"] = campo.prop.argument
                elif (tipo == 'w'): # Si es un campo complementario lineas y se ha pedido su inicialización se carga el maestro 'w' vacío
                    # parametros['valor'] = self.nuevoCampoWLineas('cw', uinf_conf[campo.valor[0].id[0]].valor, campo.valor, etiqueta=campo, t_senyal=uinf._tSenyales[0])
                    # Se añade el campo de busqueda al campo externo para que cuando se cambie modifique las líneas del complementario. El externo siempre se ha de definir con anterioridad
                    uinf._modifCampo(campo.valor[0].id[0], 'busqueda', (campo,))
                    tipo = 'l'                
                elif (tipo == 'a'): # Si es un adjunto el valor por defecto será el adjunto con sus campos ya creados
                    parametros['valor'] = self.nuevoMaestro(campo.valor.almacen, etiqueta=campo, t_senyal=uinf._tSenyales[0])
                
                if (tipo in ['e','a']):
                    parametros["objeto"] = campo.info['e']
                        
                # Se crea el nuevo campo con sus parámetros, si los tuviera
                uinf._nuevoCampo(nombreCampo, tipo, **parametros)
        
        uinf._camposModif = []
        uinf._asignaCamposId(tuple(camposId))    
      
        uinf.setEtiqueta(kwargs.pop('etiqueta', ''))

        if kwargs.get('t_senyal', None):
            uinf.asignaTunelSenyal(kwargs['t_senyal'])
        else:
            uinf.asignaTunelSenyal(None)
        
        return uinf        
        
    
    