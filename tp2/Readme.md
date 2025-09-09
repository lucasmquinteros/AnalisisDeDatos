— Explicación detallada y trazabilidad al código
Este README detalla cómo cada bloque del script resuelve las consignas del TP, con decisiones justificadas y referencias directas al código.

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
