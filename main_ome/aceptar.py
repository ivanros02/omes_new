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





def obtener_bloques_profesionales(nombre_db, nombre_fijo, dias):
    try:
        response = requests.get(
            f"{API_URL}/api/bloques",
            headers={
                "x-database": nombre_db,
                "x-nombre-fijo": nombre_fijo
            },
            params={
                "dias": dias
            }
        )
        response.raise_for_status()
        data = response.json()
        print("Datos obtenidos desde la API:", data)
        return [
            (row["benef"], row["cod_practica"], row["cod_diag"], row["nombre_generador"])
            for row in data
        ]
    except requests.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return []



# Seleccionar credenciales únicas
def obtener_credenciales():
    return ('UP3069149922304', 'ARGENTINA2025', 'clinica')

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
def procesar_paciente(benef, cod_practica, cod_diag, indice):
    horas_y_minutos = [('08', '0'), ('08', '30'), ('09', '0'), ('09', '30'), ('10', '0'), 
                       ('10', '30'), ('11', '0'), ('11', '30'), ('12', '0'), ('12', '30'), 
                       ('13', '0'), ('13', '30'), ('14', '0'), ('14', '30'), ('15', '0'),
                       ('15', '30'), ('16', '0'), ('16', '30'), ('17', '0'), ('17', '30')]
    
    hora, minuto = horas_y_minutos[indice % len(horas_y_minutos)]

    pyautogui.press('tab', presses=13)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('del')
    pyautogui.typewrite(str(benef))  # Utiliza la línea actual del archivo
    pyautogui.press('tab',presses=4)
    pyautogui.press('enter')
    pyautogui.press('p')
    pyautogui.press('p')
    pyautogui.press('enter')
    time.sleep(3)

    pyautogui.press('tab', presses=5)  # hasta el boton buscar
    pyautogui.press('enter')
    time.sleep(4)
    pyautogui.press('pagedown')  # Simula una pulsación de la tecla Page Down
    time.sleep(3)
    
    try:
        boton = pyautogui.locateCenterOnScreen('./img/botonValidar.png', confidence=0.9)  # click en validar
        if boton is not None:  # Verificar si la imagen fue encontrada
            x, y = boton
            pyautogui.click(x, y)
            time.sleep(5)
            pyautogui.press('tab', presses=3)  # llegar a fecha
            pyautogui.press('right')
            pyautogui.press('enter')  # pone la fecha actual por defecto
            time.sleep(2)
            horario = pyautogui.locateCenterOnScreen('./img/horario.png', confidence=0.7)  # click en horario
        if horario is not None:  # Verificar si la imagen fue encontrada
            x, y = horario
            pyautogui.click(x, y)
            time.sleep(1)
            pyautogui.typewrite(hora)  # hora
            time.sleep(1)
            pyautogui.press('enter')
            pyautogui.press('tab')
            time.sleep(1)
            pyautogui.typewrite(minuto)  # minutos
            time.sleep(1)   
            pyautogui.press('tab',presses=2)
            time.sleep(1)
            pyautogui.press('c')  # primera boca
            time.sleep(1)
            pyautogui.press('tab')  # hasta aceptar
            pyautogui.press('enter')  # acepto
            time.sleep(3)
            pyautogui.press('enter')  # para aceptar

            # Guardar en el archivo de resultados
            with open('resultadosACEPTACION.txt', 'a') as result_file:
                result_file.write(f"{benef} - {cod_practica} - Aceptada\n")
            time.sleep(5)
             
        else:
            with open('resultadosACEPTACION.txt', 'a') as result_file:
                result_file.write(f"{benef} - {cod_practica} - No Aceptada\n")
            panel = pyautogui.locateCenterOnScreen('./img/panelAceptacion.png', confidence=0.7)
            if panel is not None:  # Verificar si la imagen fue encontrada
                x, y = panel
                pyautogui.click(x, y)
               
        time.sleep(3)

    except Exception as e:
        print(f"Error inesperado: {e}")



def ejecutar(nombre_db, nombre_fijo, dias):
    usuario, contrasena, _ = obtener_credenciales()
    iniciar_sesion(usuario, contrasena)

    # Procesar pacientes sin división por bloques
    for i, (benef, cod_practica, cod_diag, _) in enumerate(obtener_bloques_profesionales(nombre_db, nombre_fijo, dias)):
        procesar_paciente(benef, cod_practica, cod_diag, i)

    pyautogui.hotkey('ctrl', 'w')
    time.sleep(3)

    # Ejecutar consulta con días
    ejecutar_consultas(nombre_db, dias)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        nombre_db = sys.argv[1]
        nombre_fijo = sys.argv[2]
        dias = sys.argv[3]
    else:
        print("❌ Faltan argumentos.")
        sys.exit(1)

    ejecutar(nombre_db, nombre_fijo, dias)




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
