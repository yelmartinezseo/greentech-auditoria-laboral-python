# Auditoría de Sostenibilidad Laboral Real — Kit Python

**Greentech · Yel Martínez · yel-martinez-portfolio.com**

Kit de análisis de datos Python para detectar patrones de precariedad laboral
encubierta en empresas con memorias de sostenibilidad. Complementa el
[plugin WordPress](https://yel-martinez-portfolio.com/auditoria-sostenibilidad-laboral/)
con análisis de datos reales aportados por el usuario.

---

## ⚠️ Principios de diseño

- **Sin backend propio.** Todo el análisis ocurre en la máquina del usuario.
- **Sin APIs externas.** No consume OpenAI, Claude ni ningún servicio de pago.
- **Sin telemetría.** No envía datos a ningún servidor.
- **El usuario aporta sus datos.** Los CSVs son suyos, los procesa localmente.

---

## Módulos incluidos

| Módulo | Patrón detectado | ODS | GRI |
|--------|-----------------|-----|-----|
| `m1_categoria_inferior.py` | Categoría contractual inferior a funciones reales | 8, 10 | 405-2 |
| `m2_cruce_ss_subvenciones.py` | Bajas SS coincidentes con vencimiento de obligatoriedad | 16 | 205-1 |
| `m3_indefinidos_rescindidos.py` | Indefinidos rescindidos antes del plazo de bonificación | 8, 16 | 401-1 |
| `m4_familiares_subvencion.py` | Posibles familiares contratados en picos de subvención | 16 | 205-1 |
| `m5_reincidencia_nif.py` | Dependencia estructural de subvenciones por NIF empresa | 16, 8 | 205-1 |

---

## Instalación

```bash
git clone https://github.com/yelmartinezseo/greentech-auditoria-laboral-python
cd greentech-auditoria-laboral-python
pip install -r requirements.txt
```

## Uso rápido (datos de ejemplo)

```bash
cd notebooks
python auditoria_laboral_master.py
```

Genera en `reports/`:
- Dashboard visual PNG (paleta Marina Vibrante)
- Informe Excel con una hoja por módulo

## Uso con datos reales

1. Prepara tus CSVs según la estructura documentada en `docs/estructura_csvs.md`
2. Cópialos en `data/`
3. Edita `USAR_DATOS_EJEMPLO = False` en el notebook maestro
4. Especifica las rutas en el dict `RUTAS`
5. Ejecuta

---

## Fuentes de datos compatibles

- **SEPE**: Estadística de Contratos Registrados (CSV público)
- **Labora**: Resoluciones de convocatorias (DOGV, portal transparencia)
- **BDNS**: Base de Datos Nacional de Subvenciones (infosubvenciones.es)
- **SILTRA/Sistema RED**: Exportación de afiliación (empresas con acceso propio)
- **Registro Mercantil**: Administradores vía BORME/Empresia
- **Software RRHH propio**: Factorial, A3, Nominasol, SAGE, etc.

---

## Marco normativo implementado

**ODS Naciones Unidas**: 8 (Trabajo decente), 10 (Reducir desigualdades), 16 (Transparencia)

**GRI Standards**: 401-1, 405-2, 205-1, 201-4, 2-23

**Normativa española**:
- ET art. 22 (clasificación profesional)
- Ley 43/2006 (bonificaciones contratos)
- RD-ley 1/2015
- Ley 38/2003 General de Subvenciones
- RD 887/2006 (Reglamento Subvenciones)
- LISOS (infracciones laborales)
- RD 901/2020 (Planes de Igualdad)
- Reforma Laboral 2022 (RDL 32/2021)

**Referencia técnica**: Herramienta *Maximiliano* (ITSS — Inspección de Trabajo)
que usa lógica equivalente con acceso directo a TGSS y BDNS.

---

## Suite completa de herramientas ESG — Greentech

- [Plugin WordPress — Auditoría Laboral](https://yel-martinez-portfolio.com/auditoria-sostenibilidad-laboral/)
- [Diagnóstico ESG](https://yel-martinez-portfolio.com/herramienta-de-diagnostico-esg-para-pymes/)
- [Calculadora huella de carbono](https://yel-martinez-portfolio.com/carbon-calculator/)
- [Generador memoria GRI](https://yel-martinez-portfolio.com/generador-de-memoria-de-sostenibilidad-gri/)
- [Auditoría greenwashing](https://yel-martinez-portfolio.com/greenwashing-auditoria-gratis-y-plantilla-descargable/)

---

**Licencia**: GPL-2.0-or-later  
**Autora**: Yel Martínez — tecnóloga y estratega digital  
**Perfil canónico**: https://yel-martinez-portfolio.com/wikipedia-profesional/
