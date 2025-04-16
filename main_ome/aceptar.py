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

#Conexion api
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





def obtener_bloques_profesionales(nombre_db, dias):
    try:
        response = requests.get(
            f"{API_URL}/api/bloques-aceptar",
            headers={
                "x-database": nombre_db
            },
            params={
                "dias": dias
            }
        )
        response.raise_for_status()
        data = response.json()
        print("Datos obtenidos desde la API:", data)
        return [
            (
                row["benef"],
                row["cod_practica"]
            )
            for row in data
        ]
    except requests.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return []




# Seleccionar credenciales únicas
def obtener_credenciales(nombre_db):
    credenciales_por_db = {
        "worldsof_medical_pq0303": ("UP3069149922304", "ARGENTINA2026", "clinica"),
        "worldsof_medical_pq0328": ("UP3070779334800", "Dankvel.2025", "clinica"),
    }

    return credenciales_por_db.get(nombre_db, ("usuario_default", "password_default", "clinica"))

def obtener_tecla_boca(nombre_db):
    teclas_por_db = {
        "worldsof_medical_pq0303": "c",  # COMTAN
        "worldsof_medical_pq0328": "d",  # DANKVEL
        "worldsof_medical_pq0402": "c",  # Ejemplo extra
        # Agregá más aquí...
    }

    # Valor por defecto si no se encuentra
    return teclas_por_db.get(nombre_db, "c")


#Fin Conexion api

# Iniciar sesión en el sistema
def iniciar_sesion(usuario, contrasena): 
    time.sleep(2)
    pyautogui.press('win')
    time.sleep(2)
    
    # Buscar Google Chrome y abrirlo
    pyautogui.write('edge')  # Escribe 'chrome' en el menú de inicio
    pyautogui.press('enter')  # Presiona Enter para abrir Google Chrome
    time.sleep(3)
    
    # Enviar el comando para abrir en modo incógnito
    pyautogui.hotkey('ctrl', 'shift', 'n')  # Abre una ventana en incógnito (Ctrl + Shift + N)
    time.sleep(3)
    
    # Escribir la URL de la página
    pyautogui.write('https://cup.pami.org.ar/controllers/loginController.php')
    pyautogui.press('enter')  # Presiona Enter para acceder a la página
    time.sleep(7)

    # Esperar unos segundos para que la página cargue completamente
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('del')
    # Usar PyAutoGUI para enviar las teclas necesarias para ingresar al sitio web
    pyautogui.typewrite(usuario)
    pyautogui.press('tab')  # Cambiar el foco al campo de contraseña
    time.sleep(2)
    pyautogui.typewrite(contrasena)
    time.sleep(2)
    pyautogui.press('enter')  # Presionar Enter para enviar el formulario

    # Esperar unos segundos para asegurarse de que la página haya cargado completamente
    time.sleep(7)
    pyautogui.press('tab', presses=4)  # 3 veces para buscar el botón ome
    pyautogui.press('enter')  # en boton ome
    time.sleep(5)
    pass

