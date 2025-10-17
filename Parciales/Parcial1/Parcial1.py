import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import CategoricalDtype

CSV = "ventas-de-productores-de-glp.csv"


# Carga y exploración inicial
df = pd.read_csv(CSV)

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



