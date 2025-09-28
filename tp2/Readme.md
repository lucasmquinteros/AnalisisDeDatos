— Explicación detallada y trazabilidad al código
Este README detalla cómo cada bloque del script resuelve las consignas del TP, con decisiones justificadas y referencias directas al código.

Cambios realizados (documentación de decisiones)
- Ampliamos TOKENS_NULOS para incluir variantes comunes ("N/A", "na", "Desconocido", "-") y asegurar una unificación robusta de faltantes.
- Implementamos dos estrategias de imputación para Age: mediana global y mediana por grupo (Gender); se reportan estadísticas comparativas y se continúa el pipeline con la imputación por grupo por preservar estructura poblacional.
- Agregamos el Paso 3 (Duplicados): se reportan duplicados exactos y por PatientId; se eliminan duplicados exactos conservando la primera ocurrencia para evitar sesgo.
- Normalizamos categóricas: Gender se mapea a {F, M} y No-show se estandariza (Yes/No). Se crea DidAttend con semántica correcta (1=asistió cuando No-show=="No"; 0=no asistió cuando "Yes").
- Verificación de dominios fortalecida: se filtran edades fuera de [0,120] y se eliminan filas con Gender inválido (distinto de F/M) y con DidAttend fuera de {0,1}.
- Outliers: se mantiene Age y se añade columna DiffDays_wins (winsorizada con IQR) para análisis robusto sin descartar casos extremos de espera.
- Fechas: corregimos el error tz-naive vs tz-aware al parsear ScheduledDay/AppointmentDay. Parseamos con utc=True y dayfirst=False, removimos la zona horaria (tz_localize(None)) y normalizamos a fecha para calcular DiffDays. Esto elimina el warning y el TypeError y asegura que DiffDays sea en días de calendario.

Requisitos previos y ejecución

- Dependencias: pandas, numpy, matplotlib, seaborn.
- Ejecución:
- Colocar tp2_limpieza_validacion.py junto a DatasetClase3_corrupto.csv.
- Ejecutar: python tp2_limpieza_validacion.py.
- Salida: DatasetClase3_limpio.csv y visualización de boxplots.
  Si los nombres de columnas difieren, ajustarlos en la sección de Configuración del script.

1. Carga y exploración inicial

- Código relevante: “Configuración del dataset” y “1. Carga y exploración inicial”.
- Qué hace:
- Carga como string: pd.read_csv(..., dtype=str) para controlar limpieza antes de tipar.
- Dimensión y tipos: imprime shape y dtypes iniciales.
- Tipado preliminar numérico: df.apply(pd.to_numeric, errors="ignore") para ver qué columnas podrían ser numéricas sin forzar errores.
- Resúmenes: describe() separado para numéricas y categóricas, y info() para estructura.
- Problema que resuelve: da una línea base de la calidad del dato y sugiere qué columnas requieren conversión o limpieza antes del análisis.

2. Valores nulos e imputación

- Código relevante: “2. Valores nulos e imputación”.
- Qué hace:
- Tokens → NaN: df.replace(TOKENS_NULOS, np.nan) unifica nulos heterogéneos como valores faltantes reales.
- Conteo de nulos: df.isna().sum() detalla las columnas afectadas.
- Conversión de Age: pd.to_numeric(..., errors="coerce") convierte edad a numérico, volviendo nulos los valores inválidos.
- Estadísticos antes: imprime count, mean, median, std, min, max previos a imputar.
- Imputación 1 (mediana global): fillna(mediana_global) — robusta frente a outliers.
- Imputación 2 (por grupo): groupby(género).transform(lambda s: s.fillna(s.median())) — preserva diferencias por subpoblación. Fallback a mediana global si quedan nulos.
- Decisión: se sigue con la versión imputada por grupo (más informativa para análisis segmentado).
- Cómo demuestra el efecto: imprime los estadísticos antes y después para comparar el impacto de cada imputación.

3. Duplicados

- Código relevante: “3. Duplicados”.
- Qué hace:
- Duplicados exactos: df.duplicated().sum() reporta clones completos.
- Duplicados por ID: df.duplicated(subset=[COL_ID]).sum() identifica potenciales múltiples registros por identificador.
- Decisión: drop_duplicates(keep="first") elimina duplicados exactos, manteniendo la primera ocurrencia para evitar sesgo por clonación.
- Justificación: duplicados exactos no agregan información y pueden sesgar conteos y promedios.

