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

# Conexion api
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

# Fin Conexion api

# Iniciar sesión en el sistema
def iniciar_sesion(usuario, contrasena): 
    time.sleep(2)
    pyautogui.press('win')
    time.sleep(2)
    
    # Buscar Google Chrome y abrirlo
    pyautogui.write('edge')  # Escribe 'chrome' en el menú de inicio
    time.sleep(2)
    pyautogui.press('enter')  # Presiona Enter para abrir Google Chrome
    time.sleep(2)
    
    # Enviar el comando para abrir en modo incógnito
    pyautogui.hotkey('ctrl', 'shift', 'n')  # Abre una ventana en incógnito (Ctrl + Shift + N)
    time.sleep(2)
    
    # Escribir la URL de la página
    pyautogui.write('https://cup.pami.org.ar/controllers/loginController.php')
    pyautogui.press('enter')  # Presiona Enter para acceder a la página
    time.sleep(2)

    # Esperar unos segundos para que la página cargue completamente
    time.sleep(7)
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
    time.sleep(5)
    pyautogui.press('tab', presses=2)  # 3 veces para buscar el botón ome
    pyautogui.press('enter')  # en boton ome
    time.sleep(3)
    pass

# Procesar paciente
def procesar_paciente(benef, cod_practica, cod_diag):
    generadas = 0  # Variable para contar cuántas órdenes se generaron
    time.sleep(1)
    x, y = pyautogui.locateCenterOnScreen('./img/botonOme.png',confidence=0.9) #click en validar
    pyautogui.click(x, y)
    time.sleep(5)
    pyautogui.press('tab',presses=10)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('del')
    time.sleep(3)
    print(benef)
    print(benef)
    pyautogui.typewrite(str(benef))  # Utiliza la línea actual del archivo
    time.sleep(3)

    pyautogui.press('tab')  # para buscar beneficio anterior
    time.sleep(4)

    pyautogui.press('tab', presses=6)  # hasta diag
    
    # Eliminar el punto si lo hay en cod_diag
    cod_diag = cod_diag.replace('.', '').replace('-', '')  # Elimina el punto si existe
    
    pyautogui.typewrite(cod_diag)  # Escribir el código diagnóstico
    time.sleep(3)
    pyautogui.press('enter')

    pyautogui.press('tab', presses=6)  # hasta práctica
    pyautogui.typewrite(str(cod_practica))
    time.sleep(3)
    pyautogui.press('enter')
    time.sleep(1)

    pyautogui.press('tab', presses=14)  # hasta finalizar
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(4)

    pyautogui.press('tab', presses=3)  # hasta confirmar ome
    pyautogui.press('enter')
    time.sleep(5)
        
    # Validar si la orden fue generada correctamente
    # Intentar localizar la imagen
    generada = pyautogui.locateCenterOnScreen('./img/ordenGenerada.png', confidence=0.7)

    if generada is not None:
        generadas += 1  # Incrementar la cuenta de órdenes generadas
        with open('reporte_ordenes.txt', 'a') as reporte:
            reporte.write(f"{benef} - Generada\n")  # Guardar en el reporte
        pyautogui.press('tab')
        pyautogui.press('enter')
        pyautogui.press('up', presses=4)
        time.sleep(3)
    else:
        # Si no se encuentra la imagen, se guarda como 'No generada'
        with open('reporte_ordenes.txt', 'a') as reporte:
            reporte.write(f"{benef} - No generada - {cod_practica}\n")  # Guardar en el reporte
        pyautogui.press('tab')
        pyautogui.press('enter')
        pyautogui.press('up', presses=4)
        time.sleep(7)

        # Intentar localizar y hacer clic en 'eliminarPractica'
        eliminar_practica = pyautogui.locateCenterOnScreen('./img/eliminarPractica.png', confidence=0.9)
        if eliminar_practica is not None:
            x, y = eliminar_practica
            pyautogui.click(x, y)
            time.sleep(5)

            # Intentar localizar y hacer clic en 'eliminarDiag'
            eliminar_diag = pyautogui.locateCenterOnScreen('./img/eliminarDiag.png', confidence=0.9)
            if eliminar_diag is not None:
                x, y = eliminar_diag
                pyautogui.click(x, y)
                time.sleep(5)
            else:
                print("No se encontró la imagen 'eliminarDiag.png'.")
        else:
            print("No se encontró la imagen 'eliminarPractica.png'.")

        pass


# Main: Proceso de OME
def ejecutar(nombre_db, nombre_fijo, dias):
    bloque_actual = None

    for benef, cod_practica, cod_diag, prof_generador, usuario, contrasena in obtener_bloques_profesionales(nombre_db, nombre_fijo, dias):
        if bloque_actual != prof_generador:
            if bloque_actual is not None:
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(3)

            print(f"Iniciando sesión con {prof_generador} ({usuario})")
            iniciar_sesion(usuario, contrasena)
            bloque_actual = prof_generador

        procesar_paciente(benef, cod_practica, cod_diag)

    pyautogui.hotkey('ctrl', 'w')
    time.sleep(3)

    ejecutar_consultas(nombre_db, dias)

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        nombre_db = sys.argv[1]
        nombre_fijo = sys.argv[2]
        dias = sys.argv[3]
    else:
        print("❌ Faltan argumentos. Uso esperado:")
        print("python generar_bloques.py <nombre_db> <nombre_fijo> <dias>")
        sys.exit(1)

    ejecutar(nombre_db, nombre_fijo, dias)


'''
# Main: Proceso de OME para pruebas de partición
def ejecutar(nombre_db, nombre_fijo, dias):
    bloque_actual = None
    for benef, cod_practica, cod_diag, nombre_generador in obtener_bloques_profesionales(nombre_db, nombre_fijo, dias):
        if bloque_actual != nombre_generador:
            if bloque_actual is not None:
                print(f"Cerrando sesión para el bloque anterior: {bloque_actual}")
            print(f"Iniciando sesión para el nuevo bloque: {nombre_generador}")
            bloque_actual = nombre_generador

        print(f"Procesando paciente: Beneficio {benef}, Práctica {cod_practica}, Diagnóstico {cod_diag}")

    print(f"Cerrando sesión para el último bloque: {bloque_actual}")



# ----- Punto de entrada -----
if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        nombre_db = sys.argv[1]
        nombre_fijo = sys.argv[2]
        dias = sys.argv[3]
    else:
        print("❌ Faltan argumentos. Uso esperado:")
        sys.exit(1)

    ejecutar(nombre_db, nombre_fijo, dias)
'''