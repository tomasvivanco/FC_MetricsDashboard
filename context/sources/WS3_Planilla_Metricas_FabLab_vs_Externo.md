# Planilla de Metricas — Que puede medir un Fab Lab / Fab City

**Fuente:** `3_Detailed_Metrics.docx` (Tomas Vivanco) — 95 indicadores, 5 escalas x 4 pilares
**Proposito:** identificar, de cada indicador de la planilla original, cuales puede instrumentar
directamente la red Fab City (fab lab, comunidad, fablabs.io, Smart Citizen, Precious Plastic) y
cuales dependen de estadistica publica/institucional externa al lab.

**Como leer la columna "Quien mide":**
- 🔧 **FAB LAB / FC** — el lab o la comunidad genera el dato directamente (logs, sensores, encuestas propias, registros de taller)
- 🌐 **EXTERNO** — requiere agencia estadistica, gobierno municipal/regional, base de datos internacional
- ⚖️ **MIXTO** — el lab puede aportar una parte (insumo, proxy, sub-muestra) pero el indicador completo necesita dato externo

---

## Escala 1: Community — la escala donde el Fab Lab ES la fuente

**Esta es la escala donde casi todo el indicador-set fue diseñado pensando en el lab mismo.**
13 de 21 indicadores son 🔧 directos.

### Ambiental
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Material reused/recycled locally | 🔧 FAB LAB | Inventario de insumos del makerspace — ya es un log que el lab lleva |
| Products repaired | 🔧 FAB LAB | Registro de taller de reparacion |
| Waste diverted from landfill | 🔧 FAB LAB | Sistema de seguimiento de residuos del lab |
| Energy consumed (renewable) | ⚖️ MIXTO | Medidor inteligente en el lab da el consumo; el % renovable depende de la matriz energetica local (externo) |
| Local food production | 🔧 FAB LAB | Si el lab opera huertos/agricultura urbana asociada |
| Water reused/harvested | 🔧 FAB LAB | Monitoreo de agua si el lab tiene sistema de cosecha/reuso instalado |

### Social
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Participants in making activities | 🔧 FAB LAB | Registro de asistencia — dato mas basico que un lab ya tiene |
| Skills training sessions delivered | 🔧 FAB LAB | Calendario de talleres |
| New skills acquired | 🔧 FAB LAB | Encuesta pre/post sesion — el lab la diseña y aplica |
| Community satisfaction | 🔧 FAB LAB | Encuesta comunitaria propia |
| Social cohesion index | 🔧 FAB LAB | Encuesta de red social — exige diseño metodologico pero el lab puede aplicarla |
| Vulnerable groups included | 🔧 FAB LAB | Ficha de intake demografica (opt-in) en el lab |

### Economico
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Local jobs created | ⚖️ MIXTO | El lab cuenta los empleos que genera directamente; valida con registro de empleo formal externo |
| Value of goods produced | 🔧 FAB LAB | Registro de transacciones/ventas del lab |
| Savings from repair/reuse | 🔧 FAB LAB | Calculo de costo evitado — el lab tiene los datos del taller de reparacion |
| Local businesses supported | 🔧 FAB LAB | Registro de partnerships del lab |
| Revenue retained locally | ⚖️ MIXTO | Requiere analisis de flujo economico — el lab aporta sus propios datos, pero el % total community-wide necesita estudio externo |

### Gobernanza
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Participation in decision-making | 🔧 FAB LAB | Asistencia a reuniones del lab/comunidad |
| Meetings/workshops held | 🔧 FAB LAB | Registro de calendario |
| Partnerships with institutions | 🔧 FAB LAB | Log de partnerships del lab |
| Transparency of operations | 🔧 FAB LAB | Auto-evaluacion del lab |
| Documented knowledge shared | 🔧 FAB LAB | Conteo de recursos en el repositorio — fablabs.io, documentacion propia |

**Resumen Community: 16 directos / 4 mixtos / 0 externos de 21 indicadores — la escala donde la red tiene maxima soberania de dato.**

---

## Escala 2: City — el lab aporta una fraccion, la mayoria es estadistica municipal

