import mysql.connector
import pyautogui
import time
from collections import defaultdict
from datetime import date, timedelta
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables del .env

API_URL = os.getenv("API_URL", "http://localhost:3000/api")  # fallback por si no está

def ejecutar_consultas(nombre_db, dias):
    aceptados_por_practica = defaultdict(list)

    try:
        with open('resultadosACEPTACION.txt', 'r') as result_file:
            for line in result_file:
                line = line.strip()
                if not line:
                    continue
                try:
                    benef, cod_practica, estado = line.split(' - ')
                    if estado == 'Aceptada':
                        aceptados_por_practica[cod_practica].append(benef)
                except ValueError:
                    print(f"Línea mal formateada: {line}")
    except FileNotFoundError:
        print("No se encontró el archivo resultadosACEPTACION.txt")
        return

    for cod_practica, beneficios in aceptados_por_practica.items():
        try:
            response = requests.post(
                f"{API_URL}/api/marcar-aceptar",
                json={
                    "beneficios": beneficios,
                    "cod_practica": cod_practica
                },
                headers={"x-database": nombre_db},
                params={"dias": dias}  # 👈 Pasar días como query param
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
