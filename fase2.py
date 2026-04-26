"""
╔══════════════════════════════════════════════════════════════╗
║        ESCAPE ROOM IA · FASE 2: PERFIL DE VÍCTIMA           ║
╚══════════════════════════════════════════════════════════════╝

MISIÓN:
  Habéis obtenido los logs de acceso de SysPanel, un sistema
  de administración corporativo. Hay un usuario administrador
  mezclado entre cientos de registros normales.

  Vuestro trabajo:
    1. Usar K-Means para agrupar los logs en clusters.
    2. Analizar los clusters e identificar cuál corresponde
       al administrador (comportamiento distinto al resto).
    3. Usar el patrón del admin para construir una
       SQL Injection que os dé acceso al panel.

SERVIDOR: http://localhost:5000/login

COLUMNAS DEL DATASET (logs.csv):
  - id                  → identificador de sesión
  - ip                  → dirección IP
  - hora                → hora del día (0.0 – 23.99)
  - duracion_min        → duración de la sesión en minutos
  - n_peticiones        → número de peticiones realizadas
  - pct_rutas_privadas  → % de accesos a rutas privadas (0-1)

LIBRERÍAS: pandas, sklearn, matplotlib (opcional para visualizar)
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt   # opcional pero recomendado


# ══════════════════════════════════════════════════════════════
# PASO 1: Cargar y explorar los datos
# ══════════════════════════════════════════════════════════════

def cargar_datos(ruta):
    """
    Carga el CSV y devuelve un DataFrame de pandas.

    PSEUDOCÓDIGO:
      df = pd.read_csv(ruta)
      imprimir df.head() para ver las primeras filas
      imprimir df.describe() para ver estadísticas básicas
      devolver df
    """
    # TODO: implementa esta función
    pass


# ══════════════════════════════════════════════════════════════
# PASO 2: Preparar las features para clustering
# ══════════════════════════════════════════════════════════════

def preparar_features(df):
    """
    Selecciona y normaliza las columnas relevantes para clustering.
    Normalizar es esencial: si 'duracion_min' va de 0-120 y
    'pct_rutas_privadas' va de 0-1, la primera dominaría el clustering.

    PSEUDOCÓDIGO:
      columnas = ['hora', 'duracion_min', 'n_peticiones', 'pct_rutas_privadas']
      X = df[columnas].values           ← array numpy con los datos

      scaler = StandardScaler()
      X_norm = scaler.fit_transform(X)  ← media=0, std=1 en cada columna

      devolver X_norm, columnas

    NOTA: StandardScaler hace que cada columna tenga media 0 y
    desviación típica 1, así todas las features pesan igual.
    """
    # TODO: implementa esta función
    pass


# ══════════════════════════════════════════════════════════════
# PASO 3: Aplicar K-Means
# ══════════════════════════════════════════════════════════════

def aplicar_kmeans(X_norm, k=3):
    """
    Aplica K-Means con k clusters y devuelve las etiquetas.

    PSEUDOCÓDIGO:
      modelo = KMeans(n_clusters=k, random_state=42, n_init=10)
      modelo.fit(X_norm)
      etiquetas = modelo.labels_    ← array con el cluster de cada fila
      devolver etiquetas, modelo

    NOTA: n_init=10 significa que prueba 10 inicializaciones distintas
    y se queda con la mejor (evita mínimos locales).
    """
    # TODO: implementa esta función
    pass


# ══════════════════════════════════════════════════════════════
# PASO 4: Analizar los clusters
# ══════════════════════════════════════════════════════════════

def analizar_clusters(df, etiquetas, columnas):
    """
    Calcula la media de cada feature por cluster para interpretarlos.

    PSEUDOCÓDIGO:
      df_analisis = df[columnas].copy()
      df_analisis['cluster'] = etiquetas

      para cada cluster en [0, 1, 2, ...]:
          subset = df_analisis donde cluster == cluster
          imprimir tamaño del subset
          imprimir media de cada columna en ese subset

      devolver df con columna cluster añadida

    PISTA: usa df.groupby('cluster')[columnas].mean()
    para ver las medias de golpe.
    """
    # TODO: implementa esta función
    pass


# ══════════════════════════════════════════════════════════════
# PASO 5 (opcional): Visualizar los clusters
# ══════════════════════════════════════════════════════════════

def visualizar(df_con_cluster, columnas):
    """
    Dibuja un scatter plot para ver la separación entre clusters.

    PSEUDOCÓDIGO:
      colores = {0: 'steelblue', 1: 'tomato', 2: 'gold'}
      para cada cluster en [0, 1, 2]:
          subset = filas del cluster
          plt.scatter(subset['hora'], subset['duracion_min'],
                      color=colores[cluster], label=f'Cluster {cluster}',
                      alpha=0.6)
      plt.xlabel('hora')
      plt.ylabel('duracion_min')
      plt.legend()
      plt.title('Clusters de sesiones')
      plt.show()

    PISTA: también podéis probar n_peticiones vs pct_rutas_privadas.
    """
    # TODO: implementa esta función (opcional)
    pass


# ══════════════════════════════════════════════════════════════
# PASO 6: Construir la SQL Injection
# ══════════════════════════════════════════════════════════════

"""
Una vez identificado el cluster del administrador, necesitáis
acceder al servidor como él SIN conocer su contraseña.

