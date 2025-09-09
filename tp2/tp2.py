# tp2_limpieza_validacion.py
# UTN - Introducción al Análisis de Datos
# Limpieza y validación de datos con Pandas

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Configuración
# -----------------------------
RUTA_CSV = "DatasetClase3_corrupto.csv"
TOKENS_NULOS = ["N/A", "NA", "na", "-", "Desconocido", "None", ""]

# Columnas según encabezado real
COL_ID = "PatientId"
COL_APPTID = "AppointmentID"
COL_GENDER = "Gender"
COL_SCHEDULED = "ScheduledDay"
COL_APPT = "AppointmentDay"
COL_AGE = "Age"
COL_NEIGH = "Neighbourhood"
COL_SCHOLAR = "Scholarship"
COL_HYPER = "Hipertension"
COL_DIAB = "Diabetes"
COL_ALCO = "Alcoholism"
COL_HAND = "Handcap"
COL_SMS = "SMS_received"
COL_SHOW = "No-show"
COL_FECHALIBRE = "FechaLibre"
COL_ESTADO = "EstadoTurno"

# Correcciones de categóricas
CORR_GENDER = {
    "FEM": "F", "FEMALE": "F", "F": "F",
    "MASC": "M", "MALE": "M", "M": "M"
}
CORR_SHOW = {
    "YES": "Yes", "yes": "Yes", "Y": "Yes",
    "NO": "No", "no": "No", "N": "No"
}

# -----------------------------
# 1. Carga y exploración inicial
# -----------------------------
df = pd.read_csv(RUTA_CSV, dtype=str)
print("Shape inicial:", df.shape)
print(df.head(3))
print("\nInfo inicial:")
print(df.info())
print("\nDescribe categórico:")
print(df.describe(include=['object']))

# -----------------------------
# 2. Valores nulos e imputación
# -----------------------------
df = df.replace(TOKENS_NULOS, np.nan)
print("\nNulos por columna:")
print(df.isna().sum())

# Convertir Age a numérico
df[COL_AGE] = pd.to_numeric(df[COL_AGE], errors="coerce")

print("\nAge antes de imputar:")
print(df[COL_AGE].agg(['count', 'mean', 'median', 'std', 'min', 'max']))

# Imputación por mediana global
mediana_age = df[COL_AGE].median(skipna=True)
df["Age_mediana"] = df[COL_AGE].fillna(mediana_age)

# Imputación por grupo (Gender)
df[COL_GENDER] = df[COL_GENDER].str.upper()
df["Age_grupo"] = df.groupby(COL_GENDER)[COL_AGE].transform(lambda s: s.fillna(s.median()))
df["Age_grupo"] = df["Age_grupo"].fillna(mediana_age)

print("\nAge después imputación por grupo:")
print(df["Age_grupo"].agg(['count', 'mean', 'median', 'std', 'min', 'max']))

# -----------------------------
# 3. Duplicados
# -----------------------------
print("\nDuplicados exactos:", df.duplicated().sum())
print("Duplicados por PatientId:", df.duplicated(subset=[COL_ID]).sum())
df = df.drop_duplicates(keep="first")

# -----------------------------
# 4. Fechas y DiffDays
# -----------------------------
df[COL_SCHEDULED] = pd.to_datetime(df[COL_SCHEDULED], errors="coerce", dayfirst=True)
df[COL_APPT] = pd.to_datetime(df[COL_APPT], errors="coerce", dayfirst=True)

df["DiffDays"] = (df[COL_APPT] - df[COL_SCHEDULED]).dt.days
print("\nRegistros con DiffDays < 0:", (df["DiffDays"] < 0).sum())
df = df[(df["DiffDays"] >= 0) | (df["DiffDays"].isna())]

# -----------------------------
# 5. Categóricas
# -----------------------------
df[COL_GENDER] = df[COL_GENDER].replace(CORR_GENDER)
df[COL_SHOW] = df[COL_SHOW].replace(CORR_SHOW)

# Baja cardinalidad
baja_card = [c for c in df.columns if df[c].nunique(dropna=True) <= 20 and df[c].dtype == object]
for c in baja_card:
    df[c] = df[c].astype("category")

# DidAttend
df["DidAttend"] = df[COL_SHOW].map({"No": 1, "Yes": 0})

# -----------------------------
# 6. Verificación de dominios
# -----------------------------
fuera_rango = (~df["Age_grupo"].between(0, 120)).sum()
print("\nEdades fuera de rango:", fuera_rango)
df = df[df["Age_grupo"].between(0, 120) | df["Age_grupo"].isna()]

# -----------------------------
# 7. Outliers
# -----------------------------
def iqr_bounds(s):
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5*iqr, q3 + 1.5*iqr

for col in ["Age_grupo", "DiffDays"]:
    if pd.api.types.is_numeric_dtype(df[col]):
        low, high = iqr_bounds(df[col].dropna())
        outliers = ((df[col] < low) | (df[col] > high)).sum()
        print(f"Outliers en {col}: {outliers}")
        sns.boxplot(x=df[col])
        plt.title(f"Boxplot de {col}")
        plt.show()

# -----------------------------
# 8. Agregaciones
# -----------------------------
print("\nEdad promedio y mediana por género:")
print(df.groupby(COL_GENDER)["Age_grupo"].agg(['mean', 'median']))

print("\nTiempo de espera promedio por asistencia:")
print(df.groupby("DidAttend")["DiffDays"].agg(['mean', 'median']))

# Guardar limpio
df.to_csv("DatasetClase3_limpio.csv", index=False)
print("\nDataset limpio guardado.")