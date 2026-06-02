"""
greentech_auditoria_laboral — Módulo 2
Cruce fechas alta/baja Seguridad Social vs calendario de subvenciones
(patrón Labora/SEPE: extinción sistemática justo al vencer obligatoriedad)

Autor: Yel Martínez — https://yel-martinez-portfolio.com
Licencia: GPL-2.0-or-later
ODS: 16 | ESG: Governance G | GRI: 205-1, 201-4

Fuentes de entrada esperadas:
  - contratos_ss.csv: NIF_empresa, NIF_trabajador, nombre, fecha_alta,
                      fecha_baja, causa_baja, categoria, salario_bruto
  - subvenciones.csv: NIF_empresa, convocatoria, organismo (Labora/SEPE/SAE...),
                      fecha_resolucion, importe, meses_obligatoriedad,
                      NIF_trabajador_vinculado (si disponible)
"""

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings('ignore')

# ── Constantes de detección ────────────────────────────────────────────────────
# Ventana de días antes/después del vencimiento de obligatoriedad
# en la que una baja se considera sospechosa
VENTANA_SOSPECHA_DIAS = 45

# Causas de baja que pueden enmascarar un despido encubierto
CAUSAS_SOSPECHOSAS = [
    'baja voluntaria', 'mutuo acuerdo', 'fin de contrato',
    'no superación periodo de prueba', 'dimisión'
]


def _dias_hasta_vencimiento(fecha_baja, fecha_inicio_obligacion, meses_oblig):
    """Calcula días entre la baja y el vencimiento de obligatoriedad."""
    try:
        vencimiento = fecha_inicio_obligacion + relativedelta(months=int(meses_oblig))
        return (pd.Timestamp(fecha_baja) - pd.Timestamp(vencimiento)).days
    except Exception:
        return None


