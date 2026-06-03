"""
greentech_auditoria_laboral — Módulo 4
Detección de familiares del titular/administrador contratados
en coincidencia temporal con picos de subvención

Autor: Yel Martínez — https://yel-martinez-portfolio.com
Kit: https://github.com/yelmartinezseo/greentech-auditoria-laboral-python
Licencia: GPL-3.0-or-later
Atribución requerida: ver ATTRIBUTION.md
ODS: 16 | ESG: Governance G | GRI: 205-1, 2-23

Fuentes de entrada esperadas:
  - plantilla.csv: NIF_empresa, NIF_trabajador, nombre, apellidos,
                   fecha_alta, fecha_baja, categoria, salario_bruto
  - administradores.csv: NIF_empresa, NIF_administrador, nombre_administrador,
                         apellidos_administrador, cargo
  - subvenciones.csv: NIF_empresa, convocatoria, fecha_resolucion, importe

Nota: La detección de parentesco se basa en coincidencia de apellidos
(técnica usada por Inspección de Trabajo como señal de alerta inicial,
no como prueba). El usuario debe verificar manualmente los casos detectados.
"""

import pandas as pd
import numpy as np
import jellyfish  # similitud fonética de apellidos
import warnings
warnings.filterwarnings('ignore')

# ── Umbral de similitud de apellidos ──────────────────────────────────────────
# Jaro-Winkler: 0.0 = completamente diferente, 1.0 = idéntico
# 0.88 captura variantes como García/Garcia, López/Lopez, apellidos compuestos
UMBRAL_SIMILITUD_APELLIDO = 0.88

# Ventana temporal: días desde la resolución de subvención
# en los que una contratación se considera sospechosa
VENTANA_CONTRATACION_DIAS = 90


def _similitud_apellido(a1: str, a2: str) -> float:
    """Calcula similitud Jaro-Winkler entre dos apellidos."""
    if not isinstance(a1, str) or not isinstance(a2, str):
        return 0.0
    a1 = a1.lower().strip()
    a2 = a2.lower().strip()
    if a1 == '' or a2 == '':
        return 0.0
    return jellyfish.jaro_winkler_similarity(a1, a2)


def _extraer_apellidos(nombre_completo: str) -> list:
    """
    Extrae apellidos asumiendo formato 'Nombre Apellido1 Apellido2'.
    Retorna lista de apellidos candidatos.
    """
    if not isinstance(nombre_completo, str):
        return []
    partes = nombre_completo.strip().split()
    if len(partes) >= 3:
        return partes[1:]   # descarta el primer nombre
    elif len(partes) == 2:
        return [partes[1]]
    return []


def _coincide_apellido(apellidos_trabajador: list, apellidos_admin: list,
                       umbral: float = UMBRAL_SIMILITUD_APELLIDO) -> tuple:
    """
    Comprueba si algún apellido del trabajador coincide fonéticamente
    con algún apellido del administrador.
    Retorna (bool_coincide, similitud_maxima, apellido_admin, apellido_trabajador)
    """
    max_sim = 0.0
    match_admin = ''
    match_trab = ''
    for ap_t in apellidos_trabajador:
        for ap_a in apellidos_admin:
            sim = _similitud_apellido(ap_t, ap_a)
            if sim > max_sim:
                max_sim = sim
                match_admin = ap_a
                match_trab = ap_t
    return max_sim >= umbral, round(max_sim, 3), match_admin, match_trab


