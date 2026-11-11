# Geoempowering Design aplicado al Río Salí: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Producir cuatro mapas del tramo urbano del Río Salí, un póster A1 a 300 ppp y una presentación de 11 diapositivas que apliquen el ensayo *Geoempowering Design* a Tucumán.

**Architecture:** Scripts de Python en cadena: descarga → procesamiento a una grilla común → funciones de análisis puras → un script por mapa. Los mapas escriben sus cifras en `salidas/cifras.json`; el póster (plantilla HTML) y la presentación (python-pptx) leen de ahí y de `contenido/textos.json`, de modo que ninguna cifra se escribe a mano dos veces.

**Tech Stack:** Python 3 (venv), geopandas, rasterio, shapely, scipy, matplotlib, matplotlib-scalebar, requests, python-pptx, Pillow, playwright (con Microsoft Edge instalado, sin descargar navegador), pytest.

**Spec:** `docs/superpowers/specs/2026-11-10-geoempowering-design-rio-sali-design.md`

## Global Constraints

- Idioma de todos los textos visibles: español.
- Sistema de referencia de trabajo: POSGAR 2007 / Argentina 3, `EPSG:5345`. Grilla ráster común de 10 m.
- Archivos finales: `PA2-Geoempowering-Design-MolinaNavarro.pptx` y `PA2-Geoempowering-Design-MolinaNavarro.jpg`.
- Póster: A1 vertical, exactamente 7016 × 9933 px, JPG color, metadato de 300 ppp.
- Rótulo del póster abajo a la derecha: "Juan Martin Molina Navarro · Sebastian Zelarayan · Juan Simon · Agustin Darelli", "4K07 Sistemas de Información Geográfica (GIS)", "2026".
- Presentación: 16:9, 11 diapositivas, en el orden del spec (sección 6.2).
- Cada mapa lleva título, leyenda, escala gráfica, norte y fuente de datos.
- Toda cifra o afirmación sobre el Salí lleva fuente citable; sin fuente no entra.
- El mapa 3 se rotula como "altura sobre el cauce (indicador topográfico)", nunca como riesgo o inundación.
- La propuesta se rotula como "ejercicio académico de geodiseño".
- Tipografía: `Segoe UI` en mapas, póster y presentación.
- Paleta única (definida en `scripts/config.py`): fondo `#F4F1EA`, tinta `#1F2A2E`, agua `#2B6C8F`, vegetación `#4F7F52`, humedal `#3FA796`, construido `#B5533C`, suelo desnudo `#D9B77E`, cultivo `#C9D48A`, acento `#E0A526`.
- Sin git: la carpeta no es un repositorio. No se hacen commits salvo que el grupo lo pida.
- Todos los comandos se corren desde `C:\Users\Juan Martin\Desktop\TFI-GIS` con `.venv/Scripts/python`.
- Fuera de alcance: demo interactiva, modelación hidráulica, multicriterio ponderado, ArcGIS/QGIS, campo.

## Review Focus

1. **Descarga cortada o servicio caído:** no debe quedar un archivo corrupto que el paso siguiente tome por bueno; se espera un error claro con el nombre de la fuente. Prueba en Task 2.
2. **Río en varios tramos o con nombre distinto en OSM** ("Río Salí", "Rio Sali", segmentos sueltos): se espera una sola traza continua dentro del área. Prueba en Task 3.
3. **Píxeles sin dato en cobertura o elevación:** los porcentajes se calculan sobre píxeles válidos y suman 100. Prueba en Task 4.
4. **Umbral que no deja ninguna celda candidata a humedal:** las hectáreas dan 0.0 y el mapa 4 se genera igual. Prueba en Task 4.
5. **Cifra distinta entre mapa, póster y presentación, o marcador sin reemplazar:** póster y presentación leen de `cifras.json` y no puede quedar ningún `{{...}}` en el póster. Pruebas en Tasks 10 y 11.

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `requirements.txt` | Dependencias |
| `scripts/config.py` | Rutas, área de estudio, umbrales, paleta, integrantes, nombres de teselas |
| `scripts/descargar.py` | Bajar datos crudos a `datos/crudos/` |
| `scripts/procesar.py` | Recortar, reproyectar y alinear a `datos/procesados/` |
| `scripts/analisis.py` | Funciones puras sobre arreglos: porcentajes, altura sobre cauce, zonificación, hectáreas |
| `scripts/estilo.py` | Marco común de los mapas |
| `scripts/mapa1_contexto.py` … `mapa4_propuesta.py` | Un mapa cada uno |
| `scripts/esquema_infra.py` | Esquema propio "hormigón vs humedal en terrazas" |
| `scripts/exportar_poster.py` | Rellenar plantilla y exportar el JPG |
| `contenido/textos.json` | Textos del ensayo, paralelo, datos del Salí con fuente |
| `poster/poster.html`, `poster/poster.css` | Plantilla del póster |
| `presentacion/crear_pptx.py` | Generar el `.pptx` |
| `salidas/cifras.json` | Cifras calculadas por los mapas 2 y 4 |
| `tests/` | Pruebas con pytest |

---

### Task 1: Entorno y configuración

**Files:**
- Create: `requirements.txt`, `scripts/__init__.py`, `scripts/config.py`, `tests/__init__.py`, `tests/test_config.py`

