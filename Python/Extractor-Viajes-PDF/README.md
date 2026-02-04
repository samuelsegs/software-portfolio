# Extractor-Viajes-PDF

Herramienta desarrollada en Python para la **extracción, limpieza y transformación de información logística** 
contenida en archivos PDF, generando como salida un archivo estructurado en formato ODS compatible con LibreOffice.

---

## Descripción

Este proyecto automatiza la lectura de reportes de viajes en formato PDF, los cuales contienen información tabular 
generada por sistemas operativos logísticos.  
El sistema identifica las tablas relevantes, filtra datos innecesarios y construye un archivo ODS listo para su 
análisis o uso operativo.

Está orientado a **usuarios no técnicos**, ofreciendo una interfaz gráfica simple para seleccionar el archivo y 
ejecutar el proceso.

---

## Flujo general del sistema

1. Selección de archivo PDF desde una interfaz gráfica.
2. Lectura del documento página por página.
3. Extracción de tablas mediante parsing estructurado.
4. Limpieza de datos:
   - Eliminación de filas vacías.
   - Omisión de encabezados duplicados.
   - Normalización de columnas relevantes.
5. Conversión de los datos a un DataFrame.
6. Exportación del resultado a un archivo ODS.

---

## Tecnologías utilizadas

- **pdfplumber** – extracción de tablas desde PDF
- **pandas** – procesamiento y limpieza de datos
- **tkinter** – interfaz gráfica de usuario
- **odfpy** – generación de archivos ODS
- **LibreOffice** (destino del archivo generado)

---

## Estructura del proyecto
```
Extractor-Viajes-PDF/
├── ExtraerViajes.py
├── assets/
│ └── logo.png
└── README.md
```
---

## Caso de uso

Este tipo de herramienta resulta útil cuando:

- Los reportes se generan únicamente en PDF.
- Se requiere reutilizar la información en hojas de cálculo.
- No existe acceso directo a una base de datos.
- El usuario final necesita una solución rápida y sencilla.

---

## Limitaciones conocidas

- El sistema depende de la **estructura del PDF**; cambios significativos en el formato pueden requerir ajustes en el código.
- No utiliza base de datos; el procesamiento es por archivo.
- No contempla validación avanzada de errores en documentos corruptos o incompletos.

---

## Posibles mejoras futuras

- Soporte para múltiples formatos de PDF.
- Validación automática de estructura del documento.
- Migración a una arquitectura basada en base de datos.
- Exportación a otros formatos (CSV, Excel).

---

## Nota importante

Este proyecto se basa en un escenario operativo real, **adaptado para fines demostrativos y de portafolio técnico**.  
Los datos utilizados en esta versión no representan información sensible ni confidencial.


## Autor

**Samuel Segura**  