def analizar_cruce_ss_subvenciones(
    df_contratos: pd.DataFrame,
    df_subvenciones: pd.DataFrame,
    ventana_dias: int = VENTANA_SOSPECHA_DIAS
) -> dict:
    """
    Detecta bajas en Seguridad Social que coinciden sospechosamente
    con el fin del período de obligatoriedad de mantenimiento del empleo
    vinculado a subvenciones públicas.

    Parámetros
    ----------
    df_contratos : DataFrame
        Alta/baja SS con columnas: NIF_empresa, NIF_trabajador, nombre,
        fecha_alta, fecha_baja, causa_baja, categoria, salario_bruto
    df_subvenciones : DataFrame
        Subvenciones concedidas con: NIF_empresa, convocatoria, organismo,
        fecha_resolucion, importe, meses_obligatoriedad, NIF_trabajador_vinculado
    ventana_dias : int
        Días de margen para considerar una baja como sospechosa respecto
        al vencimiento de obligatoriedad. Default: 45 días.

    Retorna
    -------
    dict con alertas, resumen y puntuacion_riesgo
    """
    df_c = df_contratos.copy()
    df_s = df_subvenciones.copy()

    # Parsear fechas
    for col in ['fecha_alta', 'fecha_baja']:
        if col in df_c.columns:
            df_c[col] = pd.to_datetime(df_c[col], dayfirst=True, errors='coerce')
    df_s['fecha_resolucion'] = pd.to_datetime(
        df_s['fecha_resolucion'], dayfirst=True, errors='coerce'
    )

    # Solo trabajadores con baja registrada
    df_bajas = df_c[df_c['fecha_baja'].notna()].copy()

    alertas = []

    # ── Patrón 1: NIF empresa con múltiples subvenciones + bajas cerca del vencimiento
    for nif_empresa in df_s['NIF_empresa'].unique():
        subv_empresa = df_s[df_s['NIF_empresa'] == nif_empresa]
        bajas_empresa = df_bajas[df_bajas['NIF_empresa'] == nif_empresa]

        if bajas_empresa.empty:
            continue

        for _, subv in subv_empresa.iterrows():
            meses = subv.get('meses_obligatoriedad', 12)
            fecha_inicio = subv['fecha_resolucion']
            vencimiento = fecha_inicio + relativedelta(months=int(meses))

            # Bajas en ventana sospechosa alrededor del vencimiento
            ventana_inicio = vencimiento - pd.Timedelta(days=ventana_dias)
            ventana_fin = vencimiento + pd.Timedelta(days=ventana_dias)

            bajas_ventana = bajas_empresa[
                (bajas_empresa['fecha_baja'] >= ventana_inicio) &
                (bajas_empresa['fecha_baja'] <= ventana_fin)
            ].copy()

            if bajas_ventana.empty:
                continue

            # Si hay vinculación directa trabajador-subvención, priorizar
            nif_vinc = subv.get('NIF_trabajador_vinculado', None)
            if pd.notna(nif_vinc) and nif_vinc != '':
                bajas_ventana = bajas_ventana[
                    bajas_ventana['NIF_trabajador'] == nif_vinc
                ] if not bajas_ventana[bajas_ventana['NIF_trabajador'] == nif_vinc].empty \
                    else bajas_ventana

            for _, baja in bajas_ventana.iterrows():
                dias_diff = (baja['fecha_baja'] - vencimiento).days
                causa = str(baja.get('causa_baja', '')).lower()
                es_causa_sospechosa = any(c in causa for c in CAUSAS_SOSPECHOSAS)

                alertas.append({
                    'NIF_empresa': nif_empresa,
                    'NIF_trabajador': baja.get('NIF_trabajador', ''),
                    'nombre': baja.get('nombre', ''),
                    'fecha_alta': baja.get('fecha_alta'),
                    'fecha_baja': baja['fecha_baja'],
                    'causa_baja': baja.get('causa_baja', ''),
                    'convocatoria': subv.get('convocatoria', ''),
                    'organismo': subv.get('organismo', ''),
                    'importe_subvencion': subv.get('importe', 0),
                    'meses_obligatoriedad': meses,
                    'vencimiento_obligacion': vencimiento.date(),
                    'dias_hasta_vencimiento': dias_diff,
                    'causa_sospechosa': es_causa_sospechosa,
                    'nivel_alerta': 'CRÍTICO' if abs(dias_diff) <= 15 else 'ALTO',
                    'tipo_alerta': 'Baja en ventana de obligatoriedad',
                    'normativa': 'Ley 38/2003 General de Subvenciones · GRI 205-1 · ODS 16',
                    'descripcion': (
                        f"Baja {dias_diff:+d} días respecto al vencimiento de obligatoriedad "
                        f"de '{subv.get('convocatoria', '')}' ({organismo_str(subv)}). "
                        f"Subvención: {subv.get('importe', 0):,.0f}€. "
                        f"{'⚠️ Causa sospechosa: ' + baja.get('causa_baja','') if es_causa_sospechosa else ''}"
                    )
                })

    # ── Patrón 2: reincidencia NIF empresa en misma convocatoria ─────────────────
    reincidencia = (
        df_s.groupby(['NIF_empresa', 'convocatoria'])
        .size()
        .reset_index(name='n_solicitudes')
    )
    reincidentes = reincidencia[reincidencia['n_solicitudes'] > 1]

    df_alertas = pd.DataFrame(alertas) if alertas else pd.DataFrame()

    # Métricas
    total_bajas = len(df_bajas)
    n_alertas = len(df_alertas)
    n_empresas_alertadas = df_alertas['NIF_empresa'].nunique() if not df_alertas.empty else 0
    n_criticas = len(df_alertas[df_alertas['nivel_alerta'] == 'CRÍTICO']) \
        if not df_alertas.empty and 'nivel_alerta' in df_alertas.columns else 0

    importe_riesgo = df_alertas['importe_subvencion'].sum() \
        if not df_alertas.empty and 'importe_subvencion' in df_alertas.columns else 0

    puntuacion = min(100, round(
        (n_criticas * 25) + ((n_alertas - n_criticas) * 10) +
        (len(reincidentes) * 8), 0
    ))

    resumen = {
        'total_bajas_analizadas': total_bajas,
        'alertas_en_ventana_obligatoriedad': n_alertas,
        'alertas_criticas_15dias': n_criticas,
        'empresas_con_patron_sospechoso': n_empresas_alertadas,
        'empresas_reincidentes_misma_convocatoria': len(reincidentes),
        'importe_subvenciones_en_riesgo_eur': round(importe_riesgo, 2),
        'puntuacion_riesgo': puntuacion,
        'ods_afectados': ['ODS 16', 'ODS 8'],
        'gri': ['GRI 205-1', 'GRI 201-4'],
        'normativa': ['Ley 38/2003 Subvenciones', 'RD 887/2006 Reglamento Subvenciones',
                      'Convocatorias Labora', 'LISOS art. 23']
    }

    return {
        'alertas': df_alertas,
        'reincidentes': reincidentes,
        'resumen': resumen,
        'puntuacion_riesgo': puntuacion
    }