**Interfaces:**
- Produces (en `scripts/config.py`):
  - `RAIZ: Path`, `CRUDOS`, `PROCESADOS`, `MAPAS`, `SALIDAS`, `CIFRAS` (`salidas/cifras.json`), `GPKG` (`datos/procesados/sali.gpkg`)
  - `CRS_PROY = "EPSG:5345"`, `PIXEL_M = 10`
  - `AOI_BBOX = (-65.25, -26.93, -65.12, -26.74)` (oeste, sur, este, norte; valor inicial, se revisa en Task 3)
  - `FRANJA_M = 500`, `UMBRAL_BAJO_M = 3.0`, `ANCHO_BOSQUE_M = 100`, `ACCESO_DIST_M = 150`, `ACCESO_SEPARACION_M = 500` (valores iniciales, se revisan en Task 3)
  - `PUNTO_CIERRE_CUENCA = (-64.887, -27.522)` (dique de Río Hondo)
  - `PALETA: dict[str, str]` con las claves `fondo, tinta, agua, vegetacion, humedal, construido, desnudo, cultivo, acento`
  - `FUENTE = "Segoe UI"`, `INTEGRANTES: list[str]`, `MATERIA`, `ANIO = "2026"`, `NOMBRE_BASE = "PA2-Geoempowering-Design-MolinaNavarro"`
  - `CLASES_WC: dict[str, tuple[int, ...]]` = `{"vegetacion": (10, 20, 30, 90), "cultivo": (40,), "construido": (50,), "desnudo": (60,), "agua": (80,)}`
  - `teselas_worldcover(bbox) -> list[str]`: nombres tipo `S27W066` (teselas de 3°, esquina sudoeste, múltiplos de 3)
  - `teselas_dem(bbox) -> list[str]`: nombres tipo `S27_00_W066_00` (teselas de 1°, esquina sudoeste)

- [ ] **Step 1:** Crear el entorno: `python -m venv .venv`. Escribir `requirements.txt` con geopandas, rasterio, shapely, scipy, matplotlib, matplotlib-scalebar, requests, python-pptx, Pillow, playwright, pytest. Instalar con `.venv/Scripts/python -m pip install -r requirements.txt`. Si alguna no instala en Python 3.14, recrear el venv con Python 3.12 (`py -3.12 -m venv .venv`; instalar 3.12 con `winget install Python.Python.3.12` solo con el visto bueno del usuario).
- [ ] **Step 2:** Verificar: `.venv/Scripts/python -c "import geopandas, rasterio, scipy, pptx, playwright; print('ok')"` imprime `ok`.
- [ ] **Step 3:** Escribir las pruebas que fallan en `tests/test_config.py`:

```python
from scripts import config

def test_teselas_worldcover_aoi():
    assert config.teselas_worldcover(config.AOI_BBOX) == ["S27W066"]

def test_teselas_worldcover_cruza_paralelo_27():
    assert config.teselas_worldcover((-65.5, -27.5, -65.0, -26.5)) == ["S27W066", "S30W066"]

def test_teselas_dem_aoi():
    assert config.teselas_dem(config.AOI_BBOX) == ["S27_00_W066_00"]

def test_teselas_dem_cruza_meridiano_65():
    assert config.teselas_dem((-65.1, -26.9, -64.9, -26.8)) == ["S27_00_W065_00", "S27_00_W066_00"]

def test_paleta_completa():
    assert set(config.PALETA) == {"fondo", "tinta", "agua", "vegetacion", "humedal",
                                  "construido", "desnudo", "cultivo", "acento"}
```

- [ ] **Step 4:** Correr `.venv/Scripts/python -m pytest tests/test_config.py -v`. Esperado: FAIL (módulo inexistente).
- [ ] **Step 5:** Implementar `scripts/config.py` con todo lo listado en Interfaces. Las listas de teselas se devuelven ordenadas alfabéticamente.
- [ ] **Step 6:** Correr las pruebas. Esperado: 5 passed.

---

### Task 2: Descarga de datos

**Files:**
- Create: `scripts/descargar.py`, `tests/test_descargar.py`

**Interfaces:**
- Consumes: `config.CRUDOS`, `config.AOI_BBOX`, `config.teselas_worldcover`, `config.teselas_dem`
- Produces:
  - `bajar(url: str, destino: Path, minimo_bytes: int = 1024) -> Path`: descarga a `destino.with_suffix(destino.suffix + ".part")` y renombra al terminar; si `destino` ya existe no vuelve a bajar; si la respuesta no es 200 o pesa menos que `minimo_bytes`, borra el `.part` y lanza `RuntimeError` con la URL.
  - `main()`: deja en `datos/crudos/`:
    - `provincia.geojson`, `departamentos.geojson`, `hidro_ign.geojson` (IGN, recortados a Tucumán)
    - `osm_rio.geojson` (vías de agua `waterway=river` cuyo nombre contenga "Sal" dentro del AOI ampliado 0.1°), `osm_vias.geojson` (`highway` en `primary, secondary, tertiary, residential` dentro del AOI)
    - `worldcover_<tesela>.tif` solo para el AOI ampliado (lectura por ventana del COG remoto), y `worldcover_prov_100m.tif` (provincia remuestreada a 100 m, modo)
    - `dem_<tesela>.tif` para el AOI ampliado
    - `hybas_sa_lev07.gpkg` (HydroBASINS Sudamérica nivel 7)
    - `FUENTES.md` con URL y fecha de descarga de cada archivo

Fuentes y URL:

