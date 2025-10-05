import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración inicial
ARCHIVO_ENTRADA = "DatasetClase3_corrupto.csv"
ARCHIVO_SALIDA = "DatasetClase3_limpio.csv"

# Tokens que representan valores nulos (extendidos para casos comunes en español/inglés)
TOKENS_NULOS = ['nan', 'NA', 'na', 'N/A', 'null', '', 'None', '-', 'Desconocido']

# Mapeos para normalizar categóricas
CORR_GENDER = {
    'FEM': 'F', 'FEMALE': 'F', 'F': 'F',
    'MASC': 'M', 'MALE': 'M', 'M': 'M'
}
CORR_SHOW = {
    'YES': 'Yes', 'yes': 'Yes', 'Y': 'Yes',
    'NO': 'No', 'no': 'No', 'N': 'No'
}

# 1. Carga y exploración inicial
def cargar_y_explorar():
    print("1. Carga y exploración inicial")
    df = pd.read_csv(ARCHIVO_ENTRADA, dtype=str)
    print("\nDimensiones iniciales:", df.shape)
    print("\nTipos de datos iniciales:")
    print(df.dtypes)
    
    # Convertir columnas numéricas de forma segura
    columnas_numericas = ['PatientId', 'AppointmentID', 'Age', 'Scholarship', 
                         'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 'SMS_received']
    
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print("\nResumen de columnas numéricas:")
    print(df[columnas_numericas].describe())
    
    return df

# 2. Limpieza de valores nulos
def limpiar_nulos(df):
    print("\n2. Tratamiento de valores nulos")
    
    # Unificar representación de nulos
    df = df.replace(TOKENS_NULOS, np.nan)
    
    print("\nCantidad de valores nulos por columna:")
    print(df.isna().sum())
    
    # Eliminar columnas con demasiados nulos (>90%)
    umbral_nulos = len(df) * 0.9
    cols_eliminar = df.columns[df.isna().sum() > umbral_nulos]
    df = df.drop(columns=cols_eliminar)
    print("\nColumnas eliminadas por exceso de nulos:", list(cols_eliminar))
    
    # Validar y limpiar edad
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    print("\nEstadísticas de Age antes de imputación:")
    print(df['Age'].agg(['count', 'mean', 'median', 'std', 'min', 'max']))
    
    # Filtrar edades no plausibles antes de imputar
    df.loc[~df['Age'].between(-1, 120), 'Age'] = np.nan
    
    # Imputación 1: mediana global
    mediana_global = df['Age'].median()
    df['Age_mediana'] = df['Age'].fillna(mediana_global)
    print("\nEstadísticas de Age con imputación por mediana global:")
    print(df['Age_mediana'].agg(['count', 'mean', 'median', 'std', 'min', 'max']))

    # Imputación 2: por grupo (Gender) con fallback a mediana global
    # Primero normalizamos Gender a mayúsculas para agrupar de forma consistente
    df['Gender'] = df['Gender'].str.upper()
    df['Age_grupo'] = df.groupby('Gender')['Age'].transform(
        lambda x: x.fillna(x.median())
    )
    df['Age_grupo'] = df['Age_grupo'].fillna(mediana_global)
    print("\nEstadísticas de Age con imputación por grupo (Gender):")
    print(df['Age_grupo'].agg(['count', 'mean', 'median', 'std', 'min', 'max']))

    # Decisión: continuar el pipeline usando la versión imputada por grupo
    df['Age'] = df['Age_grupo']
    
    return df

# 3. Duplicados

def manejar_duplicados(df):
    print("\n3. Duplicados")
    duplicados_exactos = df.duplicated().sum()
    print(f"Duplicados exactos: {duplicados_exactos}")
    if 'PatientId' in df.columns:
        duplicados_id = df.duplicated(subset=['PatientId']).sum()
        print(f"Duplicados por PatientId: {duplicados_id}")
    else:
        print("Columna PatientId no encontrada para chequeo específico de ID.")
    # Decisión: eliminar duplicados exactos conservando la primera ocurrencia
    if duplicados_exactos > 0:
        df = df.drop_duplicates(keep='first')
        print("Duplicados exactos eliminados (keep='first').")
    return df


# 4. Procesamiento de fechas y DiffDays

def procesar_fechas(df):
    print("\n4. Procesamiento de fechas y DiffDays")

    # Opción 1: Si conoces el formato exacto (RECOMENDADO - más rápido y sin warnings)
    # Formato ISO común: '2016-04-29T18:38:08Z'
    try:
        df['ScheduledDay'] = pd.to_datetime(
            df['ScheduledDay'],
            format='%Y-%m-%dT%H:%M:%SZ',
            errors='coerce'
        ).dt.tz_localize(None)

        df['AppointmentDay'] = pd.to_datetime(
            df['AppointmentDay'],
            format='%Y-%m-%dT%H:%M:%SZ',
            errors='coerce'
        ).dt.tz_localize(None)
    except:
        # Opción 2: Si el formato varía, inferir pero sin utc=True
        print("Formato no coincide, usando parseo flexible...")
        df['ScheduledDay'] = pd.to_datetime(
            df['ScheduledDay'],
            errors='coerce'
        )
        df['AppointmentDay'] = pd.to_datetime(
            df['AppointmentDay'],
            errors='coerce'
        )

    # Calcular diferencia en días de calendario (normalizando a medianoche)
    df['DiffDays'] = (df['AppointmentDay'].dt.normalize() - df['ScheduledDay'].dt.normalize()).dt.days

    # Eliminar registros con fechas inválidas o inconsistentes
    registros_invalidos = df['DiffDays'] < 0
    print(f"\nRegistros con DiffDays negativos (eliminados): {registros_invalidos.sum()}")
    df = df[~registros_invalidos]

    return df
## 5. Limpieza de variables categóricas
def limpiar_categoricas(df):
    print("\n5. Limpieza de variables categóricas")

    # Normalizar escritura de Gender y No-show
    df['Gender'] = df['Gender'].str.upper().replace(CORR_GENDER)
    df['No-show'] = df['No-show'].replace(CORR_SHOW)

    # Crear variable DidAttend (1 = asistió, 0 = no asistió)
    # En este dataset: No-show == 'No' implica que SÍ asistió.
    df['DidAttend'] = df['No-show'].map({'No': 1, 'Yes': 0, 0: 1, 1: 0, '0': 1, '1': 0})

    # Convertir variables de baja cardinalidad a category
    categoricas = ['Gender', 'DidAttend', 'Scholarship', 'Hipertension',
                  'Diabetes', 'Alcoholism', 'SMS_received', 'No-show']
    for col in categoricas:
        if col in df.columns:
            df[col] = df[col].astype('category')
            df[col] = df[col].cat.remove_unused_categories()
            print(f"\nCategorías en {col}:", df[col].unique())
    
    return df

# 6. Verificación de dominios
def verificar_dominios(df):
    print("\n6. Verificación de dominios")
    
    # Verificar edades plausibles
    edades_invalidas = ~df['Age'].between(0, 120)
    print(f"Registros con edades fuera de rango [0, 120]: {edades_invalidas.sum()}")
    df = df[~edades_invalidas]

    # Verificar y depurar valores de género (solo 'F' y 'M' válidos)
    valores_gender = df['Gender'].unique()
    print("\nValores únicos en Gender (antes):", valores_gender)
    mask_genero_valido = df['Gender'].isin(['F', 'M'])
    inval_genero = (~mask_genero_valido).sum()
    if inval_genero > 0:
        print(f"Registros con Gender inválido (eliminados): {inval_genero}")
        df = df[mask_genero_valido]

    # Verificar y depurar valores en DidAttend (0/1)
    if 'DidAttend' in df.columns:
        valores_att = df['DidAttend'].unique()
        print("Valores únicos en DidAttend (antes):", valores_att)
        mask_att_valido = df['DidAttend'].isin([0, 1]) | df['DidAttend'].isin(['0', '1'])
        inval_att = (~mask_att_valido).sum()
        if inval_att > 0:
            print(f"Registros con DidAttend inválido (eliminados): {inval_att}")
            df = df[mask_att_valido]
        # Asegurar tipo consistente
        df['DidAttend'] = pd.to_numeric(df['DidAttend'], errors='coerce').astype('Int64')
        df['DidAttend'] = df['DidAttend'].astype('category')
    
    # Resumen final de dominios
    print("\nValores únicos en Gender (después):", df['Gender'].unique())
    if 'DidAttend' in df.columns:
        print("Valores únicos en DidAttend (después):", df['DidAttend'].unique())
    
    return df


# 7. Análisis de outliers
def analizar_outliers(df):
    print("\n7. Análisis de outliers")

    def calcular_limites_iqr(serie):
        Q1 = serie.quantile(0.25)
        Q3 = serie.quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        return limite_inferior, limite_superior

    # Crear directorio si no existe
    import os
    os.makedirs('./docs', exist_ok=True)

    # Análisis para Age y DiffDays
    for columna in ['Age', 'DiffDays']:
        l_inf, l_sup = calcular_limites_iqr(df[columna])
        outliers = df[(df[columna] < l_inf) | (df[columna] > l_sup)]
        print(f"\nOutliers en {columna}: {len(outliers)} ({len(outliers) / len(df) * 100:.2f}%)")

        # Crear versión winsorizada para DiffDays
        if columna == 'DiffDays':
            df[f'{columna}_wins'] = df[columna].clip(l_inf, l_sup)

        # Visualización
        plt.figure(figsize=(10, 4))
        sns.boxplot(x=df[columna])
        plt.title(f'Boxplot de {columna}')

        # IMPORTANTE: Guardar ANTES de mostrar
        plt.savefig(f'./docs/{columna}_boxplot.png', dpi=300, bbox_inches='tight')
        plt.show()  # Ahora sí mostrar (cierra la figura)
        plt.close()  # Liberar memoria
    # Después del loop, agregar comparación
    if 'DiffDays_wins' in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Original
        sns.boxplot(x=df['DiffDays'], ax=axes[0])
        axes[0].set_title('DiffDays (Original)')
        axes[0].set_xlabel('Días de espera')

        # Winsorizado
        sns.boxplot(x=df['DiffDays_wins'], ax=axes[1], color='orange')
        axes[1].set_title('DiffDays (Winsorizado)')
        axes[1].set_xlabel('Días de espera')

        plt.tight_layout()
        plt.savefig('./docs/diffdays_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()

        print("\nComparación guardada en: ./docs/diffdays_comparison.png")

    return df


def realizar_agregaciones(df):
    print("\n8. Agregaciones iniciales")

    # Estadísticos por género (observed=True evita categorías vacías)
    print("\nEstadísticos de edad por género:")
    print(df.groupby('Gender', observed=True)['Age'].agg(['count', 'mean', 'median', 'std']))

    # Estadísticos de espera por asistencia
    print("\nEstadísticos de días de espera por asistencia:")
    print(df.groupby('DidAttend', observed=True)['DiffDays'].agg(['count', 'mean', 'median', 'std']))

    # Agregación múltiple
    print("\nEstadísticos combinados por género y asistencia:")
    print(df.groupby(['Gender', 'DidAttend'], observed=True).agg({
        'Age': ['count', 'mean'],
        'DiffDays': ['mean', 'median']
    }))

    return df

def main():
    df = cargar_y_explorar()
    df = limpiar_nulos(df)
    df = manejar_duplicados(df)
    df = procesar_fechas(df)
    df = limpiar_categoricas(df)
    df = verificar_dominios(df)
    df = analizar_outliers(df)
    df = realizar_agregaciones(df)
    
    # Guardar resultado
    df.to_csv(ARCHIVO_SALIDA, index=False)
    print(f"\nDatos limpios guardados en {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    main()
