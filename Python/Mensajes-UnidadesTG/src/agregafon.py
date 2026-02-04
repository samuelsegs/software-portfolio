import pandas as pd

# --- Cargar archivo de viajes desde celda G7 (fila 1) ---
df_viajes = pd.read_excel("Viajes.ods", engine="odf", header=0)

# --- Cargar archivo de números desde .ods ---
df_numeros = pd.read_excel("numeros.ods", engine="odf")

# --- Normalizar nombres de columnas ---
df_viajes.columns = df_viajes.columns.str.strip().str.upper()
df_numeros.columns = df_numeros.columns.str.strip().str.upper()

# --- Validar columnas necesarias ---
assert "UNIDAD" in df_viajes.columns, "Columna 'UNIDAD' no encontrada en Viajes.ods"
assert "UNIDAD" in df_numeros.columns, "Columna 'UNIDAD' no encontrada en numeros.ods"
assert "NUMERO" in df_numeros.columns, "Columna 'NUMERO' no encontrada en numeros.ods"

# --- Convertir UNIDAD a entero ---
df_viajes["UNIDAD"] = pd.to_numeric(df_viajes["UNIDAD"], errors="coerce").fillna(0).astype(int)
df_numeros["UNIDAD"] = pd.to_numeric(df_numeros["UNIDAD"], errors="coerce").fillna(0).astype(int)

# --- Limpiar el número ---
df_numeros["NUMERO"] = df_numeros["NUMERO"].astype(str).str.strip()

# --- Hacer merge por UNIDAD ---
df_resultado = pd.merge(df_viajes, df_numeros[["UNIDAD", "NUMERO"]], on="UNIDAD", how="left")

# --- Insertar número en columna M (índice 12) ---
if df_resultado.shape[1] < 13:
    while df_resultado.shape[1] < 12:
        df_resultado[f"Extra_{df_resultado.shape[1]}"] = ""
    df_resultado.insert(12, "TELEFONO", df_resultado.pop("NUMERO"))
else:
    df_resultado.insert(12, "TELEFONO", df_resultado.pop("NUMERO"))

# --- Exportar resultado como ODS ---
df_resultado.to_excel("viajes_con_telefonos.ods", index=False, engine="odf")

print("✅ Archivo generado como 'viajes_con_telefonos.ods' correctamente.")