| Dato | URL |
|---|---|
| IGN (WFS) | `https://wms.ign.gob.ar/geoserver/ign/ows` con `typeName` `ign:provincia`, `ign:departamento`, `ign:lineas_de_aguas_continentales_perenne`, `outputFormat=application/json` |
| OSM | Overpass: `https://overpass-api.de/api/interpreter` |
| WorldCover 2021 v200 | `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_<tesela>_Map.tif` |
| Copernicus GLO-30 | `https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_<tesela>_DEM/Copernicus_DSM_COG_10_<tesela>_DEM.tif` |
| HydroBASINS | `https://data.hydrosheds.org/file/hydrobasins/standard/hybas_sa_lev07_v1c.zip` |

Los nombres de capa del IGN y la URL de HydroBASINS se confirman antes de codificar (GetCapabilities del WFS; página de descargas de HydroSHEDS). Si alguno difiere, se usa el equivalente y se anota en `FUENTES.md`. No se envían datos personales ni correo en cabeceras; `User-Agent: tfi-gis-academico`.

- [ ] **Step 1:** Escribir pruebas que fallan en `tests/test_descargar.py`, usando `monkeypatch` sobre `requests.get` con una respuesta falsa:

```python
def test_bajar_respuesta_chica_no_deja_archivo(tmp_path, monkeypatch):
    # respuesta 200 con 10 bytes
    with pytest.raises(RuntimeError, match="http://x/y.tif"):
        descargar.bajar("http://x/y.tif", tmp_path / "y.tif")
    assert list(tmp_path.iterdir()) == []

def test_bajar_error_http_no_deja_archivo(tmp_path, monkeypatch):
    # respuesta 503
    with pytest.raises(RuntimeError):
        descargar.bajar("http://x/y.tif", tmp_path / "y.tif")
    assert list(tmp_path.iterdir()) == []

def test_bajar_no_repite_si_existe(tmp_path, monkeypatch):
    # destino ya existe con 2000 bytes; requests.get lanza si se lo llama
    assert descargar.bajar("http://x/y.tif", tmp_path / "y.tif") == tmp_path / "y.tif"
```

- [ ] **Step 2:** Correr `pytest tests/test_descargar.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar `bajar` y `main` en `scripts/descargar.py`.
- [ ] **Step 4:** Correr las pruebas. Esperado: 3 passed.
- [ ] **Step 5:** Correr `.venv/Scripts/python -m scripts.descargar`. Esperado: termina sin error y `datos/crudos/` contiene todos los archivos listados, ninguno `.part`. Si un servicio no responde tras tres intentos, usar una fuente equivalente (spec, sección 10) y registrarla.

---

### Task 3: Procesamiento y definición del área de estudio

**Files:**
- Create: `scripts/procesar.py`, `tests/test_procesar.py`
- Modify: `scripts/config.py` (valores definitivos de `AOI_BBOX`, `FRANJA_M`, `UMBRAL_BAJO_M`)

**Interfaces:**
- Consumes: archivos de Task 2, constantes de `config`
- Produces:
  - `unir_rio(gdf: GeoDataFrame) -> LineString | MultiLineString`: filtra por nombre normalizado (sin tildes, minúsculas) que contenga `"sali"` y une los tramos con `shapely.ops.linemerge`.
  - `cuenca_aguas_arriba(hybas: GeoDataFrame, punto: tuple[float, float]) -> GeoDataFrame`: subcuencas que drenan a la que contiene `punto`, recorriendo `NEXT_DOWN`.
  - `main()`: escribe en `datos/procesados/`:
    - `sali.gpkg` con capas `rio`, `franja` (buffer de `FRANJA_M` del río dentro del AOI), `aoi`, `provincia`, `departamentos`, `hidro`, `cuenca`, `vias`, todas en `EPSG:5345`
    - `cobertura.tif` (uint8, 10 m, nodata 0), `dem.tif` (float32, remuestreo bilineal a la misma grilla de 10 m, nodata -9999), `urbano_prov.tif`
    - `salidas/vista_previa_aoi.png`: cobertura con río, franja y AOI encima

- [ ] **Step 1:** Escribir pruebas que fallan en `tests/test_procesar.py`:

```python
def test_unir_rio_normaliza_nombre_y_une_tramos():
    gdf = gpd.GeoDataFrame(
        {"name": ["Río Salí", "Rio Sali", "Arroyo Otro"]},
        geometry=[LineString([(0, 0), (0, 1)]), LineString([(0, 1), (0, 2)]),
                  LineString([(5, 5), (6, 6)])], crs="EPSG:5345")
    linea = procesar.unir_rio(gdf)
    assert linea.geom_type == "LineString"
    assert linea.length == 2

def test_cuenca_aguas_arriba_recorre_next_down():
    # cuatro cuadrados: 1 -> 2 -> 3 (cierre), 4 -> 0 (otra cuenca); punto dentro del 3
    assert set(procesar.cuenca_aguas_arriba(hybas, punto)["HYBAS_ID"]) == {1, 2, 3}
```

- [ ] **Step 2:** Correr `pytest tests/test_procesar.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar `scripts/procesar.py`.
- [ ] **Step 4:** Correr las pruebas. Esperado: 2 passed.
- [ ] **Step 5:** Correr `.venv/Scripts/python -m scripts.procesar`. Verificar con un script corto que `cobertura.tif` y `dem.tif` tienen igual forma, transformación y CRS, y que la capa `rio` tiene una sola geometría que cruza el AOI de norte a sur.
- [ ] **Step 6:** Mirar `salidas/vista_previa_aoi.png`. Ajustar `AOI_BBOX` y `FRANJA_M` en `config.py` para que el tramo cubra el frente urbano completo y la franja incluya la planicie visible; calcular el percentil 25 de la altura sobre el cauce dentro de la franja (tras Task 4) como referencia para `UMBRAL_BAJO_M`.
- [ ] **Step 7: Punto de control con el usuario.** Mostrar la vista previa y los valores propuestos de tramo, franja y umbral. Esperar aprobación antes de seguir con los mapas 2 a 4.

