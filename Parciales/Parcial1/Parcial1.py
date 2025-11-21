import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import CategoricalDtype

CSV = "ventas-de-productores-de-glp.csv"


# Carga y exploración inicial
df = pd.read_csv(CSV, low_memory=False)

print("\n=== SHAPE ===")
print(df.shape)

print("\n=== INFO ===")
print(df.info())

print("\n=== DESCRIBE ===")
print(df.describe())

print("\n=== DTYPES ===")
print(df.dtypes)

print("\n=== NULOS POR COLUMNA ===")
print(df.isna().sum())

print("\n=== DUPLICADOS ===")
print(df.duplicated().sum())

print("\n=== HEAD ===")
print(df.head())

# Renombrar columna fecha_data a Fecha Data porque es la unica con guion bajo
df = df.rename(columns={"fecha_data": "Fecha Data"})

# Convertir columna Fecha Data a formato datetime
df['Fecha Data'] = pd.to_datetime(df['Fecha Data'])

# convertir columnas numericas a objecto para analizar nulos
df["Volumen Fuera"] = df["Volumen Fuera"].astype("str")
df["Volumen Res 844/2007"] = df["Volumen Res 844/2007"].astype("str")

# tratamiento de nulos
TOKENS_NULOS = {"", " ", "   ", "-", "na", "NA", "NaN", "nan", "N/A", "Desconocido", "desconocido"}
for c in df.columns:
    if df[c].dtype == object:
        df[c] = df[c].replace(list(TOKENS_NULOS), pd.NA)

# convertir las columnas a numéricas
df["Volumen Fuera"] = pd.to_numeric(df["Volumen Fuera"], errors="coerce")
df["Volumen Res 844/2007"] = pd.to_numeric(df["Volumen Res 844/2007"], errors="coerce")

# convertir nulos en columnas categoricas a desconocido
df["Planta Carga"] = df["Planta Carga"].fillna("Desconocido")
df["Comprador"] = df["Comprador"].fillna("Desconocido")

# convertir nulos en columnas numericas a 0
df["Volumen Fuera"] = df["Volumen Fuera"].fillna(0)
df["Volumen Res 844/2007"] = df["Volumen Res 844/2007"].fillna(0)

# nulos tras el tratamiento
print("\n=== NULOS TRAS EL TRATAMIENTO ===")
print(df.isna().sum())

# derivacion de metricas
precio_promedio = df.groupby("Mes")["Precio Fuera Iva"].mean()
precio_ordenado = precio_promedio.sort_values(ascending=False)

print("\n=== PRECIO PROMEDIO POR MES ORDENADO DE MAYOR A MENOR ===")
print(precio_ordenado)


# Conversion de tipos columnas Object a tipado furte:
##Columna vendedor
df["Vendedor"] = df["Vendedor"].astype(str)
## Columna de planta de carga
df["Planta Carga"] = df["Planta Carga"].astype(str)
## Columna de tipo de producto
df["Tipo Producto"] = df["Tipo Producto"].astype(str)
## Cuit de comprador to numeric - tiene cosas como 2046330 y 20-46330
df["Cuit Comprador"] = df["Cuit Comprador"].astype(str)

##Funcion para pasar todos los cuits a XX-XXXXXXX-x
def formatear_cuit(cuit):
    cuit = str(cuit).replace("-","")
    if len(cuit) == 11:
        return f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"
    return cuit  # Devuelve sin cambios si no tiene longitud válida
## Aplicar la funcion a la columna
df['Cuit Comprador'] = df['Cuit Comprador'].astype(str).apply(formatear_cuit)

##continuamos actualizando las columnas tipo object: Comprador
df["Comprador"] = df["Comprador"].astype(str)

#Actividad comprador
df["Actividad Comprador"] = df["Actividad Comprador"].astype(str)

##Fecha data a datetime
df["Fecha Data"] = pd.to_datetime(df["Fecha Data"])

##Mostrar nuevos tipos
print("\n=== DTYPES ===")
print("Tratamiento de tipos de datos object:")
print(df.dtypes)
# corroboramos si hubo cambios respecto a nulos
print("\n=== NULOS POR COLUMNA ===")
print(df.isna().sum())


