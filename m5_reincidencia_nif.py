"""
greentech_auditoria_laboral — Módulo 5
Reincidencia sistemática en convocatorias de empleo por el mismo NIF empresa
(patrón: empresa usa subvenciones como financiación estructural de plantilla,
no como ayuda puntual de inserción)

Autor: Yel Martínez — https://yel-martinez-portfolio.com
Licencia: GPL-2.0-or-later
ODS: 16, 8 | ESG: Governance G | GRI: 205-1, 201-4

Fuentes de entrada esperadas:
  - subvenciones.csv: NIF_empresa, nombre_empresa, convocatoria, organismo,
                      año, fecha_resolucion, importe, n_puestos,
                      tipo_contrato_subvencionado, NIF_trabajador_vinculado
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── Umbrales de detección ─────────────────────────────────────────────────────
UMBRAL_REINCIDENCIA_CONVOCATORIA = 2   # misma convocatoria más de N veces = alerta
UMBRAL_AÑOS_DEPENDENCIA = 3            # 3+ años consecutivos recibiendo subvenciones
UMBRAL_PCT_PLANTILLA_SUBV = 40         # >40% plantilla financiada con subvenciones = riesgo
UMBRAL_IMPORTE_ACUMULADO = 30000       # >30.000€ acumulados = magnitud relevante


def analizar_reincidencia_nif(
    df_subvenciones: pd.DataFrame,
    df_plantilla: pd.DataFrame = None
) -> dict:
    """
    Detecta empresas (NIF) que muestran dependencia estructural de
    subvenciones de empleo, identificando:
    1. Reincidencia en la misma convocatoria (mismo programa, varios años)
    2. Dependencia continua (subvenciones en 3+ años consecutivos)
    3. Alto porcentaje de plantilla financiada con fondos públicos
    4. Escalada del importe acumulado sin crecimiento real de plantilla

    Parámetros
    ----------
    df_subvenciones : DataFrame con historial de subvenciones concedidas
    df_plantilla : DataFrame opcional con plantilla actual por empresa
                   (para calcular % de puestos subvencionados)

    Retorna
    -------
    dict con alertas, ranking_empresas, resumen, puntuacion_riesgo
    """
    df = df_subvenciones.copy()
    df['fecha_resolucion'] = pd.to_datetime(
        df['fecha_resolucion'], dayfirst=True, errors='coerce'
    )
    if 'año' not in df.columns:
        df['año'] = df['fecha_resolucion'].dt.year

    alertas = []

    # ── Análisis por NIF empresa ───────────────────────────────────────────────
    for nif in df['NIF_empresa'].unique():
        subv_nif = df[df['NIF_empresa'] == nif].copy()
        nombre_empresa = subv_nif['nombre_empresa'].iloc[0] \
            if 'nombre_empresa' in subv_nif.columns else nif

        años_activos = sorted(subv_nif['año'].dropna().unique())
        importe_total = subv_nif['importe'].sum() if 'importe' in subv_nif.columns else 0
        n_solicitudes = len(subv_nif)
        n_puestos_total = subv_nif['n_puestos'].sum() \
            if 'n_puestos' in subv_nif.columns else None

        # Patrón 1: Reincidencia misma convocatoria
        reinc_conv = (
            subv_nif.groupby('convocatoria').size()
            .reset_index(name='n_veces')
        )
        reinc_critica = reinc_conv[
            reinc_conv['n_veces'] > UMBRAL_REINCIDENCIA_CONVOCATORIA
        ]

        # Patrón 2: Dependencia temporal (años consecutivos)
        if len(años_activos) >= 2:
            años_consec = _max_consecutivos(años_activos)
        else:
            años_consec = len(años_activos)

        dependencia_estructural = años_consec >= UMBRAL_AÑOS_DEPENDENCIA

        # Patrón 3: % de plantilla subvencionada
        pct_subvencionada = None
        if df_plantilla is not None and n_puestos_total is not None:
            plantilla_nif = df_plantilla[df_plantilla['NIF_empresa'] == nif]
            if not plantilla_nif.empty:
                total_empleados = len(plantilla_nif)
                pct_subvencionada = (n_puestos_total / total_empleados * 100
                                     if total_empleados > 0 else None)

        # Patrón 4: Importe acumulado elevado
        importe_alto = importe_total >= UMBRAL_IMPORTE_ACUMULADO

        # Construir alerta si hay señales suficientes
        n_señales = (
            int(len(reinc_critica) > 0) +
            int(dependencia_estructural) +
            int(pct_subvencionada is not None and
                pct_subvencionada > UMBRAL_PCT_PLANTILLA_SUBV) +
            int(importe_alto and n_solicitudes >= 3)
        )

        if n_señales >= 1:
            nivel = 'CRÍTICO' if n_señales >= 3 else ('ALTO' if n_señales == 2 else 'MEDIO')

            convs_reincidentes = ', '.join(
                f"'{r['convocatoria']}' ({int(r['n_veces'])}x)"
                for _, r in reinc_critica.iterrows()
            ) if not reinc_critica.empty else 'ninguna'

            alertas.append({
                'NIF_empresa': nif,
                'nombre_empresa': nombre_empresa,
                'n_solicitudes_total': n_solicitudes,
                'años_con_subvenciones': len(años_activos),
                'años_consecutivos_max': años_consec,
                'dependencia_estructural': dependencia_estructural,
                'importe_acumulado_eur': round(importe_total, 2),
                'pct_plantilla_subvencionada': round(pct_subvencionada, 1)
                if pct_subvencionada is not None else None,
                'convocatorias_reincidentes': convs_reincidentes,
                'n_señales_detectadas': n_señales,
                'nivel_alerta': nivel,
                'tipo_alerta': 'Dependencia estructural de subvenciones de empleo',
                'normativa': 'Ley 38/2003 · Convocatorias Labora/SEPE · GRI 205-1 · ODS 16',
                'descripcion': _construir_descripcion(
                    nombre_empresa, nif, n_solicitudes, años_activos,
                    años_consec, importe_total, convs_reincidentes,
                    pct_subvencionada, dependencia_estructural
                )
            })

    df_alertas = pd.DataFrame(alertas) if alertas else pd.DataFrame()

    if not df_alertas.empty and 'nivel_alerta' in df_alertas.columns:
        df_alertas = df_alertas.sort_values(
            ['n_señales_detectadas', 'importe_acumulado_eur'],
            ascending=[False, False]
        ).reset_index(drop=True)

    # Ranking por importe acumulado
    ranking = (
        df.groupby(['NIF_empresa', 'nombre_empresa'])
        .agg(
            n_solicitudes=('convocatoria', 'count'),
            importe_total=('importe', 'sum'),
            años_activos=('año', 'nunique'),
            organismos=('organismo', lambda x: ', '.join(x.dropna().unique()))
        )
        .reset_index()
        .sort_values('importe_total', ascending=False)
        .reset_index(drop=True)
    ) if 'nombre_empresa' in df.columns else pd.DataFrame()

    n_alertas = len(df_alertas)
    n_criticas = len(df_alertas[df_alertas['nivel_alerta'] == 'CRÍTICO']) \
        if not df_alertas.empty else 0
    importe_riesgo = df_alertas['importe_acumulado_eur'].sum() \
        if not df_alertas.empty else 0

    puntuacion = min(100, round(n_criticas * 25 + (n_alertas - n_criticas) * 12, 0))

    resumen = {
        'total_empresas_analizadas': df['NIF_empresa'].nunique(),
        'empresas_con_patron_reincidencia': n_alertas,
        'empresas_criticas': n_criticas,
        'importe_total_en_riesgo_eur': round(importe_riesgo, 2),
        'puntuacion_riesgo': puntuacion,
        'ods_afectados': ['ODS 16', 'ODS 8'],
        'gri': ['GRI 205-1', 'GRI 201-4'],
        'normativa': ['Ley 38/2003 Subvenciones', 'RD 887/2006',
                      'Convocatorias Labora EMCORP', 'LISOS art. 23',
                      'Plan de Control Tributario AEAT']
    }

    return {
        'alertas': df_alertas,
        'ranking_empresas': ranking,
        'resumen': resumen,
        'puntuacion_riesgo': puntuacion
    }


def _max_consecutivos(años: list) -> int:
    """Calcula el máximo de años consecutivos en una lista de años."""
    if not años:
        return 0
    años = sorted(set(int(a) for a in años))
    max_consec = consec = 1
    for i in range(1, len(años)):
        if años[i] == años[i-1] + 1:
            consec += 1
            max_consec = max(max_consec, consec)
        else:
            consec = 1
    return max_consec


def _construir_descripcion(nombre, nif, n_sol, años, años_consec,
                            importe, convs_reinc, pct_subv, dep_estruct) -> str:
    desc = (
        f"'{nombre}' ({nif}): {n_sol} solicitudes en {len(años)} años "
        f"({min(años) if años else '?'}–{max(años) if años else '?'}). "
        f"Importe acumulado: {importe:,.0f}€. "
    )
    if dep_estruct:
        desc += f"Dependencia estructural: {años_consec} años consecutivos con subvenciones. "
    if convs_reinc != 'ninguna':
        desc += f"Reincidencia en: {convs_reinc}. "
    if pct_subv is not None:
        desc += f"{pct_subv:.1f}% de la plantilla financiada con fondos públicos. "
    return desc.strip()


def generar_csv_ejemplo() -> pd.DataFrame:
    """Genera un DataFrame de ejemplo."""
    return pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'nombre_empresa': 'TechVerde S.L.',
         'convocatoria': 'Labora EMCORP', 'organismo': 'Labora',
         'año': 2020, 'fecha_resolucion': '2020-03-01',
         'importe': 12000, 'n_puestos': 2, 'tipo_contrato_subvencionado': 'Auxiliar'},
        {'NIF_empresa': 'B12345678', 'nombre_empresa': 'TechVerde S.L.',
         'convocatoria': 'Labora EMCORP', 'organismo': 'Labora',
         'año': 2021, 'fecha_resolucion': '2021-03-01',
         'importe': 12000, 'n_puestos': 2, 'tipo_contrato_subvencionado': 'Auxiliar'},
        {'NIF_empresa': 'B12345678', 'nombre_empresa': 'TechVerde S.L.',
         'convocatoria': 'Labora EMCORP', 'organismo': 'Labora',
         'año': 2022, 'fecha_resolucion': '2022-03-01',
         'importe': 12000, 'n_puestos': 2, 'tipo_contrato_subvencionado': 'Auxiliar'},
        {'NIF_empresa': 'B12345678', 'nombre_empresa': 'TechVerde S.L.',
         'convocatoria': 'SEPE Inserción', 'organismo': 'SEPE',
         'año': 2023, 'fecha_resolucion': '2023-05-01',
         'importe': 8500, 'n_puestos': 1, 'tipo_contrato_subvencionado': 'Auxiliar'},
        {'NIF_empresa': 'A87654321', 'nombre_empresa': 'EcoServicios CV S.L.',
         'convocatoria': 'Labora EMCORP', 'organismo': 'Labora',
         'año': 2022, 'fecha_resolucion': '2022-04-01',
         'importe': 15000, 'n_puestos': 3, 'tipo_contrato_subvencionado': 'Técnico'},
        {'NIF_empresa': 'A87654321', 'nombre_empresa': 'EcoServicios CV S.L.',
         'convocatoria': 'Labora EMCORP', 'organismo': 'Labora',
         'año': 2023, 'fecha_resolucion': '2023-04-01',
         'importe': 15000, 'n_puestos': 3, 'tipo_contrato_subvencionado': 'Técnico'},
        {'NIF_empresa': 'C11223344', 'nombre_empresa': 'Consultoría Verde S.C.',
         'convocatoria': 'SEPE Inserción', 'organismo': 'SEPE',
         'año': 2023, 'fecha_resolucion': '2023-06-01',
         'importe': 9000, 'n_puestos': 1, 'tipo_contrato_subvencionado': 'Indefinido'},
    ])