def analizar_familiares_subvencion(
    df_plantilla: pd.DataFrame,
    df_administradores: pd.DataFrame,
    df_subvenciones: pd.DataFrame,
    ventana_dias: int = VENTANA_CONTRATACION_DIAS,
    umbral_similitud: float = UMBRAL_SIMILITUD_APELLIDO
) -> dict:
    """
    Detecta trabajadores cuyos apellidos coinciden fonéticamente con los
    del administrador/titular de la empresa, contratados en los 90 días
    siguientes a la resolución de una subvención.

    ⚠️ IMPORTANTE: Esta detección es una señal de alerta, NO una prueba
    de parentesco. Requiere verificación manual y contraste con el
    Registro Mercantil (cargo) y Registro Civil (parentesco real).

    Parámetros
    ----------
    df_plantilla : DataFrame con plantilla de trabajadores
    df_administradores : DataFrame con administradores/titulares por NIF empresa
    df_subvenciones : DataFrame con subvenciones concedidas
    ventana_dias : días desde resolución para considerar contratación sospechosa
    umbral_similitud : similitud Jaro-Winkler mínima para marcar posible parentesco

    Retorna
    -------
    dict con alertas, resumen, puntuacion_riesgo
    """
    df_p = df_plantilla.copy()
    df_a = df_administradores.copy()
    df_s = df_subvenciones.copy()

    # Parsear fechas
    df_p['fecha_alta'] = pd.to_datetime(df_p['fecha_alta'], dayfirst=True, errors='coerce')
    df_s['fecha_resolucion'] = pd.to_datetime(
        df_s['fecha_resolucion'], dayfirst=True, errors='coerce'
    )

    # Extraer apellidos de trabajadores
    nombre_col = 'nombre' if 'nombre' in df_p.columns else df_p.columns[2]
    df_p['apellidos_trab'] = df_p[nombre_col].apply(_extraer_apellidos)

    # Extraer apellidos de administradores
    df_a['apellidos_admin'] = df_a.apply(
        lambda r: _extraer_apellidos(
            str(r.get('apellidos_administrador', '')) or
            str(r.get('nombre_administrador', ''))
        ), axis=1
    )

    alertas = []

    for nif_empresa in df_s['NIF_empresa'].unique():
        admins = df_a[df_a['NIF_empresa'] == nif_empresa]
        subvs = df_s[df_s['NIF_empresa'] == nif_empresa]
        trabajadores = df_p[df_p['NIF_empresa'] == nif_empresa]

        if admins.empty or trabajadores.empty or subvs.empty:
            continue

        # Para cada subvención, ver quién fue contratado en la ventana temporal
        for _, subv in subvs.iterrows():
            fecha_res = subv['fecha_resolucion']
            if pd.isna(fecha_res):
                continue

            ventana_fin = fecha_res + pd.Timedelta(days=ventana_dias)
            contratados_ventana = trabajadores[
                (trabajadores['fecha_alta'] >= fecha_res) &
                (trabajadores['fecha_alta'] <= ventana_fin)
            ]

            if contratados_ventana.empty:
                continue

            # Cruzar apellidos con administradores
            for _, trab in contratados_ventana.iterrows():
                for _, admin in admins.iterrows():
                    aps_trab = trab['apellidos_trab']
                    aps_admin = admin['apellidos_admin']

                    if not aps_trab or not aps_admin:
                        continue

                    # No alertar si el NIF es el mismo (el propio administrador autónomo)
                    if (str(trab.get('NIF_trabajador', '')) ==
                            str(admin.get('NIF_administrador', ''))):
                        continue

                    coincide, similitud, ap_admin, ap_trab = _coincide_apellido(
                        aps_trab, aps_admin, umbral_similitud
                    )

                    if coincide:
                        dias_desde_subv = (trab['fecha_alta'] - fecha_res).days
                        alertas.append({
                            'NIF_empresa': nif_empresa,
                            'NIF_trabajador': trab.get('NIF_trabajador', ''),
                            'nombre_trabajador': trab.get(nombre_col, ''),
                            'fecha_alta': trab['fecha_alta'],
                            'categoria': trab.get('categoria', ''),
                            'salario_bruto': trab.get('salario_bruto', None),
                            'nombre_administrador': admin.get('nombre_administrador', ''),
                            'cargo_administrador': admin.get('cargo', ''),
                            'convocatoria': subv.get('convocatoria', ''),
                            'organismo': subv.get('organismo', ''),
                            'importe_subvencion': subv.get('importe', 0),
                            'fecha_resolucion': fecha_res.date(),
                            'dias_desde_resolucion': dias_desde_subv,
                            'apellido_coincidente_trabajador': ap_trab,
                            'apellido_coincidente_administrador': ap_admin,
                            'similitud_apellido': similitud,
                            'nivel_alerta': 'CRÍTICO' if dias_desde_subv <= 30 else 'ALTO',
                            'tipo_alerta': 'Posible familiar contratado en pico de subvención',
                            'normativa': 'Ley 38/2003 art. 31 · GRI 205-1 · ODS 16',
                            'descripcion': (
                                f"'{trab.get(nombre_col,'')}' contratado {dias_desde_subv} días "
                                f"tras resolución de '{subv.get('convocatoria','')}' "
                                f"({subv.get('importe',0):,.0f}€). "
                                f"Coincidencia de apellido '{ap_trab}' con administrador "
                                f"'{admin.get('nombre_administrador','')}' (similitud: {similitud:.2f}). "
                                f"⚠️ Requiere verificación manual."
                            ),
                            'advertencia': (
                                'SEÑAL DE ALERTA INICIAL. No es prueba de parentesco. '
                                'Verificar en Registro Civil y Registro Mercantil.'
                            )
                        })

    df_alertas = pd.DataFrame(alertas) if alertas else pd.DataFrame()

    total_trabajadores = len(df_p)
    n_alertas = len(df_alertas)
    n_criticas = len(df_alertas[df_alertas['nivel_alerta'] == 'CRÍTICO']) \
        if not df_alertas.empty else 0
    importe_riesgo = df_alertas['importe_subvencion'].sum() \
        if not df_alertas.empty and 'importe_subvencion' in df_alertas.columns else 0

    puntuacion = min(100, round(n_criticas * 35 + (n_alertas - n_criticas) * 15, 0))

    resumen = {
        'total_trabajadores_analizados': total_trabajadores,
        'alertas_posible_familiar': n_alertas,
        'alertas_criticas_30dias': n_criticas,
        'importe_subvenciones_en_riesgo_eur': round(importe_riesgo, 2),
        'empresas_alertadas': df_alertas['NIF_empresa'].nunique()
        if not df_alertas.empty else 0,
        'nota_metodologica': (
            'Detección basada en similitud fonética de apellidos (Jaro-Winkler >= '
            f'{umbral_similitud}). Señal inicial de Inspección de Trabajo. '
            'Requiere verificación documental para confirmar parentesco.'
        ),
        'puntuacion_riesgo': puntuacion,
        'ods_afectados': ['ODS 16'],
        'gri': ['GRI 205-1', 'GRI 2-23'],
        'normativa': ['Ley 38/2003 art. 31', 'RD 887/2006', 'LISOS art. 23']
    }

    return {
        'alertas': df_alertas,
        'resumen': resumen,
        'puntuacion_riesgo': puntuacion
    }


