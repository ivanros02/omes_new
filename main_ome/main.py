import tkinter as tk
import subprocess

# Mapeo entre el texto visible y la base real
base_map = {
    "COMTAN": "pq0303_token",
    "DANKVEL": "worldsof_medical_pq0328",
    "PEÑI": "worldsof_medical_pq2001"
}

profesional_opciones = [
    "FORBITO AGUSTIN",
    "Ramirez Blankenhorst Oscar"
]

dias_opciones = {
    "Hoy": "0",
    "Mañana": "1",
    "+2 días": "2",
    "+3 días": "3"
}


# Ejecutar scripts pasando la base como argumento
def ejecutar_script(nombre_script, db_selected, prof_selected, dias):
    if db_selected not in base_map:
        print("Seleccioná una base válida.")
        return
    nombre_db = base_map[db_selected]
    try:
        subprocess.run(["python", nombre_script, nombre_db, prof_selected, dias], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {nombre_script}: {e}")


# Crear ventana principal
ventana = tk.Tk()
ventana.title("WorldSoft - Acciones OME")
ventana.geometry("400x500")

# Opción seleccionada (por defecto COMTAN)
selected_db = tk.StringVar(ventana)
selected_db.set("COMTAN")

# Profesional seleccionado (por defecto el primero)
selected_prof = tk.StringVar(ventana)
selected_prof.set(profesional_opciones[0])

# Día seleccionado (por defecto "Hoy")
selected_dias = tk.StringVar(ventana)
selected_dias.set("Hoy")

# Menú de selección de clínica
label_select = tk.Label(ventana, text="Seleccione Clínica:")
label_select.pack(pady=5)
dropdown = tk.OptionMenu(ventana, selected_db, *base_map.keys())
dropdown.pack(pady=5)

# Menú de selección de profesional fijo
label_prof = tk.Label(ventana, text="Seleccione Profesional para 520101:")
label_prof.pack(pady=5)
dropdown_prof = tk.OptionMenu(ventana, selected_prof, *profesional_opciones)
dropdown_prof.pack(pady=5)

# Menú de selección de días
label_dias = tk.Label(ventana, text="Seleccione Día:")
label_dias.pack(pady=5)
dropdown_dias = tk.OptionMenu(ventana, selected_dias, *dias_opciones.keys())
dropdown_dias.pack(pady=5)

# Botones con todos los valores seleccionados
btn_generar = tk.Button(ventana, text="Generar OME", width=25,
    command=lambda: ejecutar_script("generar.py", selected_db.get(), selected_prof.get(), dias_opciones[selected_dias.get()]))

btn_aceptar = tk.Button(ventana, text="Aceptar OME", width=25,
    command=lambda: ejecutar_script("aceptar.py", selected_db.get(), selected_prof.get(), dias_opciones[selected_dias.get()]))

btn_consulta_generar = tk.Button(ventana, text="Consulta Generar OME", width=25,
    command=lambda: ejecutar_script("consulta_generar.py", selected_db.get(), selected_prof.get(), dias_opciones[selected_dias.get()]))

btn_consulta_aceptar = tk.Button(ventana, text="Consulta Aceptar OME", width=25,
    command=lambda: ejecutar_script("consulta_aceptar.py", selected_db.get(), selected_prof.get(), dias_opciones[selected_dias.get()]))

# Ubicar botones
btn_generar.pack(pady=10)
btn_aceptar.pack(pady=10)
btn_consulta_generar.pack(pady=10)
btn_consulta_aceptar.pack(pady=10)

# Ejecutar la app
ventana.mainloop()

