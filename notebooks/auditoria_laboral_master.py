"""
NOTEBOOK MAESTRO — convertir a .ipynb con:
  jupyter nbconvert --to notebook --execute auditoria_laboral_master.py
O ejecutar directamente como script Python.
"""

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AUDITORÍA DE SOSTENIBILIDAD LABORAL REAL — Kit de análisis Python          ║
# ║  Greentech · Yel Martínez · yel-martinez-portfolio.com                      ║
# ║  GPL-3.0-or-later                                                           ║
# ║                                                                              ║
# ║  ODS 8, 10, 16 · ESG Social y Governance · GRI 401-1, 405-2, 205-1         ║
# ║                                                                              ║
# ║  ⚠️  IMPORTANTE: Este kit procesa datos locales del usuario.                ║
# ║  Ningún dato se envía a servidores externos. No consume APIs de terceros.   ║
# ║  Todo el análisis ocurre en tu máquina.                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar módulos de análisis
from m1_categoria_inferior      import analizar_categoria_inferior, generar_csv_plantilla_ejemplo
from m2_cruce_ss_subvenciones   import analizar_cruce_ss_subvenciones, generar_csvs_ejemplo as gen_m2
from m3_indefinidos_rescindidos import analizar_indefinidos_rescindidos, generar_csv_ejemplo as gen_m3
from m4_familiares_subvencion   import analizar_familiares_subvencion, generar_csvs_ejemplo as gen_m4
from m5_reincidencia_nif        import analizar_reincidencia_nif, generar_csv_ejemplo as gen_m5

# ── Paleta Marina Vibrante (coherente con plugin WordPress) ──────────────────
COLORES = {
    'navy':     '#122633',
    'blue':     '#155C8E',
    'burgundy': '#6B1A1A',
    'gold':     '#C9A84C',
    'cream':    '#F8EFD5',
    'critico':  '#6B1A1A',
    'alto':     '#b5820a',
    'medio':    '#2d6a4f',
    'ok':       '#2d6a2d',
}

plt.rcParams.update({
    'figure.facecolor': '#F8EFD5',
    'axes.facecolor':   '#FFFFFF',
    'axes.edgecolor':   '#122633',
    'axes.labelcolor':  '#122633',
    'xtick.color':      '#122633',
    'ytick.color':      '#122633',
    'text.color':       '#122633',
    'font.family':      'sans-serif',
    'font.size':        11,
})