### Ambiental
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Sectoral self-sufficiency (Fab City Index) | 🌐 EXTERNO | Analisis de produccion-consumo, requiere estadistica de comercio/produccion a nivel ciudad |
| Material consumption | 🌐 EXTERNO | MFA + datos municipales de residuos |
| Recycling rate | 🌐 EXTERNO | Datos de la autoridad municipal de residuos |
| GHG emissions | 🌐 EXTERNO | Inventario de emisiones (protocolo GPC) |
| Renewable energy share | 🌐 EXTERNO | Estadistica energetica municipal |
| Urban metabolism efficiency | 🌐 EXTERNO | MFA + datos economicos |
| Green space per capita | 🌐 EXTERNO | Analisis GIS sobre catastro municipal |
| Air quality (PM2.5) | ⚖️ MIXTO | Estaciones de referencia municipal **+ kits Smart Citizen del lab pueden densificar la red de monitoreo** |

### Social
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Unemployment rate | 🌐 EXTERNO | Estadistica laboral nacional/municipal |
| Income inequality (Gini) | 🌐 EXTERNO | Encuestas economicas |
| Access to education | 🌐 EXTERNO | Analisis GIS municipal |
| Life expectancy | 🌐 EXTERNO | Estadisticas de salud |
| Affordable housing | 🌐 EXTERNO | Datos de vivienda municipal |
| Digital inclusion | 🌐 EXTERNO | Encuestas de conectividad |
| Citizen engagement | ⚖️ MIXTO | Datos electorales (externo) **+ participacion en Decidim/plataformas civicas que el lab puede promover y registrar localmente** |

### Economico
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| GDP per capita | 🌐 EXTERNO | Estadistica economica |
| Circular economy jobs | 🌐 EXTERNO | Encuestas de empleo |
| Local business density | 🌐 EXTERNO | Registro de negocios |
| R&D investment | 🌐 EXTERNO | Estadistica de innovacion |
| Supply chain localization | 🌐 EXTERNO | Encuestas a negocios |
| Circular economy revenue | 🌐 EXTERNO | Analisis economico |

### Gobernanza
| Indicador | Quien mide | Como lo levanta el lab |
|---|---|---|
| Policy coherence | 🌐 EXTERNO | Analisis de politicas publicas |
| Budget allocated to CE/sustainability | 🌐 EXTERNO | Analisis presupuestario municipal |
| Open data availability | 🌐 EXTERNO | Auditoria del portal de datos abiertos |
| Stakeholder participation | 🌐 EXTERNO | Registros de consulta publica |
| Inter-departmental collaboration | 🌐 EXTERNO | Seguimiento de proyectos municipales |
| Monitoring & reporting frequency | 🌐 EXTERNO | Registros de publicacion institucional |

**Resumen City: 0 directos / 2 mixtos / 19 externos de 21 — la escala mas dependiente de estadistica oficial. La unica entrada propia de la red es la densificacion de sensores Smart Citizen y la participacion en plataformas civicas.**

*Nota: el catalogo de indicadores de ingesta (Data Points Catalog) añade aqui indicadores propios de
red — densidad de fablabs.io, alumni de Fab Academy, Precious Plastic — que no estan en la planilla
original de Vivanco pero que SI son 🔧 FAB LAB. Ver seccion final.*

---

## Escala 3: Region — practicamente toda externa

### Ambiental
| Indicador | Quien mide |
|---|---|
| Regional material flows | 🌐 EXTERNO — MFA regional |
| Inter-city material exchange | 🌐 EXTERNO — datos de comercio + encuestas |
| Regional energy independence | 🌐 EXTERNO — estadistica energetica |
| GHG emissions (regional) | 🌐 EXTERNO — inventario regional |
| Land use efficiency | 🌐 EXTERNO — satelite + GIS |
| Water security | 🌐 EXTERNO — evaluacion de recursos hidricos |

### Social
| Indicador | Quien mide |
|---|---|
| Inter-city mobility | 🌐 EXTERNO — encuestas laborales |
| Regional skills match | 🌐 EXTERNO — analisis de mercado laboral |
| Income parity across cities | 🌐 EXTERNO — estadistica economica |
| Access to specialized services | 🌐 EXTERNO — GIS |
| Regional identity/cohesion | 🌐 EXTERNO — encuestas regionales |