---

### Task 4: Funciones de análisis

**Files:**
- Create: `scripts/analisis.py`, `tests/test_analisis.py`

**Interfaces:**
- Consumes: `config.CLASES_WC`
- Produces:
  - `porcentajes_cobertura(cob: np.ndarray, mascara: np.ndarray) -> dict[str, float]`: claves de `CLASES_WC`; porcentaje sobre los píxeles de `mascara` con valor distinto de 0; redondeo a 1 decimal; si no hay píxeles válidos devuelve todo `0.0`.
  - `distancia_y_altura(dem: np.ndarray, rio: np.ndarray, pixel_m: float, nodata: float = -9999) -> tuple[np.ndarray, np.ndarray]`: para cada celda, distancia en metros a la celda de río más cercana y `dem - dem[celda de río más cercana]` (usar `scipy.ndimage.distance_transform_edt(~rio, return_indices=True)`); donde `dem` es nodata, la altura es `np.nan`.
  - `zonificar(cob, altura, distancia, franja, umbral_bajo_m, ancho_bosque_m) -> np.ndarray` (uint8): `1` humedal = dentro de `franja`, `altura <= umbral_bajo_m`, cobertura que no sea 50 ni 80 ni 0; `2` bosque de ribera = dentro de `franja`, `distancia <= ancho_bosque_m`, cobertura 60 o 30, y no humedal; `0` el resto.
  - `hectareas_por_zona(zonas: np.ndarray, pixel_m: float) -> dict[str, float]`: claves `humedal`, `bosque`; 1 decimal.

- [ ] **Step 1:** Escribir las pruebas que fallan:

```python
def test_porcentajes_ignoran_nodata_y_suman_100():
    cob = np.array([[10, 50, 0], [80, 60, 40]], dtype=np.uint8)
    p = analisis.porcentajes_cobertura(cob, np.ones_like(cob, dtype=bool))
    assert p == {"vegetacion": 20.0, "cultivo": 20.0, "construido": 20.0,
                 "desnudo": 20.0, "agua": 20.0}

def test_porcentajes_sin_pixeles_validos():
    cob = np.zeros((2, 2), dtype=np.uint8)
    assert set(analisis.porcentajes_cobertura(cob, np.ones((2, 2), bool)).values()) == {0.0}

def test_distancia_y_altura():
    dem = np.array([[105., 100., 103.], [106., 101., -9999.]], dtype=np.float32)
    rio = np.array([[False, True, False], [False, True, False]])
    dist, alt = analisis.distancia_y_altura(dem, rio, 10)
    assert dist[0].tolist() == [10.0, 0.0, 10.0]
    assert alt[0].tolist() == [5.0, 0.0, 3.0]
    assert alt[1, 0] == 5.0 and np.isnan(alt[1, 2])

def test_zonificar_reglas():
    cob       = np.array([[30, 50, 60, 30, 10]], dtype=np.uint8)
    altura    = np.array([[1.0, 1.0, 8.0, 8.0, 8.0]])
    distancia = np.array([[20., 20., 50., 300., 50.]])
    franja    = np.ones((1, 5), bool)
    z = analisis.zonificar(cob, altura, distancia, franja, 3.0, 100)
    assert z.tolist() == [[1, 0, 2, 0, 0]]

def test_zonificar_fuera_de_franja_es_cero():
    z = analisis.zonificar(np.array([[30]], np.uint8), np.array([[1.0]]),
                           np.array([[10.]]), np.zeros((1, 1), bool), 3.0, 100)
    assert z.tolist() == [[0]]

def test_hectareas_sin_candidatos():
    assert analisis.hectareas_por_zona(np.zeros((10, 10), np.uint8), 10) == {"humedal": 0.0, "bosque": 0.0}

def test_hectareas():
    z = np.zeros((10, 10), np.uint8); z[0] = 1; z[1, :5] = 2
    assert analisis.hectareas_por_zona(z, 100) == {"humedal": 10.0, "bosque": 5.0}
```

- [ ] **Step 2:** Correr `pytest tests/test_analisis.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar las cuatro funciones en `scripts/analisis.py`.
- [ ] **Step 4:** Correr las pruebas. Esperado: 7 passed.

---

### Task 5: Marco común y mapa 1 (contexto)

**Files:**
- Create: `scripts/estilo.py`, `scripts/mapa1_contexto.py`, `tests/test_estilo.py`

**Interfaces:**
- Consumes: `config`, capas `provincia`, `departamentos`, `hidro`, `cuenca`, `aoi`, `rio` de `sali.gpkg`, `urbano_prov.tif`
- Produces (en `scripts/estilo.py`):
  - `nuevo_mapa(pregunta: str, titulo: str, lado_in: float = 10) -> tuple[Figure, Axes]`: figura cuadrada, fondo `PALETA["fondo"]`, `pregunta` como título principal y `titulo` como subtítulo, tipografía `FUENTE`, ejes sin marcas.
  - `terminar_mapa(fig, ax, fuente: str, ruta: Path) -> Path`: agrega escala gráfica en km o m (matplotlib-scalebar, `dx=1` porque el CRS está en metros), flecha de norte arriba a la derecha, texto de fuente abajo a la izquierda, y guarda PNG a 300 ppp.
  - `leyenda(ax, items: list[tuple[str, str]])`: lista de `(etiqueta, color)`.
- Produce `salidas/mapas/mapa1_contexto.png` (3000 × 3000 px).

Contenido del mapa 1: pregunta "¿Cómo es el territorio?"; provincia con departamentos en línea fina; cuenca Salí-Dulce recortada a la provincia en tono suave de `agua`; red hídrica; el Salí resaltado; manchas urbanas en `construido`; recuadro del área de estudio en `acento` con etiqueta; etiquetas "San Miguel de Tucumán" y "Embalse de Río Hondo" si entra en el encuadre. Fuente: "IGN, OpenStreetMap, HydroBASINS, ESA WorldCover 2021".

- [ ] **Step 1:** Escribir la prueba que falla:

```python
def test_terminar_mapa_guarda_png_300ppp(tmp_path):
    fig, ax = estilo.nuevo_mapa("¿Pregunta?", "Título")
    ax.plot([0, 1000], [0, 1000])
    ruta = estilo.terminar_mapa(fig, ax, "Fuente: prueba", tmp_path / "m.png")
    im = Image.open(ruta)
    assert im.size == (3000, 3000)
    assert round(im.info["dpi"][0]) == 300
