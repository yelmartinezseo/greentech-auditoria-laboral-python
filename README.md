# Auditoría de Sostenibilidad Laboral Real — Greentech Plugin

**Plugin de WordPress** open source para detectar patrones de precariedad laboral encubierta en empresas con memorias de sostenibilidad.

Desarrollado por [Yel Martínez](https://yel-martinez-portfolio.com/wikipedia-profesional/) — tecnóloga y estratega digital especializada en ESG y patrimonio digital.

---

## Qué hace

Cruza los indicadores laborales que introduce el usuario con benchmarks sectoriales por **CNAE-2009**, calibrados con datos públicos del SEPE, INE y Ministerio de Trabajo, y genera un **Índice de Riesgo de Greenwashing Laboral** con alertas clasificadas por nivel de gravedad.

**Patrones que detecta:**
- Becarios sin remuneración y tasa de conversión a empleo
- Reincidencia en subvenciones Labora/SEPE por el mismo perfil de puesto sin antigüedad
- Concentración artificial de plantilla en categorías de baja remuneración (auxiliares administrativos)
- Rotación de contratos <6 meses sistemática
- Brecha salarial de género y representación femenina directiva
- Incoherencia entre memoria de sostenibilidad y práctica real
- Ausencia de Plan de Igualdad en empresas obligadas

---

## ODS y marco ESG

| ODS | Dimensión ESG | Estándar GRI | Normativa |
|-----|--------------|--------------|-----------|
| ODS 8 — Trabajo decente | Social (S) | GRI 401-1 | Reforma Laboral 2022, RD 592/2014 |
| ODS 10 — Reducir desigualdades | Social (S) | GRI 405-2 | RD 901/2020, LISOS |
| ODS 16 — Transparencia | Governance (G) | GRI 205-1, GRI 2-23 | CSRD/ESRS S1, Directiva 2019/1937 |

---

## Instalación

1. Descarga el archivo `.zip` del plugin
2. En WordPress: **Plugins → Añadir nuevo → Subir plugin**
3. Sube el ZIP y pulsa **Activar**
4. En la página donde quieras mostrar la herramienta, añade el shortcode:

```
[auditoria_laboral]
```

---

## Notas técnicas

- **Sin base de datos.** El plugin no crea tablas ni almacena datos de usuarios.
- **Sin peticiones externas.** Todo el cálculo ocurre en el navegador del visitante. Solo se carga Chart.js desde jsDelivr CDN.
- **CSS y JS inline.** Para evitar problemas de caché con CDN o proxies, los estilos y el script se inyectan inline en el shortcode con versión basada en `filemtime`.
- **Schema.org automático.** Si la página contiene `[auditoria_laboral]`, el plugin inyecta JSON-LD en el `<head>` con el nodo `SoftwareApplication` referenciando la entidad canónica `#yel-martinez`.
- **Compatible con Astra + Elementor.** CSS prefijado con `.gt-` para evitar conflictos con el tema.

---

## Estructura de archivos

```
auditoria-laboral/
├── auditoria-laboral.php        ← Plugin principal (shortcode + schema)
├── assets/
│   ├── auditoria-laboral.css   ← Paleta Marina Vibrante v3.3
│   └── auditoria-laboral.js    ← Motor de análisis + benchmarks CNAE
└── README.md
```

---

## Licencia

**GPL-2.0-or-later** — libre para usar, modificar y distribuir con atribución.

Atribución obligatoria:
```
Desarrollado por Yel Martínez — https://yel-martinez-portfolio.com
```

---

## Suite de herramientas ESG de Greentech

Esta herramienta forma parte de la suite open source de Yel Martínez:

- [Diagnóstico ESG para pymes](https://yel-martinez-portfolio.com/herramienta-de-diagnostico-esg-para-pymes/)
- [Generador de informe ASG/ESG](https://yel-martinez-portfolio.com/generador-de-informe-asg-esg-para-pymes/)
- [Calculadora de huella de carbono](https://yel-martinez-portfolio.com/carbon-calculator/)
- [Memoria de sostenibilidad GRI](https://yel-martinez-portfolio.com/generador-de-memoria-de-sostenibilidad-gri/)
- [Auditoría de greenwashing](https://yel-martinez-portfolio.com/greenwashing-auditoria-gratis-y-plantilla-descargable/)
- [SIR Autodiagnóstico](https://yel-martinez-portfolio.com/herramienta-de-autoevaluacion-para-registro-sir-entidades-socialmente-responsables/)
- [BYTE 404 Game](https://yel-martinez-portfolio.com/byte-404-greentech-game-de-yel-martinez/)