4. Fechas y DiffDays

- Código relevante: “4. Fechas y DiffDays”.
- Qué hace:
- Conversión robusta: pd.to_datetime(..., errors="coerce", dayfirst=True) estandariza formato regional y envía fechas inválidas a NaN.
- DiffDays: (AppointmentDay - ScheduledDay).dt.days calcula días de espera.
- Validación temporal: cuenta DiffDays < 0 e elimina esos registros por inconsistencia (turno anterior al agendamiento).
- Justificación: un turno no puede ocurrir antes de ser programado; conservarlos contaminaría análisis de tiempos de espera.

5. Categóricas

- Código relevante: “5. Categóricas”.
- Qué hace:
- Normalización de escritura: replace(CORR_GENDER).str.upper() y replace(CORR_SHOW) unifican variantes (“Fem”→“F”, “NO”→“No”).
- Baja cardinalidad: detecta columnas con ≤ 20 categorías y las castea a category para consistencia y eficiencia.
- Variable DidAttend: map({"No": 1, "Yes": 0}) crea un indicador 1/0 (asistencia real).
- Justificación: valores consistentes reducen ambigüedad en análisis y evitan duplicación de categorías por typos.

6. Verificación de dominios

- Código relevante: “6. Verificación de dominios”.
- Qué hace:
- Edades plausibles: cuenta y elimina edades fuera de [0, 120] con between(0, 120).
- Revisión de categorías: imprime categorías presentes en Gender y No-show para auditoría final.
- Decisión: eliminar edades implausibles; documentar categorías finales para trazabilidad.

7. Outliers con IQR y visualización

- Código relevante: “7. Outliers (IQR) y boxplots”.
- Qué hace:
- Cálculo de límites IQR: función iqr_bounds obtiene Q_1, Q_3, IQR y límites.
  \text{IQR} = Q_3 - Q_1,\quad L = Q_1 - 1.5 \cdot \text{IQR},\quad U = Q_3 + 1.5 \cdot \text{IQR}- Conteo de outliers: compara contra [L, U] en Age y DiffDays.
- Boxplots: seaborn.boxplot para inspección visual de extremos.
- Tratamiento: se decide mantener outliers de Age (posibles valores reales en extremos) y se ilustra winsorización en DiffDays con clip para análisis robusto en presencia de colas largas.
- Justificación: los tiempos de espera pueden tener colas pesadas por reprogramaciones; winsorizar estabiliza promedios sin descartar casos.

8. Primeras agregaciones

- Código relevante: “8. Primeras agregaciones”.
- Qué hace:
- Edad por género: groupby(Gender)[Age].agg(['count','mean','median','std']) para estadísticos descriptivos.
- Espera por asistencia: groupby(DidAttend)['DiffDays'].agg(...) para entender relación entre espera y asistencia.
- Groupby múltiple: groupby([Gender, DidAttend]).agg(...) combina segmentación y múltiples métricas.
- Valor: provee tablas base para el informe con resultados clave y comprensibles.

Decisiones de limpieza resumidas

- Tokens nulos: unificados a NaN para tratamiento consistente.
- Imputación de Age: se prefiere por grupo (género) con fallback a mediana global.
- Duplicados exactos: eliminados conservando primera aparición.
- Fechas inválidas: registros con DiffDays < 0 eliminados.
- Categóricas: estandarización de valores y conversión a category.
- Dominios: edades fuera de [0, 120] eliminadas.
- Outliers: Age se conserva; DiffDays se winsoriza en columna adicional (DiffDays_wins) para análisis robusto.

Cómo usar los resultados en tu informe PDF

- Problemas encontrados: reportes de nulos, duplicados, DiffDays < 0, categorías desalineadas, edades fuera de rango, outliers.
- Decisiones: justificar cada acción con una línea (ver “Decisiones de limpieza resumidas”).
- Ejemplos de resultados:
- Pegar tablas de “Edad por género”, “DiffDays por DidAttend” y el groupby múltiple.
- Incluir antes vs. después de imputación de Age (mediana global vs. por grupo).
- Incluir gráficos de boxplot de Age y DiffDays.
  ¿Querés que lo deje adaptado a las categorías específicas que trae tu CSV si cambian de “Yes/No” a “0/1” o “Si/No”? Pasame un vistazo de los valores únicos de Gender y No-show y te ajusto el mapeo al toque.