```

- [ ] **Step 2:** Correr `pytest tests/test_estilo.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar `scripts/estilo.py`. No usar `bbox_inches="tight"` (cambia el tamaño final).
- [ ] **Step 4:** Correr la prueba. Esperado: PASS.
- [ ] **Step 5:** Implementar `scripts/mapa1_contexto.py` con `main()` y correr `.venv/Scripts/python -m scripts.mapa1_contexto`.
- [ ] **Step 6:** Abrir el PNG con la herramienta de lectura de imágenes y revisar: nada cortado, etiquetas legibles, leyenda sin tapar el mapa, escala y norte presentes. Corregir y repetir hasta que esté bien.
- [ ] **Step 7: Punto de control con el usuario:** mostrar el mapa 1 y aplicar ajustes.

---

### Task 6: Mapa 2 (estado de la ribera)

**Files:**
- Create: `scripts/mapa2_ribera.py`, `scripts/cifras.py`, `tests/test_cifras.py`

**Interfaces:**
- Consumes: `analisis.porcentajes_cobertura`, `estilo.*`, `cobertura.tif`, capas `rio`, `franja`, `aoi`
- Produces:
  - `scripts/cifras.py`: `guardar(seccion: str, datos: dict) -> None` (fusiona en `salidas/cifras.json` sin borrar otras secciones) y `leer() -> dict`.
  - `salidas/cifras.json` con la sección `"ribera"`: `{"vegetacion": float, "cultivo": float, "construido": float, "desnudo": float, "agua": float, "franja_m": int, "largo_km": float}`
  - `salidas/mapas/mapa2_ribera.png`

Contenido del mapa 2: pregunta "¿Funciona bien?"; cobertura coloreada con la paleta dentro del AOI, atenuada fuera de la franja; contorno de la franja; río; una barra apilada horizontal con los porcentajes de la franja bajo el mapa. Fuente: "ESA WorldCover 2021 (10 m), OpenStreetMap".

- [ ] **Step 1:** Escribir la prueba que falla:

```python
def test_guardar_fusiona_secciones(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CIFRAS", tmp_path / "cifras.json")
    cifras.guardar("ribera", {"vegetacion": 40.0})
    cifras.guardar("propuesta", {"humedal": 12.5})
    assert cifras.leer() == {"ribera": {"vegetacion": 40.0}, "propuesta": {"humedal": 12.5}}
```

