# peluqueria.py - Lógica principal del sistema

from datetime import datetime
from models import Cliente, Profesional, Slot, Turno
from db import db
from utils import crea_csv

class Peluqueria:
    def __init__(self):
        self.clients_filename = "clients.csv"
        self.profesionales_filename = "profesionales.csv"
        self.slots_filename = "slots.csv"
        self.turns_filename = "turns.csv"

        # Crear archivos si no existen
        for archivo, claves in [
            (self.clients_filename, Cliente.keys),
            (self.profesionales_filename, Profesional.keys),
            (self.slots_filename, Slot.keys),
            (self.turns_filename, Turno.keys)
        ]:
            try:
                open(archivo, "r").close()
            except:
                crea_csv(archivo, claves)

        # Bases de datos
        self.clients_db = db(self.clients_filename, Cliente)
        self.profesionales_db = db(self.profesionales_filename, Profesional)
        self.slots_db = db(self.slots_filename, Slot)
        self.turns_db = db(self.turns_filename, Turno)

        # Cargar datos
        self.clients = self.clients_db.read()
        self.profesionales = self.profesionales_db.read()
        self.slots = self.slots_db.read()
        self.turns = self.turns_db.read()

        # Crear 4 profesionales por defecto si no hay ninguno
        if not self.profesionales:
            nombres = ["Carlos", "Laura", "Mónica", "Diego"]
            for i in range(4):
                prof = Profesional(id=str(i+1), nombre=nombres[i], estado="activo")
                self.profesionales.append(prof)
            self.profesionales_db.write(self.profesionales)

    def guardar_todo(self):
        self.clients_db.write(self.clients)
        self.profesionales_db.write(self.profesionales)
        self.slots_db.write(self.slots)
        self.turns_db.write(self.turns)

    def registrar_cliente(self):
        print("\n--- REGISTRAR CLIENTE ---")
        dni = input("DNI: ").strip()
        if any(c.dni == dni for c in self.clients):
            print("¡Cliente ya existe!")
            return
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        email = input("Email: ").strip()
        telefono = input("Teléfono: ").strip()
        cliente = Cliente(dni=dni, nombre=nombre, apellido=apellido, email=email, telefono=telefono)
        self.clients.append(cliente)
        print("Cliente registrado con éxito")

    def gestionar_profesionales(self):
        while True:
            print("\n--- PROFESIONALES ---")
            for p in self.profesionales:
                estado = "ACTIVO" if p.estado == "activo" else "INACTIVO"
                print(f"  {p.id}. {p.nombre} → {estado}")
            
            print("\n1. Agregar profesional")
            print("2. Cambiar estado")
            print("3. Volver")
            op = input("Opción: ")
            
            if op == "1":
                nombre = input("Nombre: ").strip()
                if not nombre:
                    continue
                nuevo_id = str(max(int(p.id) for p in self.profesionales) + 1)
                prof = Profesional(id=nuevo_id, nombre=nombre, estado="activo")
                self.profesionales.append(prof)
                print(f"¡{nombre} agregado!")
            
            elif op == "2":
                id_prof = input("ID a cambiar: ")
                for p in self.profesionales:
                    if p.id == id_prof:
                        p.estado = "inactivo" if p.estado == "activo" else "activo"
                        print(f"{p.nombre} ahora está {p.estado.upper()}")
                        break
                else:
                    print("ID no encontrado")
            
            elif op == "3":
                break
        self.guardar_todo()

    def solicitar_turno(self):
        print("\n--- SOLICITAR TURNO ---")
        dni = input("DNI del cliente: ")
        cliente = next((c for c in self.clients if c.dni == dni), None)
        if not cliente:
            print("Cliente no encontrado")
            return
        
        servicio = input("Servicio: ").strip()
        fecha = input("Fecha (YYYY-MM-DD): ").strip()
        hora = input("Hora (HH:00): ").strip()

        # Validaciones
        try:
            dt = datetime.strptime(fecha, "%Y-%m-%d")
            if dt.weekday() == 6 or dt.weekday() == 0:  # lunes=0, domingo=6
                print("Solo de martes a sábado")
                return
            if not (10 <= int(hora.split(":")[0]) <= 17):
                print("Horario: 10:00 a 18:00")
                return
        except:
            print("Formato inválido")
            return

        # Buscar profesional disponible
        for prof in self.profesionales:
            if prof.estado != "activo":
                continue
            
            # Ver si ya existe slot
            slot = next((s for s in self.slots 
                        if s.profesional_id == prof.id and s.fecha == fecha and s.hora == hora), None)
            
            if not slot:
                slot = Slot(profesional_id=prof.id, fecha=fecha, hora=hora, disponible="True")
                self.slots.append(slot)
            
            if slot.disponible == "True":
                # Crear turno
                nuevo_id = str(max([int(t.id) for t in self.turns] or [0]) + 1)
                turno = Turno(id=nuevo_id, cliente_dni=dni, profesional_id=prof.id,
                             fecha=fecha, hora=hora, servicio=servicio)
                self.turns.append(turno)
                slot.disponible = "False"
                print(f"¡Turno asignado con {prof.nombre}!")
                self.guardar_todo()
                return
        
        print("No hay turnos disponibles en ese horario")

    def listar_turnos(self):
        print("\n--- LISTADO DE TURNOS ---")
        fecha = input("Fecha (dejar vacío para todos): ").strip()
        turnos_filtrados = self.turns
        if fecha:
            turnos_filtrados = [t for t in self.turns if t.fecha == fecha]
        
        for t in turnos_filtrados:
            cliente = next((c for c in self.clients if c.dni == t.cliente_dni), None)
            prof = next((p for p in self.profesionales if p.id == t.profesional_id), None)
            if cliente and prof:
                print(f"ID {t.id} | {t.fecha} {t.hora} | {cliente.nombre} {cliente.apellido} → {prof.nombre} | {t.servicio}")

    def modificar_cancelar_turno(self):
        id_turno = input("ID del turno: ")
        turno = next((t for t in self.turns if t.id == id_turno), None)
        if not turno:
            print("Turno no encontrado")
            return
        
        print("1. Cancelar turno")
        print("2. Modificar servicio")
        op = input("Opción: ")
        
        if op == "1":
            # Liberar slot
            slot = next((s for s in self.slots 
                        if s.profesional_id == turno.profesional_id 
                        and s.fecha == turno.fecha and s.hora == turno.hora), None)
            if slot:
                slot.disponible = "True"
            self.turns.remove(turno)
            print("Turno cancelado")
        elif op == "2":
            nuevo = input(f"Servicio actual ({turno.servicio}): ").strip()
            if nuevo:
                turno.servicio = nuevo
                print("Servicio actualizado")
        
        self.guardar_todo()

    def menu(self):
        while True:
            print("\n" + "="*40)
            print("   SISTEMA DE TURNOS - PELUQUERÍA")
            print("="*40)
            print("1. Registrar cliente")
            print("2. Solicitar turno")
            print("3. Listar turnos")
            print("4. Modificar/Cancelar turno")
            print("5. Gestionar profesionales")
            print("6. Guardar y salir")
            print("7. Salir sin guardar")
            
            op = input("\nElija opción: ")
            
            if op == "1": self.registrar_cliente()
            elif op == "2": self.solicitar_turno()
            elif op == "3": self.listar_turnos()
            elif op == "4": self.modificar_cancelar_turno()
            elif op == "5": self.gestionar_profesionales()
            elif op == "6":
                self.guardar_todo()
                print("Datos guardados. ¡Chau!")
                break
            elif op == "7":
                print("Saliendo sin guardar...")
                break