Explicación detallada del código (con citas literales)

A continuación se documenta el script tp2_limpieza_validacion.py, citando literalmente los bloques de código y explicando el porqué de cada decisión (nulos, imputación por mediana/grupo, edades negativas, fechas, categóricas, outliers y agregaciones).

1) Configuración y constantes (cita literal)

```
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
```

- Por qué: unificamos tokens nulos frecuentes en español/inglés y normalizamos categorías con mapeos explícitos para evitar variantes como "Fem"/"Female" o "YES"/"Y".

2) 1. Carga y exploración inicial (cita literal + explicación)

```
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
```

- Por qué dtype=str: evita parseos prematuros que oculten datos corruptos. Luego convertimos numéricos con errors='coerce' para mandar a NaN los valores inválidos y poder auditarlos.

3) 2. Tratamiento de valores nulos e imputación (cita literal + explicación)

```
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
```

- Por qué mediana y no media: la mediana es robusta frente a outliers. En distribuciones sesgadas (como puede ocurrir con edades o tiempos), la media se desplaza por valores extremos; la mediana mantiene el centro típico.
- Por qué imputación por grupo: al imputar por género preservamos diferencias estructurales entre subpoblaciones (p.ej., si las edades típicas difieren por F/M). Usamos mediana global como respaldo cuando el grupo no tiene suficiente información.
- Edades negativas: son implausibles; primero las marcamos como faltantes (NaN) para no contaminarlas en los cálculos y luego, tras imputar, verificamos dominios (ver punto 6). Si algún valor permanece fuera de rango o inconsistente, se elimina.
- Columnas con >90% nulos: se eliminan porque aportan muy poca información y pueden introducir ruido.

4) 3. Duplicados (cita literal + explicación)

```
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
```

- Por qué: los duplicados exactos no agregan información y sesgan conteos y promedios. Mantener la primera ocurrencia preserva el registro original.

5) 4. Fechas y DiffDays (cita literal + explicación)

```
# 4. Procesamiento de fechas y DiffDays

def procesar_fechas(df):
    print("\n4. Procesamiento de fechas y DiffDays")
    
    # Convertir fechas asegurando misma conciencia de zona horaria y sin ambigüedades
    # Usamos utc=True para que ambas series sean tz-aware en UTC y luego quitamos el tz para operar sin conflictos.
    df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'], errors='coerce', dayfirst=False, utc=True).dt.tz_localize(None)
    df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'], errors='coerce', dayfirst=False, utc=True).dt.tz_localize(None)
    
    # Calcular diferencia en días de calendario (normalizando a medianoche)
    df['DiffDays'] = (df['AppointmentDay'].dt.normalize() - df['ScheduledDay'].dt.normalize()).dt.days
    
    # Eliminar registros con fechas inválidas o inconsistentes
    registros_invalidos = df['DiffDays'] < 0
    print(f"\nRegistros con DiffDays negativos (eliminados): {registros_invalidos.sum()}")
    df = df[~registros_invalidos]
    
    return df
```

- Por qué utc=True + tz_localize(None): evitamos el error "tz-naive vs tz-aware" y los warnings de pandas; normalizamos a medianoche para comparar días calendario.
- Por qué eliminar DiffDays < 0: un turno no puede ocurrir antes de ser agendado; mantener esos registros introduciría inconsistencias en tiempos de espera.

6) 5. Categóricas (cita literal + explicación)

```
# 5. Limpieza de variables categóricas
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
            print(f"\nCategorías en {col}:", df[col].unique())
    
    return df
```

- Por qué normalizar: evita duplicar categorías por mayúsculas/typos (Fem/fem/FEMALE → F; YES/Y → Yes).
- DidAttend: mapeamos explícitamente la semántica del dataset (No-show == 'No' → asistió) y soportamos variantes 0/1 en texto o número.
- Tipo category: más eficiente en memoria y más claro para análisis descriptivo.

7) 6. Verificación de dominios (cita literal + explicación)

```
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
```

- Por qué rango [0, 120]: basado en plausibilidad humana; valores negativos o >120 son errores. Ya los marcamos como NaN antes; aquí aseguramos que todo valor final sea plausible. Si no, se elimina.
- Validación de categorías: removemos registros con categorías no válidas para evitar mezclas de clases inexistentes.

