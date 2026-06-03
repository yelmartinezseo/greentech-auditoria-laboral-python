"""
greentech_auditoria_laboral — Módulo 1
Detección de concentración de categoría profesional inferior a funciones reales
(patrón: auxiliar→técnico, administrativo→gestor, etc.)

Autor: Yel Martínez — https://yel-martinez-portfolio.com
Kit: https://github.com/yelmartinezseo/greentech-auditoria-laboral-python
Licencia: GPL-3.0-or-later
Atribución requerida: ver ATTRIBUTION.md
ODS: 8, 10 | ESG: Social S | GRI: 405-2, 401-1

Fuentes de entrada esperadas:
  - plantilla.csv: NIF_empresa, NIF_trabajador, nombre, categoria_contrato,
                   salario_bruto, fecha_alta, departamento, funciones_declaradas
  - convenio.csv:  categoria, salario_minimo_convenio, grupo_profesional
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── Mapa de equivalencias categoría → grupo profesional real esperado ──────────
# Basado en clasificación del ET art. 22 y convenios colectivos sectoriales.
# El usuario puede sobreescribir este mapa con su propio convenio.
GRUPO_ESPERADO = {
    # Grupo 1 — Dirección / Titulados superiores
    'director': 1, 'gerente': 1, 'jefe de area': 1, 'responsable': 1,
    'titulado superior': 1, 'ingeniero': 1, 'licenciado': 1,
    # Grupo 2 — Mandos intermedios / Titulados medios
    'jefe de seccion': 2, 'jefe de equipo': 2, 'tecnico superior': 2,
    'coordinador': 2, 'supervisor': 2, 'graduado': 2,
    # Grupo 3 — Técnicos / Especialistas
    'tecnico': 3, 'especialista': 3, 'programador': 3, 'analista': 3,
    'gestor': 3, 'oficial': 3,
    # Grupo 4 — Empleados administrativos
    'administrativo': 4, 'contable': 4, 'secretario': 4, 'recepcionista': 4,
    # Grupo 5 — Auxiliares / Operativos
    'auxiliar administrativo': 5, 'auxiliar': 5, 'ayudante': 5,
    'operario': 5, 'peón': 5, 'mozo': 5,
}

# Palabras clave en funciones declaradas que sugieren grupo real superior
KEYWORDS_GRUPO = {
    1: ['estrategia', 'dirección', 'presupuesto', 'p&l', 'consejo', 'firma autorizada',
        'representación legal', 'liderazgo ejecutivo'],
    2: ['coordinación de equipo', 'supervisión', 'planificación', 'gestión de proyecto',
        'reporting a dirección', 'kpis', 'objetivos del área'],
    3: ['análisis de datos', 'programación', 'desarrollo', 'auditoría', 'diagnóstico',
        'implementación de sistemas', 'python', 'sql', 'erp', 'crm', 'gestión fiscal',
        'contabilidad analítica', 'nóminas complejas'],
    4: ['atención al cliente', 'facturación', 'pedidos', 'agenda directiva',
        'gestión documental', 'contabilidad básica'],
    5: ['archivo', 'fotocopias', 'recepción de llamadas', 'limpieza', 'almacén'],
}


def _normalizar(texto: str) -> str:
    """Normaliza texto a minúsculas sin tildes para comparación."""
    if not isinstance(texto, str):
        return ''
    reemplazos = str.maketrans('áàäâãéèëêíìïîóòöôõúùüûñç',
                                'aaaaaeeeeiiiiooooouuuunc')
    return texto.lower().strip().translate(reemplazos)


def _grupo_desde_categoria(categoria: str) -> int:
    """Infiere grupo profesional desde la categoría contractual."""
    cat = _normalizar(categoria)
    for key, grupo in GRUPO_ESPERADO.items():
        if key in cat:
            return grupo
    return 4  # default: empleado administrativo si no se reconoce


def _grupo_desde_funciones(funciones: str) -> int:
    """Infiere grupo real esperado desde las funciones declaradas."""
    if not isinstance(funciones, str) or funciones.strip() == '':
        return None
    func = _normalizar(funciones)
    for grupo in sorted(KEYWORDS_GRUPO.keys()):
        for kw in KEYWORDS_GRUPO[grupo]:
            if _normalizar(kw) in func:
                return grupo
    return None


def analizar_categoria_inferior(
    df_plantilla: pd.DataFrame,
    umbral_salario_pct: float = 0.85,
    df_convenio: pd.DataFrame = None
) -> dict:
    """
    Detecta trabajadores cuya categoría contractual es inferior al grupo
    profesional que sugieren sus funciones reales o su salario.

    Parámetros
    ----------
    df_plantilla : DataFrame con columnas mínimas:
        NIF_trabajador, nombre, categoria_contrato, salario_bruto,
        departamento, funciones_declaradas (opcional)
    umbral_salario_pct : float
        Si el salario es < umbral_salario_pct * salario_minimo_del_grupo_real,
        se marca como alerta. Default 0.85 (15% por debajo del mínimo).
    df_convenio : DataFrame con salarios mínimos por grupo (opcional).

    Retorna
    -------
    dict con:
        - alertas: DataFrame con casos sospechosos
        - resumen: dict con métricas clave
        - puntuacion_riesgo: float 0-100
    """
    df = df_plantilla.copy()

    # Inferir grupo desde categoría
    df['grupo_contrato'] = df['categoria_contrato'].apply(_grupo_desde_categoria)

    # Inferir grupo real desde funciones (si disponible)
    if 'funciones_declaradas' in df.columns:
        df['grupo_funciones'] = df['funciones_declaradas'].apply(_grupo_desde_funciones)
    else:
        df['grupo_funciones'] = None

    # Detectar brecha: categoría contrato > grupo funciones (categoría más baja de lo que hace)
    df['brecha_categoria'] = df.apply(
        lambda r: (r['grupo_contrato'] > r['grupo_funciones'])
        if pd.notna(r['grupo_funciones']) else False,
        axis=1
    )

    # Detectar concentración anómala en grupo 5 (auxiliares)
    total = len(df)
    aux_count = (df['grupo_contrato'] == 5).sum()
    pct_aux = aux_count / total * 100 if total > 0 else 0

    # Alerta por salario inferior al mínimo del grupo que ejerce
    alertas_salario = pd.DataFrame()
    if df_convenio is not None and 'salario_bruto' in df.columns:
        df_conv = df_convenio.set_index('grupo_profesional')['salario_minimo_anual']
        df['salario_minimo_grupo_real'] = df['grupo_funciones'].map(df_conv)
        df['alerta_salario'] = df.apply(
            lambda r: (
                pd.notna(r['salario_minimo_grupo_real']) and
                pd.notna(r['salario_bruto']) and
                r['salario_bruto'] < r['salario_minimo_grupo_real'] * umbral_salario_pct
            ),
            axis=1
        )
        alertas_salario = df[df['alerta_salario']]

    # Consolidar alertas
    alertas = df[df['brecha_categoria']].copy()
    alertas['tipo_alerta'] = 'Categoría inferior a funciones reales'
    alertas['normativa'] = 'ET art. 22 · GRI 405-2 · ODS 8/10'
    alertas['descripcion'] = alertas.apply(
        lambda r: (
            f"Contratado como Grupo {r['grupo_contrato']} "
            f"({r['categoria_contrato']}) pero funciones sugieren Grupo {int(r['grupo_funciones'])}"
        ),
        axis=1
    )

    cols_output = ['NIF_trabajador', 'nombre', 'categoria_contrato',
                   'grupo_contrato', 'grupo_funciones', 'departamento',
                   'tipo_alerta', 'descripcion', 'normativa']
    cols_disponibles = [c for c in cols_output if c in alertas.columns]
    alertas = alertas[cols_disponibles]

    # Puntuación de riesgo
    pct_brecha = len(alertas) / total * 100 if total > 0 else 0
    puntuacion = min(100, round(
        (pct_brecha * 0.6) + (max(0, pct_aux - 20) * 0.4), 1
    ))

    resumen = {
        'total_trabajadores': total,
        'alertas_categoria_inferior': len(alertas),
        'pct_alertas': round(pct_brecha, 1),
        'pct_auxiliares_grupo5': round(pct_aux, 1),
        'alertas_salario_por_debajo_convenio': len(alertas_salario),
        'puntuacion_riesgo': puntuacion,
        'ods_afectados': ['ODS 8', 'ODS 10'],
        'gri': ['GRI 405-2', 'GRI 401-1'],
        'normativa': ['ET art. 22', 'RD 1 Estatuto Trabajadores', 'LISOS art. 8']
    }

    return {'alertas': alertas, 'resumen': resumen, 'puntuacion_riesgo': puntuacion}


def generar_csv_plantilla_ejemplo() -> pd.DataFrame:
    """Genera un CSV de ejemplo con la estructura esperada."""
    return pd.DataFrame([
        {'NIF_trabajador': '12345678A', 'nombre': 'Ana García',
         'categoria_contrato': 'Auxiliar Administrativo', 'salario_bruto': 16800,
         'departamento': 'TI', 'fecha_alta': '2023-01-15',
         'funciones_declaradas': 'Desarrollo Python, análisis de datos, implementación de sistemas ERP'},
        {'NIF_trabajador': '87654321B', 'nombre': 'Luis Martín',
         'categoria_contrato': 'Auxiliar Administrativo', 'salario_bruto': 16200,
         'departamento': 'Finanzas', 'fecha_alta': '2023-03-01',
         'funciones_declaradas': 'Contabilidad analítica, reporting a dirección, gestión fiscal'},
        {'NIF_trabajador': '11223344C', 'nombre': 'Marta Sanz',
         'categoria_contrato': 'Técnico', 'salario_bruto': 24000,
         'departamento': 'Administración', 'fecha_alta': '2022-06-01',
         'funciones_declaradas': 'Archivo, recepción de llamadas, fotocopias'},
        {'NIF_trabajador': '55667788D', 'nombre': 'Pedro López',
         'categoria_contrato': 'Administrativo', 'salario_bruto': 19500,
         'departamento': 'RRHH', 'fecha_alta': '2021-09-01',
         'funciones_declaradas': 'Coordinación de equipo, supervisión de nóminas, reporting a dirección'},
    ])