- [ ] **Step 2:** Correr `pytest tests/test_cifras.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar `scripts/cifras.py`. Correr la prueba. Esperado: PASS.
- [ ] **Step 4:** Implementar `scripts/mapa2_ribera.py` y correr `.venv/Scripts/python -m scripts.mapa2_ribera`.
- [ ] **Step 5:** Verificar que los cinco porcentajes de `cifras.json` suman entre 99.8 y 100.2.
- [ ] **Step 6:** Revisar el PNG. Comparar la cobertura con una imagen satelital del tramo: si la ribera está visiblemente mal clasificada, aplicar la alternativa del spec (clasificar Sentinel-2) antes de seguir, avisando al usuario.
- [ ] **Step 7: Punto de control con el usuario:** mostrar el mapa 2.

---

### Task 7: Mapa 3 (altura sobre el cauce)

**Files:**
- Create: `scripts/mapa3_altura.py`
- Modify: `scripts/procesar.py` (agregar la escritura de `altura_cauce.tif` y `distancia_cauce.tif`)

**Interfaces:**
- Consumes: `analisis.distancia_y_altura`, `dem.tif`, capa `rio` rasterizada a la grilla común (`rasterio.features.rasterize`, `all_touched=True`)
- Produces: `datos/procesados/altura_cauce.tif`, `datos/procesados/distancia_cauce.tif` (float32, misma grilla), `salidas/mapas/mapa3_altura.png`

Contenido del mapa 3: pregunta "¿Cómo funciona el agua?"; subtítulo "Altura del terreno sobre el cauce (indicador topográfico)"; altura en clases 0–1, 1–2, 2–3, 3–5, 5–10, más de 10 m, en rampa de `agua` a `fondo`; sombreado de relieve tenue debajo; río y franja encima; nota al pie: "No es un modelo hidráulico de inundación". Fuente: "Copernicus DEM GLO-30, OpenStreetMap".

- [ ] **Step 1:** Agregar a `procesar.main()` el cálculo y la escritura de los dos rásters. Correr `.venv/Scripts/python -m scripts.procesar`.
- [ ] **Step 2:** Verificar: la altura sobre las celdas de río es 0; la mediana dentro de la franja es mayor o igual a 0 y menor que 30 m. Si la mediana es negativa o el río aparece "elevado", el DEM no resuelve el cauce: tomar como cota del río el mínimo del DEM en una ventana de 50 m alrededor de cada celda de la traza y repetir.
- [ ] **Step 3:** Implementar `scripts/mapa3_altura.py` y correrlo.
- [ ] **Step 4:** Revisar el PNG: las zonas bajas deben seguir la planicie del río y no mostrar bandas rectas (artefacto de tesela).
- [ ] **Step 5: Punto de control con el usuario:** mostrar el mapa 3 y confirmar `UMBRAL_BAJO_M`.

---

### Task 8: Mapa 4 (propuesta de corredor)

**Files:**
- Create: `scripts/mapa4_propuesta.py`, `tests/test_accesos.py`
- Modify: `scripts/analisis.py` (agregar `puntos_de_acceso`)

**Interfaces:**
- Consumes: `analisis.zonificar`, `analisis.hectareas_por_zona`, `cifras.guardar`, `cobertura.tif`, `altura_cauce.tif`, `distancia_cauce.tif`, capas `rio`, `franja`, `vias`
- Produces:
  - `analisis.puntos_de_acceso(vias: GeoSeries, rio: BaseGeometry, dist_m: float, separacion_m: float) -> list[Point]`: intersecciones de `vias` con el borde de `rio.buffer(dist_m)`, ordenadas por posición a lo largo del río (`rio.project`), descartando las que estén a menos de `separacion_m` (medida a lo largo del río) de una ya aceptada en la misma margen.
  - `datos/procesados/zonas.tif` y capas `zonas` (polígonos) y `accesos` (puntos) en `sali.gpkg`
  - sección `"propuesta"` en `cifras.json`: `{"humedal": float, "bosque": float, "accesos": int, "umbral_bajo_m": float, "ancho_bosque_m": int}`
  - `salidas/mapas/mapa4_propuesta.png` (4800 × 4800 px, `lado_in=16`)

Contenido del mapa 4: pregunta "¿Cómo podría cambiar?"; subtítulo "Corredor ecológico del Salí: ejercicio académico de geodiseño"; base de cobertura muy atenuada con vías en gris; humedales en `humedal`, bosque de ribera en `vegetacion`, accesos como puntos en `acento`; río en `agua`; leyenda con hectáreas de cada zona y la regla usada en una línea ("Humedal: terreno a ≤ N m sobre el cauce, sin edificar"). Fuente: "Elaboración propia sobre ESA WorldCover, Copernicus DEM y OpenStreetMap".

- [ ] **Step 1:** Escribir la prueba que falla:

```python
def test_puntos_de_acceso_separa_por_distancia():
    rio = LineString([(0, 0), (0, 2000)])
    vias = gpd.GeoSeries([LineString([(-500, y), (-10, y)]) for y in (100, 300, 900)])
    pts = analisis.puntos_de_acceso(vias, rio, dist_m=150, separacion_m=500)
    assert [round(p.y) for p in pts] == [100, 900]
    assert all(round(p.x) == -150 for p in pts)
```

- [ ] **Step 2:** Correr `pytest tests/test_accesos.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar `puntos_de_acceso`. Correr la prueba. Esperado: PASS.
- [ ] **Step 4:** Implementar `scripts/mapa4_propuesta.py` y correrlo. Eliminar del ráster de zonas los parches menores a 0.5 ha antes de vectorizar y de calcular hectáreas.
- [ ] **Step 5:** Verificar que el script termina y produce el PNG también cuando `UMBRAL_BAJO_M` se fuerza a `-1` por variable de entorno `UMBRAL_BAJO_M` (sin humedales): hectáreas `0.0` y mapa generado. Restaurar el valor.
- [ ] **Step 6:** Revisar el PNG: los humedales no deben caer sobre zonas edificadas ni sobre el cauce.
- [ ] **Step 7: Punto de control con el usuario:** mostrar el mapa 4 con sus cifras. Si piden cambiar umbrales, cambiar `config.py` y volver a correr Tasks 7 (paso 1) y 8.

---

### Task 9: Contenido con fuentes y esquema

**Files:**
- Create: `contenido/textos.json`, `scripts/esquema_infra.py`, `tests/test_contenido.py`

**Interfaces:**
- Produces:
  - `contenido/textos.json` con las claves:
    - `titulo`: "Geoempowering Design", `subtitulo`: "Geodiseño para el Río Salí, Tucumán"
    - `ensayo`: lista de 4 objetos `{"idea": str, "texto": str}` (geodiseño; GIS como plataforma; infraestructura ecológica; biomímesis), redactados con palabras propias a partir de la sección 4 del spec, cada `texto` de 35 palabras como máximo
    - `cita`: una sola cita textual del ensayo de menos de 15 palabras, con autor
    - `shuicheng`: lista de 3 frases
    - `paralelo`: lista de 3 objetos `{"shuicheng": str, "sali": str}`
    - `datos_sali`: lista de 3 a 5 objetos `{"texto": str, "fuente": str, "url": str}`
    - `limites`: las 3 frases de la sección 5.4 del spec
    - `aporte_gis`: lista de 3 frases
    - `preguntas_previsibles`: lista de 6 objetos `{"pregunta": str, "respuesta": str}`
    - `referencias`: lista de strings (ensayo, fuentes de datos, fuentes de `datos_sali`)
  - `salidas/mapas/esquema_infra.png` (3000 × 1500 px): dos cortes transversales lado a lado, "Río canalizado: hormigón" y "Infraestructura ecológica: humedales en terrazas", dibujados con matplotlib en la paleta común.

