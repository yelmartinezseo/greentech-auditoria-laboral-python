# Estructura de archivos CSV de entrada

Greentech · Auditoría de Sostenibilidad Laboral Real — Kit Python
Yel Martínez · yel-martinez-portfolio.com · GPL-2.0-or-later

---

## Cómo obtener cada archivo

Ningún módulo accede directamente a bases de datos externas.
El usuario aporta sus propios CSVs exportados desde las fuentes disponibles.

---

## plantilla.csv — Datos de plantilla

Fuentes: Nóminas, software RRHH (Factorial, A3, Nominasol, SAGE), ERP propio.

| Columna | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| NIF_empresa | str | NIF/CIF de la empresa | ✓ |
| NIF_trabajador | str | NIF del empleado | ✓ |
| nombre | str | Nombre completo | ✓ |
| categoria_contrato | str | Categoría según contrato (ej: "Auxiliar Administrativo") | ✓ |
| salario_bruto | float | Salario bruto anual en euros | ✓ |
| fecha_alta | date | Fecha de alta en empresa (DD/MM/YYYY) | ✓ |
| departamento | str | Departamento o área | |
| funciones_declaradas | str | Descripción libre de tareas reales (clave para M1) | recomendado |

---

## contratos_ss.csv — Altas y bajas en Seguridad Social

Fuentes:
- **Empresas**: Exportación de SILTRA / Sistema RED (afiliación)
- **Administración**: TGSS (con convenio de acceso)
- **Parcial**: Vida Laboral individual (por cada trabajador)

| Columna | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| NIF_empresa | str | NIF/CIF de la empresa | ✓ |
| NIF_trabajador | str | NIF del empleado | ✓ |
| nombre | str | Nombre completo | ✓ |
| tipo_contrato | str | Tipo (ej: "Indefinido", "Temporal", "Fijo discontinuo") | ✓ |
| fecha_alta | date | Fecha de alta SS | ✓ |
| fecha_baja | date | Fecha de baja SS (vacío si sigue activo) | |
| causa_baja | str | Causa de la baja (ej: "Mutuo acuerdo", "Despido") | |
| categoria | str | Categoría profesional según contrato | |
| salario_bruto | float | Salario bruto anual | |
| bonificacion_aplicada | str | Tipo de bonificación (ej: "labora_emcorp", "general") | M3 |
| importe_bonificacion_mensual | float | €/mes de bonificación a SS | M3 |

---

## subvenciones.csv — Subvenciones de empleo concedidas

Fuentes:
- **Labora (CV)**: Resoluciones publicadas en DOGV / Portal de transparencia Labora
- **SEPE**: Estadísticas de bonificaciones y subvenciones (datos agregados públicos)
- **Otras CCAA**: Portales de transparencia autonómicos (SAE, SOC, Lanbide, etc.)
- **BDNS** (Base de Datos Nacional de Subvenciones): https://www.infosubvenciones.es

| Columna | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| NIF_empresa | str | NIF/CIF de la empresa beneficiaria | ✓ |
| nombre_empresa | str | Razón social | |
| convocatoria | str | Nombre del programa (ej: "Labora EMCORP 2023") | ✓ |
| organismo | str | Organismo concedente (Labora, SEPE, SAE...) | ✓ |
| año | int | Año de la convocatoria | |
| fecha_resolucion | date | Fecha de resolución de concesión | ✓ |
| importe | float | Importe concedido en euros | ✓ |
| n_puestos | int | Número de puestos subvencionados | |
| tipo_contrato_subvencionado | str | Tipo de contrato exigido | |
| meses_obligatoriedad | int | Meses de mantenimiento del empleo obligatorio | M2 |
| NIF_trabajador_vinculado | str | NIF del trabajador vinculado a la subvención | M2, M4 |

---

## administradores.csv — Administradores/titulares de empresas

Fuentes:
- **Registro Mercantil Central**: https://www.rmc.es (consulta por NIF)
- **Empresia / SABI / Axesor**: agregadores de datos del Registro Mercantil
- **BORME** (BOE): https://boe.es/diario_borme/

| Columna | Tipo | Descripción | Obligatorio |
|---|---|---|---|
| NIF_empresa | str | NIF/CIF de la empresa | ✓ |
| NIF_administrador | str | NIF del administrador | ✓ |
| nombre_administrador | str | Nombre completo del administrador | ✓ |
| apellidos_administrador | str | Apellidos (si están separados) | recomendado |
| cargo | str | Cargo (ej: "Administrador único", "Consejero") | |

---

## convenio.csv — Salarios mínimos por grupo profesional (opcional)

Fuentes: Convenio colectivo sectorial aplicable (BOE/DOGV).

| Columna | Tipo | Descripción |
|---|---|---|
| grupo_profesional | int | Número de grupo (1–5) |
| categoria | str | Nombre de la categoría |
| salario_minimo_anual | float | Salario mínimo anual del grupo en euros |

---

## Notas legales

**RGPD**: Si los datos incluyen información personal de trabajadores identificables,
el tratamiento debe realizarse bajo base legal apropiada (art. 6 RGPD):
contrato laboral, obligación legal, o interés legítimo documentado.

**Secreto estadístico**: Los datos del SEPE y TGSS disponibles públicamente
son agregados y anonimizados. El acceso a datos individualizados requiere
convenio administrativo firmado con el organismo correspondiente.

**Uso en Inspección de Trabajo**: La herramienta *Maximiliano* de la ITSS
utiliza lógica similar (cruce TGSS–BDNS) sobre datos a los que la Inspección
accede directamente. Este kit reproduce la lógica analítica con los datos
que el usuario legalmente tiene disponibles.

---

Desarrollado por Yel Martínez — https://yel-martinez-portfolio.com
GPL-2.0-or-later — Procesamiento 100% local — Sin APIs externas