# Procesar paciente con horarios rotativos
def procesar_paciente(benef, cod_practica, tecla_boca, indice):
    horas_y_minutos = [('08', '0'), ('08', '30'), ('09', '0'), ('09', '30'), ('10', '0'), 
                       ('10', '30'), ('11', '0'), ('11', '30'), ('12', '0'), ('12', '30'), 
                       ('13', '0'), ('13', '30'), ('14', '0'), ('14', '30'), ('15', '0'),
                       ('15', '30'), ('16', '0'), ('16', '30'), ('17', '0'), ('17', '30')]

    hora, minuto = horas_y_minutos[indice % len(horas_y_minutos)]

    pyautogui.press('tab', presses=13)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('del')
    pyautogui.typewrite(str(benef))
    pyautogui.press('tab', presses=4)
    pyautogui.press('enter')
    pyautogui.press('p')
    pyautogui.press('p')
    pyautogui.press('enter')
    time.sleep(3)

    pyautogui.press('tab', presses=5)
    pyautogui.press('enter')
    time.sleep(4)
    pyautogui.press('pagedown')
    time.sleep(3)

    try:
        boton = pyautogui.locateCenterOnScreen('./img/botonValidar.png', confidence=0.9)

        if boton is not None:
            x, y = boton
            pyautogui.click(x, y)
            time.sleep(5)
            pyautogui.press('tab', presses=3)
            pyautogui.press('enter')
            time.sleep(2)

            horario = pyautogui.locateCenterOnScreen('./img/horario.png', confidence=0.7)

            if horario is not None:
                x, y = horario
                pyautogui.click(x, y)
                time.sleep(1)
                pyautogui.typewrite(hora)
                time.sleep(1)
                pyautogui.press('enter')
                pyautogui.press('tab')
                time.sleep(1)
                pyautogui.typewrite(minuto)
                time.sleep(1)
                pyautogui.press('tab', presses=2)
                time.sleep(1)
                pyautogui.press(tecla_boca)
                time.sleep(1)
                pyautogui.press('tab')
                pyautogui.press('enter')
                time.sleep(3)
                pyautogui.press('enter')

                with open('resultadosACEPTACION.txt', 'a') as result_file:
                    result_file.write(f"{benef} - {cod_practica} - Aceptada\n")
            else:
                # Si no se encontró horario
                with open('resultadosACEPTACION.txt', 'a') as result_file:
                    result_file.write(f"{benef} - {cod_practica} - No Aceptada\n")
        else:
            # Si no se encontró el botón validar
            with open('resultadosACEPTACION.txt', 'a') as result_file:
                result_file.write(f"{benef} - {cod_practica} - No Aceptada\n")

            panel = pyautogui.locateCenterOnScreen('./img/panelAceptacion.png', confidence=0.7)
            if panel is not None:
                x, y = panel
                pyautogui.click(x, y)

        time.sleep(3)

    except Exception as e:
        print(f"Error inesperado: {e}")
        with open('resultadosACEPTACION.txt', 'a') as result_file:
            result_file.write(f"{benef} - {cod_practica} - ERROR: {str(e)}\n")




def ejecutar(nombre_db, dias):
    usuario, contrasena, _ = obtener_credenciales(nombre_db)
    tecla_boca = obtener_tecla_boca(nombre_db)
    iniciar_sesion(usuario, contrasena)

    # Procesar pacientes sin división por bloques
    for i, (benef, cod_practica) in enumerate(obtener_bloques_profesionales(nombre_db, dias)):
        procesar_paciente(benef, cod_practica,tecla_boca, i)

    pyautogui.hotkey('ctrl', 'w')
    time.sleep(3)

    # Ejecutar consulta con días
    ejecutar_consultas(nombre_db, dias)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        nombre_db = sys.argv[1]
        dias = sys.argv[2]
    else:
        print("❌ Faltan argumentos. Uso esperado:")
        print("python generar_bloques.py <nombre_db> <dias>")
        sys.exit(1)

    ejecutar(nombre_db, dias)




'''
# Main: Proceso de OME para pruebas sin división por bloques
def ejecutar_prueba(nombre_db, nombre_fijo, dias):
    usuario, contrasena, _ = obtener_credenciales()
    print(f"Iniciando sesión con usuario: {usuario}")

    # Simulación del procesamiento de pacientes sin división en bloques
    for i, (benef, cod_practica, cod_diag, _) in enumerate(obtener_bloques_profesionales(nombre_db, nombre_fijo, dias)):
        print(f"Procesando paciente {i + 1}: Beneficio {benef}, Práctica {cod_practica}, Diagnóstico {cod_diag}")
        
        horas_y_minutos = [
            ('08', '0'), ('08', '30'), ('09', '0'), ('09', '30'), ('10', '0'), 
            ('10', '30'), ('11', '0'), ('11', '30'), ('12', '0'), ('12', '30'), 
            ('13', '0'), ('13', '30'), ('14', '0'), ('14', '30'), ('15', '0'),
            ('15', '30'), ('16', '0'), ('16', '30'), ('17', '0'), ('17', '30')
        ]
        hora, minuto = horas_y_minutos[i % len(horas_y_minutos)]
        print(f"Asignando hora {hora}:{minuto} para el paciente {benef}")

    print("Cerrando sesión.")



# Ejecutar si se llama desde main.py
if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        nombre_db = sys.argv[1]
        nombre_fijo = sys.argv[2]
        dias = sys.argv[3]
    else:
        print("❌ Faltan argumentos. Uso esperado:")
        print("python generar_sin_bloques.py <nombre_db> <nombre_fijo> <dias>")
        sys.exit(1)

    ejecutar_prueba(nombre_db, nombre_fijo, dias)

'''
