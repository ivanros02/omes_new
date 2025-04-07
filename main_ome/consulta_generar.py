import mysql.connector
import pyautogui
import time
from datetime import date, timedelta
from collections import defaultdict
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables del .env

API_URL = os.getenv("API_URL", "http://localhost:3000/api")  # fallback por si no está

def ejecutar_consultas(nombre_db, dias):
    beneficios_por_practica = defaultdict(list)

    try:
        with open('reporte_ordenes.txt', 'r') as result_file:
            for line in result_file:
                line = line.strip()
                if not line:
                    continue
                try:
                    benef, estado, cod_practica = line.split(' - ')
                    if estado == 'Generada':
                        beneficios_por_practica[cod_practica].append(benef)
                except ValueError:
                    print(f"Línea mal formateada: {line}")
    except FileNotFoundError:
        print("No se encontró el archivo reporte_ordenes.txt")
        return

    if not beneficios_por_practica:
        print("No hay beneficios para actualizar.")
        return

    for cod_practica, beneficios in beneficios_por_practica.items():
        try:
            response = requests.post(
                f"{API_URL}/api/marcar-generado",
                json={
                    "beneficios": beneficios,
                    "cod_practica": cod_practica
                },
                headers={"x-database": nombre_db},
                params={"dias": dias}  # 👈 PASÁS el valor de días como query param
            )
            response.raise_for_status()
            print(f"✅ Actualización para práctica {cod_practica} completada:", response.json())
        except requests.RequestException as e:
            print(f"❌ Error al actualizar beneficios para práctica {cod_practica}: {e}")



if __name__ == "__main__":
    if len(sys.argv) > 1:
        nombre_db = sys.argv[1]
        dias = sys.argv[3]
    else:
        print("⚠️ No se especificó la base de datos. Usando valor por defecto.")

    ejecutar_consultas(nombre_db,dias)
            