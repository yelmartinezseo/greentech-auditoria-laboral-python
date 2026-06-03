"""
greentech_auditoria_laboral — Módulo 3
Detección de contratos indefinidos rescindidos antes del plazo de obligatoriedad
(simulación de indefinido para acceder a bonificación, rescisión antes de plazo)

Autor: Yel Martínez — https://yel-martinez-portfolio.com
Kit: https://github.com/yelmartinezseo/greentech-auditoria-laboral-python
Licencia: GPL-3.0-or-later
Atribución requerida: ver ATTRIBUTION.md
ODS: 8, 16 | ESG: Social S, Governance G | GRI: 401-1, 205-1

Fuentes de entrada esperadas:
  - contratos_ss.csv: NIF_empresa, NIF_trabajador, nombre, tipo_contrato,
                      fecha_alta, fecha_baja, causa_baja, bonificacion_aplicada,
                      importe_bonificacion_mensual
"""

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings('ignore')

# ── Plazos mínimos de mantenimiento por tipo de bonificación ──────────────────
# Fuente: RD-ley 1/2015, Ley 43/2006, convocatorias Labora/SEPE
# El usuario puede ampliar este diccionario con los plazos de su convocatoria.
PLAZOS_BONIFICACION = {
    'general': 36,                          # indefinido ordinario: 3 años mínimo
    'jovenes_garantia': 36,                 # Garantía Juvenil: 3 años
    'mayores_52': 36,
    'discapacidad': 48,                     # contratos discapacidad: 4 años
    'labora_emcorp': 12,                    # EMCORP: 1 año
    'sepe_insercion': 12,
    'indefinido_bonificado': 36,
    'conversion_temporal': 24,
    'primer_empleo_joven': 18,
}

TIPOS_INDEFINIDO = [
    'indefinido', 'indefinido ordinario', 'fijo discontinuo',
    'indefinido bonificado', 'conversión a indefinido',
    'contrato de trabajo indefinido'
]

CAUSAS_SOSPECHOSAS_RESCISION = [
    'mutuo acuerdo', 'baja voluntaria', 'dimisión',
    'no superación periodo de prueba', 'fin relacion laboral',
    'acuerdo extinción'
]


def _meses_duracion(fecha_alta, fecha_baja) -> float:
    """Calcula meses entre alta y baja."""
    try:
        delta = relativedelta(
            pd.Timestamp(fecha_baja),
            pd.Timestamp(fecha_alta)
        )
        return delta.years * 12 + delta.months + delta.days / 30
    except Exception:
        return None


def _plazo_requerido(bonificacion: str) -> int:
    """Devuelve meses mínimos de mantenimiento según tipo de bonificación."""
    if not isinstance(bonificacion, str):
        return PLAZOS_BONIFICACION['general']
    bon = bonificacion.lower().strip()
    for key, meses in PLAZOS_BONIFICACION.items():
        if key in bon:
            return meses
    return PLAZOS_BONIFICACION['general']


