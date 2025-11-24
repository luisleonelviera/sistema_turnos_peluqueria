# db.py - Manejo de archivos CSV

from models import registro

class transforma(object):
    def __init__(self, atributos, tipo_registro=None):
        self.keys = atributos
        self.tipo_registro = tipo_registro or registro
    
    def toobject(self, values):
        if len(values) < len(self.keys):
            return None
        datos = {}
        for i in range(len(values)):
            key = self.keys[i].strip()
            value = values[i].strip()
            datos[key] = value
        return self.tipo_registro(**datos)


class db(object):
    def __init__(self, filename, tipo_registro=registro):
        self.filename = filename
        self.tipo_registro = tipo_registro
    
    def read(self):
        objetos = []
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lineas = file.readlines()
                if len(lineas) <= 1:
                    return objetos
                keys = lineas[0].strip().split(",")
                tran = transforma(keys, self.tipo_registro)
                for linea in lineas[1:]:
                    if linea.strip():
                        valores = linea.strip().split(",")
                        obj = tran.toobject(valores)
                        if obj:
                            objetos.append(obj)
        except FileNotFoundError:
            pass
        return objetos
    
    def write(self, registros):
        if not registros:
            return
        keys = registros[0].__dict__.keys()
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write(",".join(keys) + "\n")
            for obj in registros:
                valores = [str(getattr(obj, k, "")) for k in keys]
                file.write(",".join(valores) + "\n")