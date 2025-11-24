# models.py - Aquí van todas las clases de datos

class registro(object):
    def __init__(self, **kwargs):
        for clave, valor in kwargs.items():
            setattr(self, clave, valor)
    
    def __str__(self):
        attrs = [f"{k}: {v}" for k, v in self.__dict__.items()]
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class Cliente(registro):
    keys = ["dni", "nombre", "apellido", "email", "telefono"]


class Profesional(registro):
    keys = ["id", "nombre", "estado"]


class Slot(registro):
    keys = ["profesional_id", "fecha", "hora", "disponible"]


class Turno(registro):
    keys = ["id", "cliente_dni", "profesional_id", "fecha", "hora", "servicio"]