def generar_csvs_ejemplo() -> tuple:
    """Genera DataFrames de ejemplo."""
    plantilla = pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '11111111A',
         'nombre': 'Clara García Martínez', 'fecha_alta': '2022-03-20',
         'fecha_baja': None, 'categoria': 'Auxiliar Administrativo',
         'salario_bruto': 16800},
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '22222222B',
         'nombre': 'Luis Sanz Pérez', 'fecha_alta': '2021-06-01',
         'fecha_baja': None, 'categoria': 'Técnico', 'salario_bruto': 22000},
        {'NIF_empresa': 'A87654321', 'NIF_trabajador': '33333333C',
         'nombre': 'Marta López García', 'fecha_alta': '2023-01-10',
         'fecha_baja': None, 'categoria': 'Administrativo', 'salario_bruto': 19000},
    ])
    administradores = pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'NIF_administrador': '99999999Z',
         'nombre_administrador': 'José García Ruiz',
         'apellidos_administrador': 'García Ruiz', 'cargo': 'Administrador único'},
        {'NIF_empresa': 'A87654321', 'NIF_administrador': '88888888Y',
         'nombre_administrador': 'Carmen López Vidal',
         'apellidos_administrador': 'López Vidal', 'cargo': 'Administradora solidaria'},
    ])
    subvenciones = pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'convocatoria': 'Labora EMCORP 2022',
         'organismo': 'Labora', 'fecha_resolucion': '2022-03-01', 'importe': 12000},
        {'NIF_empresa': 'A87654321', 'convocatoria': 'SEPE Inserción 2022',
         'organismo': 'SEPE', 'fecha_resolucion': '2022-12-20', 'importe': 8500},
    ])
    return plantilla, administradores, subvenciones