8) 7. Outliers (IQR), visualización y winsorización (cita literal + explicación)

```
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
    
    # Análisis para Age y DiffDays
    for columna in ['Age', 'DiffDays']:
        l_inf, l_sup = calcular_limites_iqr(df[columna])
        outliers = df[(df[columna] < l_inf) | (df[columna] > l_sup)]
        print(f"\nOutliers en {columna}: {len(outliers)} ({len(outliers)/len(df)*100:.2f}%)")
        
        # Crear versión winsorizada para DiffDays
        if columna == 'DiffDays':
            df[f'{columna}_wins'] = df[columna].clip(l_inf, l_sup)
        
        # Visualización
        plt.figure(figsize=(10, 4))
        sns.boxplot(x=df[columna])
        plt.title(f'Boxplot de {columna}')
        plt.show()
    
    return df
```

- Por qué IQR: método estándar, no paramétrico, robusto a colas pesadas.
- Por qué winsorizar DiffDays: los tiempos de espera suelen tener colas largas por reprogramaciones; winsorizar estabiliza métricas sin eliminar casos. En Age preferimos conservar valores, tras validar dominios.
- Gráficos: se generan boxplots para inspeccionar la magnitud y naturaleza de outliers.

9) 8. Agregaciones iniciales (cita literal + explicación)

```
# 8. Agregaciones iniciales
def realizar_agregaciones(df):
    print("\n8. Agregaciones iniciales")
    
    # Estadísticos por género
    print("\nEstadísticos de edad por género:")
    print(df.groupby('Gender')['Age'].agg(['count', 'mean', 'median', 'std']))
    
    # Estadísticos de espera por asistencia
    print("\nEstadísticos de días de espera por asistencia:")
    print(df.groupby('DidAttend')['DiffDays'].agg(['count', 'mean', 'median', 'std']))
    
    # Agregación múltiple
    print("\nEstadísticos combinados por género y asistencia:")
    print(df.groupby(['Gender', 'DidAttend']).agg({
        'Age': ['count', 'mean'],
        'DiffDays': ['mean', 'median']
    }))
    
    return df
```

- Valor: proveen tablas listas para pegar en el informe y comenzar la interpretación.

10) Orquestación (main) (cita literal)

```
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
```

- Flujo: cada paso imprime resúmenes para auditoría y produce una versión limpia persistida en CSV.

Sección para gráficos y análisis (deja tus figuras aquí)

- Boxplot de Age
  - Inserta aquí la imagen del boxplot generada por el script.
  - Sugerencia de ruta: docs/boxplot_age.png
  - Placeholders Markdown:
    - ![Boxplot de Age](docs/boxplot_age.png)
  - Análisis sugerido:
    - Porcentaje de outliers detectados.
    - ¿Hay asimetrías? ¿Cola derecha/izquierda?
    - ¿La distribución cambia por género? (puede hacerse un boxplot por hue si se desea ampliar).

- Boxplot de DiffDays
  - Inserta aquí la imagen del boxplot de DiffDays.
  - ![Boxplot de DiffDays](docs/boxplot_diffdays.png)
  - Compara con versión winsorizada:
    - ![Boxplot de DiffDays (wins)](docs/boxplot_diffdays_wins.png)
  - Análisis sugerido:
    - ¿Qué tanto redujo la winsorización la influencia de outliers?
    - ¿Cómo cambian la media y la mediana antes vs. después?

Justificación de decisiones clave (resumen)

- Nulos → Mediana/Mediana por grupo: la mediana reduce el impacto de outliers; agrupar por género preserva heterogeneidad poblacional. La media se descartó por sensibilidad a extremos.
- Edades negativas: no son plausibles. Se marcan como NaN y se imputan; posteriormente se verifica el dominio [0, 120] y se eliminan filas inconsistentes si correspondiera.
- DiffDays < 0: inconsistente temporalmente; se eliminan para no sesgar análisis de espera.
- Categóricas normalizadas: asegura consistencia semántica y evita duplicación de categorías por variaciones de escritura.
- Outliers: se ilustran y se aplica winsorización a DiffDays para análisis robusto, manteniendo información.

Cómo usar este README

- Copiar y pegar las citas de código en tu informe si necesitás justificar cada paso.
- Pegar las imágenes de boxplots en las secciones indicadas y completar el análisis guiado.
- Integrar las tablas impresas por realizar_agregaciones como evidencia de resultados.
