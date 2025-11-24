# utils.py - Funciones auxiliares

def crea_csv(nombre_archivo, columnas):
    with open(nombre_archivo, "w", encoding="utf-8") as file:
        file.write(",".join(columnas) + "\n")