- [ ] **Step 1:** Escribir las pruebas que fallan:

```python
def test_datos_sali_tienen_fuente():
    t = json.loads(Path("contenido/textos.json").read_text(encoding="utf-8"))
    assert 3 <= len(t["datos_sali"]) <= 5
    for d in t["datos_sali"]:
        assert d["fuente"].strip() and d["url"].startswith("http")

def test_estructura_textos():
    t = json.loads(Path("contenido/textos.json").read_text(encoding="utf-8"))
    assert len(t["ensayo"]) == 4 and len(t["paralelo"]) == 3 and len(t["limites"]) == 3
    assert all(len(e["texto"].split()) <= 35 for e in t["ensayo"])
    assert len(t["cita"]["texto"].split()) < 15
    assert len(t["preguntas_previsibles"]) == 6
```

- [ ] **Step 2:** Correr `pytest tests/test_contenido.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Investigar en la web los datos del Salí (estado ambiental del río y de la cuenca Salí-Dulce, fuentes de vertido, efectos en el embalse de Río Hondo, acciones del Comité de Cuenca). Priorizar organismos públicos y publicaciones académicas. Abrir cada fuente y confirmar que dice lo que se le atribuye antes de anotarla.
- [ ] **Step 4:** Escribir `contenido/textos.json`. Las preguntas previsibles incluyen al menos: por qué no es un mapa de inundación, de dónde salen los umbrales, qué diferencia hay entre GIS y geodiseño, y qué haría falta para pasar a un proyecto real.
- [ ] **Step 5:** Correr las pruebas. Esperado: 2 passed.
- [ ] **Step 6:** Implementar y correr `scripts/esquema_infra.py`; revisar el PNG.
- [ ] **Step 7: Punto de control con el usuario:** mostrar los `datos_sali` con sus fuentes para que el grupo los valide.

---

### Task 10: Póster

**Files:**
- Create: `poster/poster.html`, `poster/poster.css`, `scripts/exportar_poster.py`, `tests/test_poster.py`

**Interfaces:**
- Consumes: `contenido/textos.json`, `cifras.leer()`, los cuatro mapas y el esquema, `config.INTEGRANTES`, `MATERIA`, `ANIO`, `NOMBRE_BASE`, `PALETA`
- Produces:
  - `rellenar(plantilla: str, valores: dict[str, str]) -> str`: reemplaza `{{clave}}`; lanza `KeyError` con el nombre si queda algún `{{...}}` sin valor.
  - `valores_poster() -> dict[str, str]`: aplana textos y cifras a claves simples (por ejemplo `ribera_vegetacion`, `propuesta_humedal`, `integrantes`).
  - `exportar(html: Path, destino: Path) -> Path`: abre el HTML con playwright (`chromium.launch(channel="msedge")`, viewport 1754 × 2483, `device_scale_factor=4`), captura la página, ajusta a 7016 × 9933 con Pillow (LANCZOS) y guarda JPG calidad 92 con `dpi=(300, 300)`.
  - `poster/PA2-Geoempowering-Design-MolinaNavarro.jpg`

Diseño (página de 1754 × 2483 px CSS, grilla de 12 columnas, margen de 60 px):

| Zona | Alto aprox. | Contenido |
|---|---|---|
| Franja de título | 12 % | `titulo`, `subtitulo`, la `cita` |
| Idea del ensayo | 18 % | Las 4 ideas en 4 columnas, con el esquema hormigón/humedal |
| Pieza central | 40 % | Mapa 4 a 8 columnas; a su derecha, en 4 columnas, las hectáreas en cifra grande y la regla de la propuesta |
| Diagnóstico | 20 % | Mapas 1, 2 y 3 en tres columnas, cada uno con su pregunta y una cifra o frase |
| Pie | 10 % | A la izquierda: `limites` y `referencias` en cuerpo chico. A la derecha: rótulo con integrantes, materia y año |

Tamaños mínimos en px CSS (el póster se lee a un metro): título 110, subtítulo 48, encabezados 34, cuerpo 22, pie 16. Fondo `fondo`, texto `tinta`, un solo color de acento.

- [ ] **Step 1:** Escribir las pruebas que fallan:

```python
def test_rellenar_falla_si_queda_marcador():
    with pytest.raises(KeyError, match="falta"):
        exportar_poster.rellenar("<p>{{ok}} {{falta}}</p>", {"ok": "1"})

def test_plantilla_completa_sin_marcadores():
    html = exportar_poster.rellenar(Path("poster/poster.html").read_text(encoding="utf-8"),
                                    exportar_poster.valores_poster())
    assert "{{" not in html
    for nombre in config.INTEGRANTES:
        assert nombre in html

def test_poster_final_dimensiones():
    im = Image.open(Path("poster") / f"{config.NOMBRE_BASE}.jpg")
    assert im.size == (7016, 9933)
    assert im.mode == "RGB"
    assert round(im.info["dpi"][0]) == 300