### Economico
| Indicador | Quien mide |
|---|---|
| Regional GDP | 🌐 EXTERNO |
| Economic diversification (Herfindahl) | 🌐 EXTERNO |
| Inter-regional trade | 🌐 EXTERNO |
| Innovation ecosystems | ⚖️ MIXTO — mapeo de innovacion; la red puede aportar su propio cluster (Fab Academy, fab labs regionales) como un dato dentro del mapeo |
| Supply chain resilience | 🌐 EXTERNO |
| Circular economy maturity | 🌐 EXTERNO |

### Gobernanza
| Indicador | Quien mide |
|---|---|
| Inter-city coordination | 🌐 EXTERNO — seguimiento de partnerships institucionales |
| Regional policy alignment | 🌐 EXTERNO |
| Joint procurement | 🌐 EXTERNO |
| Regional data sharing | ⚖️ MIXTO — auditoria de plataforma de datos; fablabs.io es en si una instancia de dato abierto federado que cuenta aqui |
| Multi-stakeholder forums | ⚖️ MIXTO — mapeo de gobernanza; foros de la red Fab City pueden contar como uno de estos foros |

**Resumen Region: 0 directos / 3 mixtos / 18 externos de 21 — el lab no instrumenta esta escala, aporta a lo sumo un dato dentro de un mapeo mas amplio.**

---

## Escala 4: Bioregion — externa con una capa de conocimiento situado que SI puede aportar el lab

### Ambiental
| Indicador | Quien mide |
|---|---|
| Ecological footprint | 🌐 EXTERNO — analisis de huella |
| Biocapacity | 🌐 EXTERNO |
| Biodiversity intactness | 🌐 EXTERNO — GLOBIO o similar |
| Forest cover | 🌐 EXTERNO — monitoreo satelital |
| Soil health index | 🌐 EXTERNO — estudios de suelo |
| Water balance | 🌐 EXTERNO — modelado hidrologico |
| Water quality | ⚖️ MIXTO — estaciones de monitoreo oficiales **+ clasificacion de fotos comunitarias (turbidez del agua) que SI puede generar la comunidad/lab** |
| Native species populations | 🌐 EXTERNO — encuestas ecologicas |
| Ecosystem service value | 🌐 EXTERNO — valoracion de servicios ecosistemicos |

### Social
| Indicador | Quien mide |
|---|---|
| Bioregional identity | 🌐 EXTERNO — encuestas (aunque el lab podria aplicarlas localmente como sub-muestra) |
| Traditional knowledge preservation | ⚖️ MIXTO — evaluacion cultural; comunidades custodias (banjar adat, juntas de vecinos) son la fuente primaria, pero requiere protocolo de soberania de datos, no es un "log de lab" simple |
| Environmental education | 🔧 FAB LAB | El lab puede llevar su propio registro de participacion en educacion ambiental |
| Stewardship participation | 🔧 FAB LAB | Registro de voluntariado de programas de stewardship que el lab organiza |
| Indigenous rights recognition | 🌐 EXTERNO — evaluacion de derechos; es un acto de reconocimiento legal/institucional |

### Economico
| Indicador | Quien mide |
|---|---|
| Bioregional food self-sufficiency | 🌐 EXTERNO — analisis del sistema alimentario |
| Natural capital value | 🌐 EXTERNO — contabilidad de capital natural |
| Regenerative business growth | 🌐 EXTERNO — clasificacion de negocios |
| Payments for ecosystem services | 🌐 EXTERNO — seguimiento de programas PES |
| Green jobs | 🌐 EXTERNO — analisis de empleo |

### Gobernanza
| Indicador | Quien mide |
|---|---|
| Bioregional governance body | 🌐 EXTERNO — evaluacion institucional |
| Watershed management plans | 🌐 EXTERNO — seguimiento de planes |
| Protected area coverage | 🌐 EXTERNO — bases de datos de conservacion (WDPA) |
| Cross-jurisdictional coordination | 🌐 EXTERNO — seguimiento de acuerdos |
| Adaptive management cycles | 🌐 EXTERNO — revisiones de gestion |