El formulario de login ejecuta esta consulta (vulnerable):

  SELECT * FROM usuarios
  WHERE username='<INPUT>' AND password='<INPUT>'

Una SQL Injection clásica hace que el AND password=... sea ignorado.

TÉCNICA — comentario SQL:
  Si username = sysadmin'--
  La query se convierte en:
    SELECT * FROM usuarios WHERE username='sysadmin'--' AND password='...'
  Todo lo que hay después de -- es un comentario → la contraseña se ignora.

PREGUNTA: ¿Cómo sabéis que el username es 'sysadmin'?
  Mirad las IPs del cluster admin en los logs. El patrón de
  comportamiento os da pistas sobre qué username buscar. Podéis
  también intentar: admin, administrator, root, sysadmin...

CAMPO USERNAME:    sysadmin'--
CAMPO CONTRASEÑA:  (cualquier cosa, por ejemplo: x)

→ Probadlo en http://localhost:5000/login
"""


# ══════════════════════════════════════════════════════════════
# PROGRAMA PRINCIPAL - no modificar
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    RUTA_CSV = "logs.csv"
    K        = 3

    print("=" * 55)
    print("  FASE 2: PERFIL DE VÍCTIMA")
    print("=" * 55)

    print("\n[1/4] Cargando datos...")
    df = cargar_datos(RUTA_CSV)
    if df is None:
        print("  ERROR: implementa cargar_datos()")
        exit(1)
    print(f"  {len(df)} registros cargados, {df.shape[1]} columnas")

    print("\n[2/4] Preparando features...")
    resultado = preparar_features(df)
    if resultado is None:
        print("  ERROR: implementa preparar_features()")
        exit(1)
    X_norm, columnas = resultado
    print(f"  Features: {columnas}")
    print(f"  Shape normalizado: {X_norm.shape}")

    print(f"\n[3/4] Aplicando K-Means (k={K})...")
    resultado = aplicar_kmeans(X_norm, K)
    if resultado is None:
        print("  ERROR: implementa aplicar_kmeans()")
        exit(1)
    etiquetas, modelo = resultado
    unique, counts = {}, {}
    for e in etiquetas:
        counts[e] = counts.get(e, 0) + 1
    for c, n in sorted(counts.items()):
        print(f"  Cluster {c}: {n} sesiones")

    print("\n[4/4] Analizando clusters...")
    df_final = analizar_clusters(df, etiquetas, columnas)
    if df_final is None:
        print("  ERROR: implementa analizar_clusters()")
        exit(1)

    print("\n" + "=" * 55)
    print("  PREGUNTA CLAVE:")
    print("  ¿Qué cluster tiene hora tardía, sesiones largas,")
    print("  pocas peticiones y muchos accesos privados?")
    print("  → Ese es el administrador.")
    print("=" * 55)
    print("\n  Ahora ve a http://localhost:5000/login")
    print("  y usa la SQL Injection para acceder como admin.")
    print("=" * 55)

    # Visualización opcional
    try:
        visualizar(df_final, columnas)
    except Exception:
        pass