def organismo_str(subv_row) -> str:
    return str(subv_row.get('organismo', 'organismo desconocido'))


def generar_csvs_ejemplo() -> tuple:
    """Genera DataFrames de ejemplo para contratos y subvenciones."""
    contratos = pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '11111111A',
         'nombre': 'Sara Pérez', 'fecha_alta': '2022-03-01',
         'fecha_baja': '2023-03-10', 'causa_baja': 'Mutuo acuerdo',
         'categoria': 'Auxiliar Administrativo', 'salario_bruto': 16800},
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '22222222B',
         'nombre': 'Jordi Vila', 'fecha_alta': '2022-03-01',
         'fecha_baja': '2023-02-28', 'causa_baja': 'Fin de contrato',
         'categoria': 'Auxiliar Administrativo', 'salario_bruto': 16500},
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '33333333C',
         'nombre': 'Elena Ruiz', 'fecha_alta': '2023-04-01',
         'fecha_baja': None, 'causa_baja': None,
         'categoria': 'Técnico', 'salario_bruto': 22000},
        {'NIF_empresa': 'A87654321', 'NIF_trabajador': '44444444D',
         'nombre': 'Marcos Torres', 'fecha_alta': '2021-06-01',
         'fecha_baja': '2022-06-05', 'causa_baja': 'Baja voluntaria',
         'categoria': 'Auxiliar Administrativo', 'salario_bruto': 17200},
    ])
    subvenciones = pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'convocatoria': 'Labora EMCORP 2022',
         'organismo': 'Labora', 'fecha_resolucion': '2022-03-01',
         'importe': 12000, 'meses_obligatoriedad': 12,
         'NIF_trabajador_vinculado': '11111111A'},
        {'NIF_empresa': 'B12345678', 'convocatoria': 'Labora EMCORP 2022',
         'organismo': 'Labora', 'fecha_resolucion': '2022-03-01',
         'importe': 12000, 'meses_obligatoriedad': 12,
         'NIF_trabajador_vinculado': '22222222B'},
        {'NIF_empresa': 'B12345678', 'convocatoria': 'Labora EMCORP 2023',
         'organismo': 'Labora', 'fecha_resolucion': '2023-04-01',
         'importe': 12000, 'meses_obligatoriedad': 12,
         'NIF_trabajador_vinculado': ''},
        {'NIF_empresa': 'A87654321', 'convocatoria': 'SEPE Inserción 2021',
         'organismo': 'SEPE', 'fecha_resolucion': '2021-06-01',
         'importe': 8500, 'meses_obligatoriedad': 12,
         'NIF_trabajador_vinculado': '44444444D'},
    ])
    return contratos, subvenciones
