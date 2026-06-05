# Política de seguridad — greentech-auditoria-laboral-python

## Principios de diseño relevantes para la seguridad

Este kit está diseñado para funcionar **100% de forma local**:

- **Sin backend propio** — no hay servidor que atacar
- **Sin APIs externas** — no transmite datos a terceros
- **Sin telemetría** — no hay eventos de seguimiento
- **Los datos del usuario nunca salen de su máquina**

## Qué reportar

Reporta vulnerabilidades si encuentras que el kit:

- Podría ser manipulado para exfiltrar datos del usuario a través de
  dependencias comprometidas (supply chain)
- Tiene comportamiento no documentado al procesar CSVs malformados o maliciosos
- Genera informes que filtran datos sensibles de forma no esperada

## Qué NO es una vulnerabilidad de este proyecto

- Dependencias de terceros con vulnerabilidades propias (reporta a sus mantenedores)
- El análisis de datos que el propio usuario introduce — el kit no valida la
  legalidad de los datos de entrada, esa responsabilidad es del usuario
  (ver nota RGPD en `docs/estructura_csvs.md`)

## Cómo reportar

**Email**: contacto@yel-martinez-portfolio.com  
**Asunto**: `[SECURITY] greentech-auditoria-laboral-python`

No abras un Issue público para vulnerabilidades de seguridad.  
Respuesta en menos de 72 horas en días laborables.

## Versiones con soporte activo

| Versión | Soporte |
|---------|---------|
| 1.0.x   | ✅ Activo |

---

Yel Martínez — https://yel-martinez-portfolio.com
