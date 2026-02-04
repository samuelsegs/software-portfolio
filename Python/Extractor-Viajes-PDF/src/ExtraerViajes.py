import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pandas as pd
import pdfplumber
import os
import sys
from tkinter import Tk

# extraer los datos del PDF
def extract_data_from_pdf(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if any(row):  # Filtrar filas vacías
                        data.append(row)
    return data

# Procesar los datos extraídos
def parse_travel_data(data):
    columns = ["VIAJE", "ORIGEN", "DESTINO", "CLIENTE", "T.V.", "UTILIDAD VIAJE", "UNIDAD", "T. UNIDAD", "UTILIDAD UNIDAD"]
    filtered_data = [row[:9] for row in data if len(row) >= 9]

    # Eliminar filas que coincidan con las cabeceras duplicadas
    filtered_data = [row for row in filtered_data if row != columns]

    df = pd.DataFrame(filtered_data, columns=columns)
    return df.dropna().reset_index(drop=True)

# Guardar los datos procesados en un archivo .ods
def save_to_ods(df, output_path):
    df.to_excel(output_path, engine='odf', index=False)

# Función para seleccionar el archivo PDF
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    if file_path:
        # Extraer y procesar los datos del PDF
        document_data = extract_data_from_pdf(file_path)
        df = parse_travel_data(document_data)

        # Guardar el archivo .ods
        output_path = filedialog.asksaveasfilename(defaultextension=".ods", filetypes=[("Archivos ODS", "*.ods")])
        if output_path:
            save_to_ods(df, output_path)
            status_label.config(text=f"Datos extraídos y guardados en: {output_path}")
        else:
            status_label.config(text="⚠️ Error: No se guardó el archivo.⚠️")
    else:
        status_label.config(text="Error: No se seleccionó ningún archivo. 🫠")

# Crear la ventana principal
root = tk.Tk()
root.title("Extraer Datos de Viajes")

# tamaño de la ventana
root.geometry("600x400")

# Configurar los colores de fondo y el tema de la ventana
root.configure(bg="#09122c")

# Crear un marco
frame = tk.Frame(root, bg="#872341")
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Cargar la imagen del logo
logo_img = Image.open("logo.png")  
logo_img = logo_img.resize((280, 45))  # Redimensionamos a 280x45
logo_resized = ImageTk.PhotoImage(logo_img)

# Crear un Label para mostrar la imagen de título
logo_label = tk.Label(frame, image=logo_resized, bg="#872341")
logo_label.pack(pady=10)  # Colocamos la imagen con un margen superior

# Agregar un título y otros widgets a la interfaz
title_label = tk.Label(frame, text="Extraer Datos de Viajes ", font=("CUbuntu", 16), fg="white", bg="#BE3144")
title_label.pack(pady=10)

# Agregar un botón para abrir archivos
open_button = tk.Button(frame, text="Seleccionar archivo", command=open_file, bg="#BE3144", fg="white", font=("Helvetica", 12))
open_button.pack(pady=20)

# Etiqueta de estado para mostrar los mensajes
status_label = tk.Label(frame, text="Seleccione un archivo PDF para empezar.", font=("Helvetica", 12), fg="white", bg="#E17564")
status_label.pack(pady=20)

# Función para cerrar la ventana al hacer clic en "Aceptar"
def close_window():
    root.quit() 

# Botón de "Aceptar" que cerrará la aplicación
accept_button = tk.Button(frame, text="Aceptar", command=close_window, bg="#BE3144", fg="white", font=("Helvetica", 12))
accept_button.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()
