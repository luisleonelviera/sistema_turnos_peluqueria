# peluqueria.py - Lógica principal del sistema

# Versión mejorada con guías al solicitar turno

from datetime import datetime
from models import Cliente, Profesional, Slot, Turno
from db import db
from utils import crea_csv

# ==================== CONFIGURACIÓN DE LA PELUQUERÍA ====================
SERVICIOS_DISPONIBLES = {
    "corte": "Corte de cabello",
    "corte y barba": "Corte + barba",
    "alisado": "Alisado",
    "tintura": "Cambio de color / Tintura",
    "brushing": "Brushing / Peinado",
    "manicuria": "Manicuria",
    "otros": "Otros servicios"
}

DIAS_TRABAJO = "Martes a Sábado"
HORARIO_APERTURA = "10:00"
HORARIO_CIERRE = "18:00"
HORARIOS_POSIBLES = [f"{h:02d}:00" for h in range(10, 18)]  # 10:00 a 17:00

# ======================================================================

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

        # Crear 4 profesionales por defecto
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
                if not nombre: continue
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
        print("\n" + "="*50)
        print("        SOLICITAR TURNO")
        print("="*50)

        # Mostrar información útil
        print("SERVICIOS DISPONIBLES:")
        for codigo, nombre in SERVICIOS_DISPONIBLES.items():
            print(f"   • {nombre}  →  escriba: {codigo}")
        print()

        print(f"DÍAS QUE ATENDEMOS: {DIAS_TRABAJO}")
        print(f"HORARIO: {HORARIO_APERTURA} a {HORARIO_CIERRE}")
        print("Horarios disponibles:", ", ".join(HORARIOS_POSIBLES))
        print("-" * 50)

        # Pedir datos
        dni = input("DNI del cliente: ").strip()
        cliente = next((c for c in self.clients if c.dni == dni), None)
        if not cliente:
            print("Cliente no encontrado. Regístrelo primero.")
            return

        print(f"\nCliente encontrado: {cliente.nombre} {cliente.apellido}")

        while True:
            servicio_input = input(f"\nServicio (ej: corte, alisado, etc): ").strip().lower()
            if servicio_input in SERVICIOS_DISPONIBLES:
                servicio = SERVICIOS_DISPONIBLES[servicio_input]
                break
            else:
                print("Servicio no válido. Elija uno de la lista.")

        fecha = input("Fecha (YYYY-MM-DD): ").strip()
        try:
            dt = datetime.strptime(fecha, "%Y-%m-%d")
            if dt.weekday() == 0 or dt.weekday() == 6:  # lunes o domingo
                print("¡La peluquería está cerrada lunes y domingos!")
                return
            if dt.weekday() == 5 and dt.hour >= 13:  # sábado después de las 13?
                pass  # por ahora no limitamos sábado
        except:
            print("Fecha inválida")
            return

        hora = input("Hora (HH:00): ").strip()
        if hora not in HORARIOS_POSIBLES:
            print(f"Hora inválida. Use: {', '.join(HORARIOS_POSIBLES)}")
            return

        # Mostrar disponibilidad por profesional
        print(f"\nBuscando disponibilidad para {fecha} a las {hora}...")
        profesionales_activos = [p for p in self.profesionales if p.estado == "activo"]
        
        for prof in profesionales_activos:
            # Ver si hay turno ya tomado
            ocupado = any(
                t.profesional_id == prof.id and t.fecha == fecha and t.hora == hora
                for t in self.turns
            )
            estado = "OCUPADO" if ocupado else "DISPONIBLE"
            print(f"   • {prof.nombre} → {estado}")
        
        # Asignar al primero disponible
        for prof in profesionales_activos:
            ya_tiene_turno = any(
                t.profesional_id == prof.id and t.fecha == fecha and t.hora == hora
                for t in self.turns
            )
            if not ya_tiene_turno:
                # Crear slot si no existe
                slot = next((s for s in self.slots 
                            if s.profesional_id == prof.id and s.fecha == fecha and s.hora == hora), None)
                if not slot:
                    slot = Slot(profesional_id=prof.id, fecha=fecha, hora=hora, disponible="True")
                    self.slots.append(slot)

                # Crear turno
                nuevo_id = str(max([int(t.id) for t in self.turns] or [0]) + 1)
                turno = Turno(id=nuevo_id, cliente_dni=dni, profesional_id=prof.id,
                             fecha=fecha, hora=hora, servicio=servicio)
                self.turns.append(turno)

                print(f"\n¡TURNO CONFIRMADO!")
                print(f"Cliente: {cliente.nombre} {cliente.apellido}")
                print(f"Profesional: {prof.nombre}")
                print(f"Fecha: {fecha} - {hora}")
                print(f"Servicio: {servicio}")
                print(f"ID del turno: {nuevo_id}")
                
                self.guardar_todo()
                return

        print("Lo siento, no hay disponibilidad en ese horario.")

    def listar_turnos(self):
        print("\n--- LISTADO DE TURNOS ---")
        fecha = input("Fecha para filtrar (dejar vacío para todos): ").strip()
        turnos = self.turns
        if fecha:
            turnos = [t for t in turnos if t.fecha == fecha]
        
        if not turnos:
            print("No hay turnos registrados.")
            return
        
        for t in turnos:
            c = next((cl for cl in self.clients if cl.dni == t.cliente_dni), None)
            p = next((pr for pr in self.profesionales if pr.id == t.profesional_id), None)
            if c and p:
                print(f"[{t.id}] {t.fecha} {t.hora} → {c.nombre} {c.apellido} con {p.nombre} | {t.servicio}")

    def modificar_cancelar_turno(self):
        id_turno = input("ID del turno a modificar/cancelar: ").strip()
        turno = next((t for t in self.turns if t.id == id_turno), None)
        if not turno:
            print("Turno no encontrado")
            return
        
        c = next((cl for cl in self.clients if cl.dni == turno.cliente_dni), None)
        p = next((pr for pr in self.profesionales if pr.id == turno.profesional_id), None)
        
        print(f"\nTurno encontrado:")
        print(f"Cliente: {c.nombre} {c.apellido} | {turno.fecha} {turno.hora} | {p.nombre} | {turno.servicio}")
        
        print("\n1. Cancelar turno")
        print("2. Cambiar servicio")
        op = input("Opción: ")
        
        if op == "1":
            # Liberar slot
            self.turns.remove(turno)
            print("Turno cancelado")
        elif op == "2":
            nuevo = input("Nuevo servicio: ").strip()
            if nuevo:
                turno.servicio = nuevo
                print("Servicio actualizado")
        
        self.guardar_todo()

    def menu(self):
        while True:
            print("\n" + "="*50)
            print("    SISTEMA DE TURNOS - PELUQUERÍA")
            print("="*50)
            print("1. Registrar cliente")
            print("2. Solicitar turno")
            print("3. Listar turnos")
            print("4. Modificar/Cancelar turno")
            print("5. Gestionar profesionales")
            print("6. Guardar y salir")
            print("7. Salir sin guardar")
            
            op = input("\n→ Elija una opción: ")
            
            if op == "1": self.registrar_cliente()
            elif op == "2": self.solicitar_turno()
            elif op == "3": self.listar_turnos()
            elif op == "4": self.modificar_cancelar_turno()
            elif op == "5": self.gestionar_profesionales()
            elif op == "6":
                self.guardar_todo()
                print("¡Datos guardados! Hasta luego")
                break
            elif op == "7":
                print("Saliendo sin guardar...")
                break