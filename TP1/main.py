"""
Tareas a realizar: 1. Cargar el dataset en un DataFrame.
2. Explorar la estructura de los datos: dimensiones, tipos de datos, primeras filas.
3. Detectar y manejar valores nulos.
 4. Identificar y eliminar duplicados.
 5. Corregir valores erróneos o inconsistentes.
 6. Realizar un análisis descriptivo de cada columna.
 7. Generar al menos 3 visualizaciones que ayuden a entender la información.
 8. Elaborar un informe en pdf con capturas de pantalla sobre lo realizado, incluyendo conclusiones sobre el dataset original y el dataset limpio.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración para visualizaciones más lindas
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# 1. Cargamos el dataset
print("1. Cargando el dataset")
df = pd.read_csv("./dataset2.csv")
print("Dataset cargado exitosamente.\n")

# Guardamos una copia del dataset original para comparar después
df_original = df.copy()

# 2. Exploramos datos, dimensiones y filas
print("2. Explorando la estructura de los datos")
print(f"Dimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")
print("\nPrimeras 5 filas del dataset:")
print(df.head())
print("\nTipos de datos:")
print(df.dtypes)
print("\nInformación general del dataset:")
print(df.info())
print("\nEstadísticas básicas:")
print(df.describe(include='all'))
print("\n")

# 3. Detectar y manejar valores nulos
print("3. Detectando y manejando valores nulos")
print("Valores nulos por columna:")
print(df.isnull().sum())

# Visualizar valores nulos
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
plt.title('Mapa de calor de valores nulos')
plt.tight_layout()
plt.savefig('valores_nulos.png')
plt.close()

# Manejar valores nulos
# Para la columna Edad, reemplazamos 'desconocido' por NaN primero
df['Edad'] = df['Edad'].replace('desconocido', np.nan)
# Convertimos Edad a numérico
df['Edad'] = pd.to_numeric(df['Edad'], errors='coerce')
# Reemplazamos valores nulos en Edad con la mediana
edad_mediana = df['Edad'].median()
df['Edad'] = df['Edad'].fillna(edad_mediana)

# Para la columna Ingresos, reemplazamos '?' por NaN
df['Ingresos'] = df['Ingresos'].replace('?', np.nan)
# Convertimos Ingresos a numérico
df['Ingresos'] = pd.to_numeric(df['Ingresos'], errors='coerce')
# Reemplazamos valores nulos en Ingresos con la mediana
ingresos_mediana = df['Ingresos'].median()
df['Ingresos'] = df['Ingresos'].fillna(ingresos_mediana)

print("\nValores nulos después de la limpieza:")
print(df.isnull().sum())
print("\n")

# 4. Identificar y eliminar duplicados
print("4. Identificando y eliminando duplicados")
print(f"Número de filas duplicadas: {df.duplicated().sum()}")
# Mostramos las filas duplicadas
if df.duplicated().sum() > 0:
    print("Filas duplicadas:")
    print(df[df.duplicated(keep='first')])
    # Eliminamos duplicados
    df = df.drop_duplicates(keep='first')
    print(f"Dataset después de eliminar duplicados: {df.shape[0]} filas")
print("\n")

# 5. Corregir valores erróneos o inconsistentes
print("5. Corrigiendo valores erróneos o inconsistentes")

# Verificamos valores únicos en cada columna categórica
print("Valores únicos en columnas categóricas:")
for col in ['Ciudad', 'Ocupacion']:
    print(f"{col}: {df[col].unique()}")

# Aseguramos que ID sea único
print(f"¿Todos los IDs son únicos? {df['ID'].is_unique}")
if not df['ID'].is_unique:
    print("Hay IDs duplicados. Corrigiendo...")
    # Identificamos IDs duplicados
    duplicated_ids = df[df['ID'].duplicated(keep=False)]
    print("IDs duplicados:")
    print(duplicated_ids)
    # Podríamos asignar nuevos IDs o mantener solo la primera ocurrencia
    # Aquí optamos por mantener solo la primera ocurrencia
    df = df.drop_duplicates(subset=['ID'], keep='first')
    print(f"Dataset después de corregir IDs duplicados: {df.shape[0]} filas")

# Verificamos rangos de edad e ingresos para detectar outliers
print("\nEstadísticas de Edad e Ingresos:")
print(df[['Edad', 'Ingresos']].describe())

# Podríamos aplicar límites a valores extremos si fuera necesario
# Por ejemplo, limitar edades a un rango razonable
df['Edad'] = df['Edad'].clip(18, 80)  # Suponiendo que queremos limitar edades entre 18 y 80

print("\nDatos después de la limpieza:")
print(df.head())
print("\n")

# 6. Realizar un análisis descriptivo de cada columna
print("6. Realizando análisis descriptivo de cada columna")

# Análisis de variables numéricas
print("Estadísticas de variables numéricas:")
print(df[['Edad', 'Ingresos']].describe())

# Análisis de variables categóricas
print("\nDistribución de Ciudad:")
print(df['Ciudad'].value_counts())
print("\nDistribución de Ocupación:")
print(df['Ocupacion'].value_counts())

# Análisis de correlación entre variables numéricas
print("\nCorrelación entre Edad e Ingresos:")
print(df[['Edad', 'Ingresos']].corr())
print("\n")

# 7. Generar visualizaciones
print("7. Generando visualizaciones")

# Visualización 1: Distribución de edades
plt.figure(figsize=(10, 6))
sns.histplot(df['Edad'], kde=True, bins=10)
plt.title('Distribución de Edades')
plt.xlabel('Edad')
plt.ylabel('Frecuencia')
plt.tight_layout()
plt.savefig('distribucion_edades.png')
plt.close()

# Visualización 2: Distribución de ingresos por ocupación
plt.figure(figsize=(12, 8))
sns.boxplot(x='Ocupacion', y='Ingresos', data=df)
plt.title('Distribución de Ingresos por Ocupación')
plt.xlabel('Ocupación')
plt.ylabel('Ingresos')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('ingresos_por_ocupacion.png')
plt.close()

# Visualización 3: Conteo de personas por ciudad
plt.figure(figsize=(10, 6))
ciudad_counts = df['Ciudad'].value_counts()
sns.barplot(x=ciudad_counts.index, y=ciudad_counts.values)
plt.title('Número de Personas por Ciudad')
plt.xlabel('Ciudad')
plt.ylabel('Cantidad')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('personas_por_ciudad.png')
plt.close()

# Visualización 4 (bonus): Relación entre edad e ingresos
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Edad', y='Ingresos', hue='Ocupacion', data=df)
plt.title('Relación entre Edad e Ingresos por Ocupación')
plt.xlabel('Edad')
plt.ylabel('Ingresos')
plt.tight_layout()
plt.savefig('edad_vs_ingresos.png')
plt.close()

print("Visualizaciones guardadas como archivos PNG.")
print("\n")

# 8. Elaborar informe
print("8. Elaboración de informe")
print("""
Para completar la tarea 8, deberás crear un informe PDF que incluya:
1. Capturas de pantalla de los resultados y visualizaciones generadas
2. Descripción del proceso de limpieza y análisis realizado
3. Conclusiones sobre el dataset original y el dataset limpio
4. Insights obtenidos de las visualizaciones

Puedes usar herramientas como Word, Google Docs o LaTeX para crear el informe PDF.
""")

# Comparación del dataset original y limpio
print("\nComparación del dataset original y limpio:")
print(f"Dataset original: {df_original.shape[0]} filas x {df_original.shape[1]} columnas")
print(f"Dataset limpio: {df.shape[0]} filas x {df.shape[1]} columnas")

# Guardar el dataset limpio
df.to_csv("dataset2_limpio.csv", index=False)
print("\nDataset limpio guardado como 'dataset2_limpio.csv'")