print("=" * 70)
print("  AUDITORÍA DE SOSTENIBILIDAD LABORAL REAL")
print("  Greentech · Yel Martínez · yel-martinez-portfolio.com")
print("  ODS 8 · ODS 10 · ODS 16 | ESG S+G | GRI 401-1, 405-2, 205-1")
print("=" * 70)
print(f"\n  Análisis iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("  Todos los datos se procesan localmente. Sin APIs externas.\n")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN — Adapta estas rutas a tus archivos reales
# Si no tienes datos propios, se usan los datos de ejemplo incluidos
# ══════════════════════════════════════════════════════════════════════════════

USAR_DATOS_EJEMPLO = True   # Cambia a False y especifica rutas reales

RUTAS = {
    'plantilla':        '../data/plantilla.csv',
    'contratos_ss':     '../data/contratos_ss.csv',
    'subvenciones':     '../data/subvenciones.csv',
    'administradores':  '../data/administradores.csv',
    'convenio':         '../data/convenio.csv',          # opcional
}

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

if USAR_DATOS_EJEMPLO:
    print("  📂 Usando datos de ejemplo. Cambia USAR_DATOS_EJEMPLO=False")
    print("     y especifica RUTAS para analizar datos reales.\n")

    df_plantilla      = generar_csv_plantilla_ejemplo()
    df_contratos, df_subvenciones_m2 = gen_m2()
    df_contratos_m3   = gen_m3()
    df_plantilla_m4, df_administradores, df_subvenciones_m4 = gen_m4()
    df_subvenciones_m5 = gen_m5()

    # Para módulos que comparten datos, usar el mismo DataFrame de subvenciones
    df_subvenciones   = df_subvenciones_m2

else:
    print("  📂 Cargando datos reales...\n")
    df_plantilla      = pd.read_csv(RUTAS['plantilla'])
    df_contratos      = pd.read_csv(RUTAS['contratos_ss'])
    df_subvenciones   = pd.read_csv(RUTAS['subvenciones'])
    df_administradores = pd.read_csv(RUTAS['administradores'])
    df_contratos_m3   = df_contratos.copy()
    df_subvenciones_m4 = df_subvenciones.copy()
    df_subvenciones_m5 = df_subvenciones.copy()
    df_plantilla_m4   = df_plantilla.copy()
    df_subvenciones_m2 = df_subvenciones.copy()

    # Convenio (opcional)
    df_convenio = None
    if os.path.exists(RUTAS['convenio']):
        df_convenio = pd.read_csv(RUTAS['convenio'])

print(f"  ✓ Plantilla cargada: {len(df_plantilla)} registros")
print(f"  ✓ Contratos SS: {len(df_contratos)} registros")
print(f"  ✓ Subvenciones: {len(df_subvenciones)} registros\n")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1 — Categoría profesional inferior a funciones reales
# ══════════════════════════════════════════════════════════════════════════════

print("─" * 70)
print("  MÓDULO 1: Categoría inferior a funciones reales")
print("  ODS 8, 10 | GRI 405-2 | ET art. 22")
print("─" * 70)

r1 = analizar_categoria_inferior(df_plantilla)
res1 = r1['resumen']

print(f"\n  Total trabajadores analizados : {res1['total_trabajadores']}")
print(f"  Alertas categoría inferior    : {res1['alertas_categoria_inferior']}")
print(f"  % en categoría auxiliar (G5)  : {res1['pct_auxiliares_grupo5']:.1f}%")
print(f"  Puntuación de riesgo          : {res1['puntuacion_riesgo']}/100")

if not r1['alertas'].empty:
    print("\n  Casos detectados:")
    for _, row in r1['alertas'].iterrows():
        print(f"    ⚠️  {row.get('nombre','N/D')} — {row.get('descripcion','')}")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2 — Cruce fechas SS vs subvenciones
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("  MÓDULO 2: Cruce fechas alta/baja SS vs calendario subvenciones")
print("  ODS 16 | GRI 205-1 | Ley 38/2003")
print("─" * 70)

r2 = analizar_cruce_ss_subvenciones(df_contratos, df_subvenciones_m2)
res2 = r2['resumen']

print(f"\n  Bajas analizadas              : {res2['total_bajas_analizadas']}")
print(f"  Alertas en ventana oblig.     : {res2['alertas_en_ventana_obligatoriedad']}")
print(f"  Alertas críticas (±15 días)   : {res2['alertas_criticas_15dias']}")
print(f"  Empresas reincidentes         : {res2['empresas_reincidentes_misma_convocatoria']}")
print(f"  Importe en riesgo             : {res2['importe_subvenciones_en_riesgo_eur']:,.0f}€")
print(f"  Puntuación de riesgo          : {res2['puntuacion_riesgo']}/100")

if not r2['alertas'].empty:
    print("\n  Casos detectados:")
    for _, row in r2['alertas'].iterrows():
        nivel = row.get('nivel_alerta', '')
        icono = '🔴' if nivel == 'CRÍTICO' else '🟠'
        print(f"    {icono} [{nivel}] {row.get('descripcion','')[:120]}...")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3 — Indefinidos rescindidos antes del plazo
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("  MÓDULO 3: Contratos indefinidos rescindidos antes del plazo")
print("  ODS 8, 16 | GRI 401-1 | Ley 43/2006")
print("─" * 70)

r3 = analizar_indefinidos_rescindidos(df_contratos_m3)
res3 = r3['resumen']

print(f"\n  Indefinidos con baja          : {res3['total_indefinidos_con_baja']}")
print(f"  Rescindidos antes del plazo   : {res3['rescindidos_antes_plazo']}")
print(f"  % rescisiones prematuras      : {res3['pct_rescisiones_prematuras']:.1f}%")
print(f"  Bonificación en riesgo        : {res3['importe_bonificacion_en_riesgo_eur']:,.0f}€")
print(f"  Puntuación de riesgo          : {res3['puntuacion_riesgo']}/100")

if not r3['alertas'].empty:
    print("\n  Casos detectados:")
    for _, row in r3['alertas'].iterrows():
        print(f"    ⚠️  {row.get('descripcion','')[:120]}...")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4 — Familiares en picos de subvención
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("  MÓDULO 4: Detección de familiares contratados en picos de subvención")
print("  ODS 16 | GRI 205-1 | Ley 38/2003 art. 31")
print("  ⚠️  Señal de alerta inicial — requiere verificación manual")
print("─" * 70)

r4 = analizar_familiares_subvencion(
    df_plantilla_m4, df_administradores, df_subvenciones_m4
)
res4 = r4['resumen']

print(f"\n  Trabajadores analizados       : {res4['total_trabajadores_analizados']}")
print(f"  Alertas posible familiar      : {res4['alertas_posible_familiar']}")
print(f"  Alertas críticas (≤30 días)   : {res4['alertas_criticas_30dias']}")
print(f"  Importe subv. en riesgo       : {res4['importe_subvenciones_en_riesgo_eur']:,.0f}€")
print(f"  Puntuación de riesgo          : {res4['puntuacion_riesgo']}/100")
print(f"\n  Nota: {res4['nota_metodologica'][:100]}...")

if not r4['alertas'].empty:
    print("\n  Casos detectados:")
    for _, row in r4['alertas'].iterrows():
        print(f"    🔴 [{row.get('nivel_alerta','')}] {row.get('descripcion','')[:120]}...")

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5 — Reincidencia sistemática NIF empresa
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("  MÓDULO 5: Reincidencia sistemática en convocatorias por NIF empresa")
print("  ODS 16, 8 | GRI 205-1 | Ley 38/2003")
print("─" * 70)

r5 = analizar_reincidencia_nif(df_subvenciones_m5, df_plantilla)
res5 = r5['resumen']

print(f"\n  Empresas analizadas           : {res5['total_empresas_analizadas']}")
print(f"  Con patrón de reincidencia    : {res5['empresas_con_patron_reincidencia']}")
print(f"  Empresas críticas             : {res5['empresas_criticas']}")
print(f"  Importe total en riesgo       : {res5['importe_total_en_riesgo_eur']:,.0f}€")
print(f"  Puntuación de riesgo          : {res5['puntuacion_riesgo']}/100")

if not r5['alertas'].empty:
    print("\n  Ranking de empresas con patrón:")
    for _, row in r5['alertas'].iterrows():
        print(f"    {'🔴' if row['nivel_alerta']=='CRÍTICO' else '🟠'} "
              f"[{row['nivel_alerta']}] {row.get('nombre_empresa','N/D')}: "
              f"{row.get('descripcion','')[:100]}...")

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD VISUAL — Resumen ejecutivo
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  GENERANDO DASHBOARD VISUAL...")
print("=" * 70)

puntuaciones = {
    'M1\nCategoría inferior': r1['puntuacion_riesgo'],
    'M2\nCruce SS-Subv.':     r2['puntuacion_riesgo'],
    'M3\nIndefinidos':        r3['puntuacion_riesgo'],
    'M4\nFamiliares':         r4['puntuacion_riesgo'],
    'M5\nReincidencia NIF':   r5['puntuacion_riesgo'],
}

colores_barra = [
    COLORES['critico'] if v >= 70 else
    COLORES['alto']    if v >= 40 else
    COLORES['medio']   if v >= 20 else
    COLORES['ok']
    for v in puntuaciones.values()
]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor(COLORES['cream'])
fig.suptitle(
    'Auditoría de Sostenibilidad Laboral Real\nGreentech · Yel Martínez · yel-martinez-portfolio.com',
    fontsize=13, fontweight='bold', color=COLORES['navy'], y=1.02
)

# Gráfico 1: Puntuaciones por módulo
ax1 = axes[0]
bars = ax1.barh(
    list(puntuaciones.keys()),
    list(puntuaciones.values()),
    color=colores_barra,
    edgecolor=COLORES['navy'],
    linewidth=0.8,
    height=0.6
)
ax1.set_xlim(0, 100)
ax1.set_xlabel('Índice de riesgo (0–100)', fontweight='bold')
ax1.set_title('Riesgo por módulo de análisis', fontweight='bold', color=COLORES['navy'])
ax1.axvline(x=70, color=COLORES['critico'], linestyle='--', alpha=0.5, linewidth=1)
ax1.axvline(x=40, color=COLORES['alto'],    linestyle='--', alpha=0.5, linewidth=1)

for bar, val in zip(bars, puntuaciones.values()):
    ax1.text(
        min(val + 2, 95), bar.get_y() + bar.get_height() / 2,
        f'{val}', va='center', fontweight='bold',
        color=COLORES['navy'], fontsize=10
    )

leyenda = [
    mpatches.Patch(color=COLORES['critico'], label='Crítico (≥70)'),
    mpatches.Patch(color=COLORES['alto'],    label='Alto (40–69)'),
    mpatches.Patch(color=COLORES['medio'],   label='Medio (20–39)'),
    mpatches.Patch(color=COLORES['ok'],      label='Bajo (<20)'),
]
ax1.legend(handles=leyenda, loc='lower right', fontsize=9)

# Gráfico 2: ODS afectados (conteo de alertas por ODS)
ods_conteo = {'ODS 8': 0, 'ODS 10': 0, 'ODS 16': 0}
for r in [res1, res2, res3, res4, res5]:
    for ods in r.get('ods_afectados', []):
        if ods in ods_conteo:
            ods_conteo[ods] += r.get('puntuacion_riesgo', 0) / 10

ax2 = axes[1]
ods_colores = ['#A21942', '#DD1367', '#02689C']  # colores ONU
wedges, texts, autotexts = ax2.pie(
    ods_conteo.values(),
    labels=list(ods_conteo.keys()),
    colors=ods_colores,
    autopct='%1.0f%%',
    startangle=90,
    textprops={'color': 'white', 'fontweight': 'bold'},
    wedgeprops={'edgecolor': COLORES['cream'], 'linewidth': 2}
)
ax2.set_title('Peso de alertas por ODS', fontweight='bold', color=COLORES['navy'])

plt.tight_layout()

# Guardar en reports/
os.makedirs('../reports', exist_ok=True)
fig_path = f"../reports/auditoria_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
plt.savefig(fig_path, dpi=150, bbox_inches='tight', facecolor=COLORES['cream'])
print(f"\n  ✓ Dashboard guardado en: {fig_path}")
plt.show()

# ══════════════════════════════════════════════════════════════════════════════
# EXPORTAR ALERTAS A EXCEL
# ══════════════════════════════════════════════════════════════════════════════

excel_path = f"../reports/alertas_auditoria_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:

    # Hoja resumen ejecutivo
    resumen_global = pd.DataFrame([
        {'Módulo': 'M1 — Categoría inferior a funciones',
         'Alertas': res1['alertas_categoria_inferior'],
         'Riesgo (0-100)': res1['puntuacion_riesgo'],
         'ODS': 'ODS 8, 10', 'GRI': 'GRI 405-2, 401-1'},
        {'Módulo': 'M2 — Cruce SS vs Subvenciones',
         'Alertas': res2['alertas_en_ventana_obligatoriedad'],
         'Riesgo (0-100)': res2['puntuacion_riesgo'],
         'ODS': 'ODS 16, 8', 'GRI': 'GRI 205-1, 201-4'},
        {'Módulo': 'M3 — Indefinidos rescindidos',
         'Alertas': res3['rescindidos_antes_plazo'],
         'Riesgo (0-100)': res3['puntuacion_riesgo'],
         'ODS': 'ODS 8, 16', 'GRI': 'GRI 401-1, 205-1'},
        {'Módulo': 'M4 — Familiares en picos subvención',
         'Alertas': res4['alertas_posible_familiar'],
         'Riesgo (0-100)': res4['puntuacion_riesgo'],
         'ODS': 'ODS 16', 'GRI': 'GRI 205-1'},
        {'Módulo': 'M5 — Reincidencia NIF empresa',
         'Alertas': res5['empresas_con_patron_reincidencia'],
         'Riesgo (0-100)': res5['puntuacion_riesgo'],
         'ODS': 'ODS 16, 8', 'GRI': 'GRI 205-1, 201-4'},
    ])
    resumen_global.to_excel(writer, sheet_name='Resumen ejecutivo', index=False)

    # Hoja de atribución — aparece en todos los informes exportados
    atribucion = pd.DataFrame([
        {'Campo': 'Herramienta',   'Valor': 'Auditoría de Sostenibilidad Laboral Real'},
        {'Campo': 'Autora',        'Valor': 'Yel Martínez'},
        {'Campo': 'Perfil',        'Valor': 'https://yel-martinez-portfolio.com/wikipedia-profesional/'},
        {'Campo': 'Web portfolio', 'Valor': 'https://yel-martinez-portfolio.com'},
        {'Campo': 'Herramienta web', 'Valor': 'https://yel-martinez-portfolio.com/auditoria-sostenibilidad-laboral/'},
        {'Campo': 'Repositorio',   'Valor': 'https://github.com/yelmartinezseo/greentech-auditoria-laboral-python'},
        {'Campo': 'Licencia',      'Valor': 'GPL-3.0-or-later'},
        {'Campo': 'Atribución',    'Valor': 'La redistribución y publicación de informes generados con este kit requiere mantener esta atribución.'},
        {'Campo': 'Fecha análisis','Valor': datetime.now().strftime('%Y-%m-%d %H:%M')},
        {'Campo': 'Marco ODS',     'Valor': 'ODS 8 · ODS 10 · ODS 16'},
        {'Campo': 'Marco ESG',     'Valor': 'Dimensión Social (S) + Governance (G)'},
        {'Campo': 'Estándares GRI','Valor': 'GRI 401-1 · GRI 405-2 · GRI 205-1 · GRI 201-4 · GRI 2-23'},
    ])
    atribucion.to_excel(writer, sheet_name='Atribución', index=False)

    # Una hoja por módulo
    if not r1['alertas'].empty:
        r1['alertas'].to_excel(writer, sheet_name='M1 Categoría inferior', index=False)
    if not r2['alertas'].empty:
        r2['alertas'].to_excel(writer, sheet_name='M2 Cruce SS-Subvenciones', index=False)
    if not r3['alertas'].empty:
        r3['alertas'].to_excel(writer, sheet_name='M3 Indefinidos rescindidos', index=False)
    if not r4['alertas'].empty:
        r4['alertas'].to_excel(writer, sheet_name='M4 Familiares subvención', index=False)
    if not r5['alertas'].empty:
        r5['alertas'].to_excel(writer, sheet_name='M5 Reincidencia NIF', index=False)
    if not r5['ranking_empresas'].empty:
        r5['ranking_empresas'].to_excel(
            writer, sheet_name='Ranking empresas', index=False
        )

print(f"  ✓ Informe Excel guardado en: {excel_path}")

# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════

total_alertas = (
    res1['alertas_categoria_inferior'] +
    res2['alertas_en_ventana_obligatoriedad'] +
    res3['rescindidos_antes_plazo'] +
    res4['alertas_posible_familiar'] +
    res5['empresas_con_patron_reincidencia']
)

riesgo_global = round(np.mean([
    res1['puntuacion_riesgo'],
    res2['puntuacion_riesgo'],
    res3['puntuacion_riesgo'],
    res4['puntuacion_riesgo'],
    res5['puntuacion_riesgo'],
]), 1)

print("\n" + "=" * 70)
print("  RESUMEN FINAL DE AUDITORÍA")
print("=" * 70)
print(f"\n  Total alertas detectadas      : {total_alertas}")
print(f"  Índice de riesgo global       : {riesgo_global}/100")
print(f"  ODS afectados                 : ODS 8, ODS 10, ODS 16")
print(f"  Marco ESG                     : Dimensión Social (S) + Governance (G)")
print(f"  Estándares GRI                : 401-1, 405-2, 205-1, 201-4, 2-23")
print(f"\n  Archivos generados:")
print(f"    • {fig_path}")
print(f"    • {excel_path}")
print(f"\n  ⚠️  Los resultados son orientativos y requieren verificación")
print(f"     documental antes de cualquier acción legal o administrativa.")
print(f"\n  Desarrollado por Yel Martínez")
print(f"  https://yel-martinez-portfolio.com/wikipedia-profesional/")
print(f"  https://github.com/yelmartinezseo/greentech-auditoria-laboral-python")
print(f"  GPL-3.0-or-later — Sin APIs externas — Procesamiento local")
print("=" * 70)