def analizar_indefinidos_rescindidos(
    df_contratos: pd.DataFrame
) -> dict:
    """
    Detecta contratos indefinidos (especialmente bonificados) que fueron
    rescindidos antes del plazo mínimo de mantenimiento obligatorio,
    lo que puede implicar reintegro de bonificaciones y sanción.

    Parámetros
    ----------
    df_contratos : DataFrame con columnas:
        NIF_empresa, NIF_trabajador, nombre, tipo_contrato,
        fecha_alta, fecha_baja, causa_baja,
        bonificacion_aplicada (bool o str), importe_bonificacion_mensual (opcional)

    Retorna
    -------
    dict con alertas, resumen, puntuacion_riesgo
    """
    df = df_contratos.copy()

    # Parsear fechas
    for col in ['fecha_alta', 'fecha_baja']:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

    # Solo contratos indefinidos con baja registrada
    df['es_indefinido'] = df['tipo_contrato'].apply(
        lambda t: any(ti in str(t).lower() for ti in TIPOS_INDEFINIDO)
        if pd.notna(t) else False
    )
    df_indefinidos_baja = df[df['es_indefinido'] & df['fecha_baja'].notna()].copy()

    # Calcular duración real
    df_indefinidos_baja['meses_duracion'] = df_indefinidos_baja.apply(
        lambda r: _meses_duracion(r['fecha_alta'], r['fecha_baja']), axis=1
    )

    # Plazo requerido según bonificación
    df_indefinidos_baja['plazo_requerido_meses'] = df_indefinidos_baja.get(
        'bonificacion_aplicada', pd.Series(['general'] * len(df_indefinidos_baja))
    ).apply(_plazo_requerido)

    # Detectar rescisiones antes del plazo
    df_indefinidos_baja['rescindido_antes_plazo'] = (
        df_indefinidos_baja['meses_duracion'] <
        df_indefinidos_baja['plazo_requerido_meses']
    )

    alertas = df_indefinidos_baja[
        df_indefinidos_baja['rescindido_antes_plazo']
    ].copy()

    # Calcular bonificación en riesgo de reintegro
    if 'importe_bonificacion_mensual' in alertas.columns:
        alertas['meses_cobrados'] = alertas['meses_duracion'].apply(
            lambda m: round(m) if pd.notna(m) else 0
        )
        alertas['importe_bonificacion_cobrado'] = (
            alertas['meses_cobrados'] * alertas['importe_bonificacion_mensual']
        )
    else:
        alertas['importe_bonificacion_cobrado'] = np.nan

    # Causa sospechosa
    alertas['causa_sospechosa'] = alertas['causa_baja'].apply(
        lambda c: any(cs in str(c).lower() for cs in CAUSAS_SOSPECHOSAS_RESCISION)
        if pd.notna(c) else False
    )

    alertas['meses_faltantes'] = (
        alertas['plazo_requerido_meses'] - alertas['meses_duracion']
    ).round(1)

    alertas['nivel_alerta'] = alertas['meses_faltantes'].apply(
        lambda m: 'CRÍTICO' if m > 12 else ('ALTO' if m > 6 else 'MEDIO')
    )

    alertas['tipo_alerta'] = 'Indefinido rescindido antes del plazo obligatorio'
    alertas['normativa'] = (
        'Ley 43/2006 Bonificaciones · RD-ley 1/2015 · '
        'Ley 38/2003 Subvenciones art. 37 · GRI 401-1 · ODS 8'
    )
    alertas['descripcion'] = alertas.apply(
        lambda r: (
            f"Contrato indefinido de {r.get('nombre','N/D')} rescindido tras "
            f"{r['meses_duracion']:.1f} meses (obligatorio: {r['plazo_requerido_meses']}). "
            f"Faltan {r['meses_faltantes']:.1f} meses. "
            f"Causa: {r.get('causa_baja', 'no especificada')}. "
            + (f"Bonificación cobrada: {r['importe_bonificacion_cobrado']:,.0f}€ (sujeta a reintegro)."
               if pd.notna(r.get('importe_bonificacion_cobrado')) else '')
        ),
        axis=1
    )

    # Análisis por empresa
    resumen_empresa = alertas.groupby('NIF_empresa').agg(
        n_alertas=('NIF_trabajador', 'count'),
        importe_riesgo=('importe_bonificacion_cobrado', 'sum')
    ).reset_index() if not alertas.empty and 'NIF_empresa' in alertas.columns \
        else pd.DataFrame()

    total_indefinidos = len(df_indefinidos_baja)
    n_alertas = len(alertas)
    n_criticas = len(alertas[alertas['nivel_alerta'] == 'CRÍTICO']) \
        if not alertas.empty else 0
    importe_riesgo_total = alertas['importe_bonificacion_cobrado'].sum() \
        if not alertas.empty and alertas['importe_bonificacion_cobrado'].notna().any() else 0

    puntuacion = min(100, round(
        (n_criticas * 30) + ((n_alertas - n_criticas) * 15), 0
    ))

    resumen = {
        'total_indefinidos_con_baja': total_indefinidos,
        'rescindidos_antes_plazo': n_alertas,
        'pct_rescisiones_prematuras': round(n_alertas / total_indefinidos * 100, 1)
        if total_indefinidos > 0 else 0,
        'alertas_criticas': n_criticas,
        'importe_bonificacion_en_riesgo_eur': round(importe_riesgo_total, 2),
        'empresas_implicadas': alertas['NIF_empresa'].nunique()
        if not alertas.empty and 'NIF_empresa' in alertas.columns else 0,
        'puntuacion_riesgo': puntuacion,
        'ods_afectados': ['ODS 8', 'ODS 16'],
        'gri': ['GRI 401-1', 'GRI 205-1'],
        'normativa': ['Ley 43/2006', 'RD-ley 1/2015', 'Ley 38/2003 art. 37',
                      'LISOS art. 22', 'ET art. 49']
    }

    return {
        'alertas': alertas,
        'resumen_por_empresa': resumen_empresa,
        'resumen': resumen,
        'puntuacion_riesgo': puntuacion
    }


def generar_csv_ejemplo() -> pd.DataFrame:
    """Genera un CSV de ejemplo con la estructura esperada."""
    return pd.DataFrame([
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '11111111A',
         'nombre': 'Ana García', 'tipo_contrato': 'Indefinido bonificado',
         'fecha_alta': '2022-01-01', 'fecha_baja': '2022-11-15',
         'causa_baja': 'Mutuo acuerdo', 'bonificacion_aplicada': 'labora_emcorp',
         'importe_bonificacion_mensual': 125},
        {'NIF_empresa': 'B12345678', 'NIF_trabajador': '22222222B',
         'nombre': 'Pep Ros', 'tipo_contrato': 'Indefinido ordinario',
         'fecha_alta': '2020-06-01', 'fecha_baja': '2021-08-01',
         'causa_baja': 'Baja voluntaria', 'bonificacion_aplicada': 'general',
         'importe_bonificacion_mensual': 0},
        {'NIF_empresa': 'A87654321', 'NIF_trabajador': '33333333C',
         'nombre': 'Laura Vidal', 'tipo_contrato': 'Conversión a indefinido',
         'fecha_alta': '2021-03-01', 'fecha_baja': '2022-01-10',
         'causa_baja': 'Dimisión', 'bonificacion_aplicada': 'conversion_temporal',
         'importe_bonificacion_mensual': 108},
        {'NIF_empresa': 'A87654321', 'NIF_trabajador': '44444444D',
         'nombre': 'Tomàs Ferrer', 'tipo_contrato': 'Indefinido ordinario',
         'fecha_alta': '2019-01-01', 'fecha_baja': '2022-06-01',
         'causa_baja': 'Despido objetivo', 'bonificacion_aplicada': 'general',
         'importe_bonificacion_mensual': 0},
    ])
