# Cómo contribuir — greentech-auditoria-laboral-python

**Greentech · Yel Martínez · yel-martinez-portfolio.com**

Gracias por tu interés en mejorar este kit. Cualquier contribución que refuerce
la detección de patrones de precariedad laboral encubierta es bienvenida.

---

## Tipos de contribución que se aceptan

- **Nuevos módulos de detección** — patrones no cubiertos por los 5 módulos actuales
- **Benchmarks sectoriales adicionales** — datos CNAE que mejoren la calibración
- **Soporte para nuevas fuentes de datos** — portales autonómicos distintos de Labora/SEPE
- **Mejoras de rendimiento** — sin romper compatibilidad con pandas ≥ 2.0
- **Correcciones de bugs** — especialmente en detección de falsos positivos
- **Traducciones de documentación** — actualmente ES; se acepta EN, CA, EU, GL

## Tipos de contribución que NO se aceptan

- Dependencias de APIs externas (el principio de diseño es 100% local)
- Telemetría o envío de datos a servidores
- Módulos que identifiquen personas sin base legal clara (ver nota RGPD en `docs/`)

---

## Proceso

1. Abre un **Issue** describiendo el cambio antes de implementarlo
2. Haz fork del repositorio
3. Crea una rama: `git checkout -b feat/nombre-del-modulo`
4. Implementa con docstring en el mismo formato que los módulos existentes
5. Incluye al menos un conjunto de datos sintéticos de prueba en `tests/`
6. Abre un Pull Request con descripción del patrón detectado y fuente normativa

---

## Estilo de código

- Docstrings en español con referencia ODS y GRI exacta
- Sin f-strings de Python < 3.8
- Compatibilidad: Python ≥ 3.9, pandas ≥ 2.0, numpy ≥ 1.24

---

## Atribución

Las contribuciones aceptadas aparecerán en el historial de commits y en
el apartado de colaboradores del repositorio. Los informes generados por
el kit seguirán incluyendo la atribución principal a Yel Martínez según
lo establecido en `ATTRIBUTION.md` y la GPL-3.0.

---

Yel Martínez — https://yel-martinez-portfolio.com  
Repositorio: https://github.com/yelmartinezseo/greentech-auditoria-laboral-python