```

- [ ] **Step 2:** Correr `pytest tests/test_poster.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Escribir `poster/poster.html` y `poster/poster.css` según la tabla de diseño; implementar `scripts/exportar_poster.py`.
- [ ] **Step 4:** Correr `.venv/Scripts/python -m scripts.exportar_poster` y luego las pruebas. Esperado: 3 passed.
- [ ] **Step 5:** Revisar el póster: abrir una versión reducida completa (1754 px de ancho) para el equilibrio general, y recortes al 100 % de cada zona para la nitidez de texto y mapas. Chequear que nada desborde, que el rótulo esté abajo a la derecha y que las cifras coincidan con `cifras.json`.
- [ ] **Step 6: Punto de control con el usuario (16/11):** mostrar el póster y aplicar los ajustes del grupo. El 17/11 queda para imprimir.

---

### Task 11: Presentación

**Files:**
- Create: `presentacion/crear_pptx.py`, `tests/test_pptx.py`

**Interfaces:**
- Consumes: `contenido/textos.json`, `cifras.leer()`, mapas, esquema, `config`
- Produces: `presentacion/PA2-Geoempowering-Design-MolinaNavarro.pptx`

Diapositivas (13.333 × 7.5 in, fondo `fondo`, tipografía `Segoe UI`, título de 36 pt mínimo, cuerpo de 20 pt mínimo, 30 palabras como máximo de cuerpo por diapositiva):

| # | Título | Contenido | Minutos |
|---|---|---|---|
| 1 | Geoempowering Design | Subtítulo, integrantes, materia, año | 0:20 |
| 2 | ¿Qué es el geodiseño? | Idea 1 y la cita | 1:00 |
| 3 | Infraestructura ecológica, no hormigón | Esquema a pantalla completa | 1:00 |
| 4 | Kongjian Yu y el río Shuicheng | 3 frases; espacio reservado para una foto que el grupo agregue con su crédito | 0:40 |
| 5 | Del Shuicheng al Salí | Tabla de paralelo y un dato del Salí con su fuente | 1:00 |
| 6 | ¿Cómo es el territorio? | Mapa 1 | 1:00 |
| 7 | ¿Funciona bien? | Mapa 2 y el porcentaje de vegetación en cifra grande | 1:15 |
| 8 | ¿Cómo funciona el agua? | Mapa 3 y la aclaración de que no es modelo hidráulico | 1:15 |
| 9 | ¿Cómo podría cambiar? | Mapa 4 y hectáreas | 1:30 |
| 10 | Qué aporta el GIS, y sus límites | `aporte_gis` y `limites` en dos columnas | 0:45 |
| 11 | Fuentes | `referencias` | 0:15 |

Notas del orador: en cada diapositiva, el guion de lo que se dice en ese tiempo; en la 10, además, las 6 preguntas previsibles con sus respuestas.

- [ ] **Step 1:** Escribir las pruebas que fallan:

```python
RUTA = Path("presentacion") / f"{config.NOMBRE_BASE}.pptx"

def test_once_diapositivas_16_9_con_notas():
    p = Presentation(RUTA)
    assert len(p.slides) == 11
    assert round(p.slide_width / p.slide_height, 3) == round(16 / 9, 3)
    assert all(s.notes_slide.notes_text_frame.text.strip() for s in p.slides)

def test_mapas_en_diapositivas_6_a_9():
    p = Presentation(RUTA)
    for i in (5, 6, 7, 8):
        assert any(sh.shape_type == MSO_SHAPE_TYPE.PICTURE for sh in p.slides[i].shapes)

def test_cifras_salen_de_cifras_json():
    c = cifras.leer()
    texto = lambda s: " ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
    p = Presentation(RUTA)
    assert str(c["ribera"]["vegetacion"]).replace(".", ",") in texto(p.slides[6])
    assert str(c["propuesta"]["humedal"]).replace(".", ",") in texto(p.slides[8])
```

- [ ] **Step 2:** Correr `pytest tests/test_pptx.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Implementar `presentacion/crear_pptx.py` (los decimales se muestran con coma). Correrlo con `.venv/Scripts/python -m presentacion.crear_pptx` (agregar `presentacion/__init__.py`).
- [ ] **Step 4:** Correr las pruebas. Esperado: 3 passed.
- [ ] **Step 5:** Revisar el resultado diapositiva por diapositiva: exportar cada una a imagen (PowerPoint por COM si está instalado; si no, pedir al usuario que lo abra) y chequear desbordes, contraste y que los mapas no se deformen.
- [ ] **Step 6: Punto de control con el usuario:** entregar el `.pptx` y el guion para el ensayo del 23/11.

---

### Task 12: Verificación final

**Files:**
- Create: `ENTREGA.md`

- [ ] **Step 1:** Correr `.venv/Scripts/python -m pytest -v`. Esperado: todas las pruebas pasan.
- [ ] **Step 2:** Regenerar todo desde cero en orden (`procesar`, mapas 1 a 4, `esquema_infra`, `exportar_poster`, `crear_pptx`) y confirmar que termina sin errores.
- [ ] **Step 3:** Cotejar cada cifra visible en el póster y en la presentación contra `salidas/cifras.json`, y cada dato del Salí contra su fuente.
- [ ] **Step 4:** Repasar la consigna punto por punto (rótulo abajo a la derecha, nombres de archivo, JPG a 300 ppp, 10 minutos, caso local) y los límites declarados del spec.
- [ ] **Step 5:** Escribir `ENTREGA.md`: qué archivos se suben, el texto para el grupo de WhatsApp con el número pendiente de confirmar, cómo regenerar todo, y lo que el grupo todavía tiene que hacer a mano (imprimir el póster, agregar la foto con crédito en la diapositiva 4 si la quieren, ensayar).