**Resumen Bioregion: 2 directos / 2 mixtos / 19 externos de 23 — escala de contexto (boundary), no de
ingesta. Los unicos aportes directos del lab son educacion ambiental y stewardship que el lab mismo
organiza; todo lo demas es dato institucional o requiere protocolo de soberania que no es un simple
registro de lab.**

---

## Escala 5: Planet — 100% externa, sin excepcion

Los 22 indicadores de esta escala (GHG ppm, temperatura global, PIB mundial, SDG, finanzas climaticas,
etc.) son indicadores de contexto planetario identicos para todas las ciudades. **Ningun fab lab
instrumenta nada aqui — es la capa que viaja hacia abajo, nunca hacia arriba.**

---

## Tabla resumen — conteo total

| Escala | Total indicadores | 🔧 Directo (lab) | ⚖️ Mixto | 🌐 Externo |
|---|---|---|---|---|
| Community | 21 | **16** | 4 | 0 |
| City | 21 | 0 | 2 | 19 |
| Region | 21 | 0 | 3 | 18 |
| Bioregion | 23 | 2 | 2 | 19 |
| Planet | 22 | 0 | 0 | 22 |
| **Total** | **108*** | **18** | **11** | **79** |

*\*El conteo de la planilla original (`3_Detailed_Metrics.docx`) da 108 filas contando los encabezados
de pilar como referencia; el numero de indicadores puros listados es 95 segun el resumen del proyecto —
la diferencia es de agrupacion editorial, no de contenido.*

**La lectura honesta:** de los 95-108 indicadores que Vivanco define en la planilla teorica, solo
~18 (17%) son medibles directamente por un fab lab sin ningun insumo externo, y estan **todos
concentrados en la escala Community.** Esto confirma exactamente el patron que ya identificamos en la
matriz de 20 celdas: la red Fab City tiene soberania de dato real en una sola franja (Community), y
todo lo demas depende, en mayor o menor grado, de estadistica publica o institucional.

---

## Lo que la planilla original NO captura — el catalogo de indicadores de red

Es importante notar: el `Data_Points_Catalog` (construido despues de la planilla de Vivanco) **añade**
indicadores propios de la red que no estan en esta planilla teorica original, precisamente para
compensar este desbalance. Estos son indicadores reales, ya instrumentables, que el lab SI puede
generar y que alimentan las celdas City/Region/Bioregion con dato propio de la red en lugar de
depender solo de estadistica externa:

| Indicador añadido | Celda que alimenta | Fuente |
|---|---|---|
| fablabs.io lab roster en catchment de 50km | Economico × City | API fablabs.io |
| Fab Academy alumni density | Economico/Social × City, Region, Bioregion | Registro Fab Academy |
| Precious Plastic chapter throughput (kg procesado) | Economico × Community/City | API Precious Plastic Universe |
| Smart Citizen kit count + uptime | Ambiental × Community/City | API Smart Citizen |
| OSM craft-tag density | Economico × Community/City | Overpass API (OpenStreetMap) |
| Clasificacion de fotos comunitarias (residuos/turbidez/vegetacion) | Ambiental × Community/Bioregion | IA sobre fotos subidas por la comunidad |
| Mapeo con drones operado por el lab | Ambiental × Community | Logs de mision del lab (patron IAAC) |
| Decidim platform health | Gobernanza × City | API Decidim |
| Asistencia a conferencias FAB / GOSH desde la bioregion | Social × Bioregion | Registros de asistencia a eventos |

**Implicacion para el workshop WS3:** el mensaje central de Block 4 deberia ser exactamente este —
la planilla teorica de Vivanco describe el ideal de que se *deberia* medir en cada escala, pero el
fab lab solo tiene soberania real sobre la franja Community mas estos nueve indicadores de red
añadidos. El ejercicio practico (Block 3) ya esta construido sobre esta franja real; este documento
es el respaldo metodologico de por que se eligieron esas tres celdas y no otras.
