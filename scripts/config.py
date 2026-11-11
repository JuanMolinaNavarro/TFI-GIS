"""Configuración común: rutas, área de estudio, umbrales, paleta y rótulo."""
import math
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CRUDOS = RAIZ / "datos" / "crudos"
PROCESADOS = RAIZ / "datos" / "procesados"
SALIDAS = RAIZ / "salidas"
MAPAS = SALIDAS / "mapas"
CIFRAS = SALIDAS / "cifras.json"
GPKG = PROCESADOS / "sali.gpkg"

CRS_PROY = "EPSG:5345"  # POSGAR 2007 / Argentina 3
PIXEL_M = 10

# (oeste, sur, este, norte) en grados. Valor inicial; se revisa al ver los datos.
AOI_BBOX = (-65.25, -26.93, -65.12, -26.74)

# Recuadro que contiene a la provincia de Tucumán (para descargas a escala provincial)
PROV_BBOX = (-66.30, -28.10, -64.40, -25.95)

FRANJA_M = 500
UMBRAL_BAJO_M = float(os.environ.get("UMBRAL_BAJO_M", 2.0))
# La cota del río se toma como el mínimo del modelo de elevación en esta ventana (m)
# y se le quitan las subidas aguas abajo. Con 0 se usa la celda del eje tal cual.
COTA_RIO_VENTANA_M = int(os.environ.get("COTA_RIO_VENTANA_M", 30))
ANCHO_BOSQUE_M = 100
ACCESO_DIST_M = 150
ACCESO_SEPARACION_M = 500

PUNTO_CIERRE_CUENCA = (-64.887, -27.522)  # dique de Río Hondo (lon, lat)

PALETA = {
    "fondo": "#F4F1EA",
    "tinta": "#1F2A2E",
    "agua": "#2B6C8F",
    "vegetacion": "#4F7F52",
    "humedal": "#3FA796",
    "construido": "#B5533C",
    "desnudo": "#D9B77E",
    "cultivo": "#C9D48A",
    "acento": "#E0A526",
}
FUENTE = "Segoe UI"

INTEGRANTES = [
    "Juan Martin Molina Navarro",
    "Sebastian Zelarayan",
    "Juan Simon",
    "Agustin Darelli",
]
MATERIA = "4K07 Sistemas de Información Geográfica (GIS)"
ANIO = "2026"
NOMBRE_BASE = "PA2-Geoempowering-Design-MolinaNavarro"

# Clases de ESA WorldCover agrupadas
CLASES_WC = {
    "vegetacion": (10, 20, 30, 90),
    "cultivo": (40,),
    "construido": (50,),
    "desnudo": (60,),
    "agua": (80,),
}


def _esquinas(bbox, paso):
    """Esquinas sudoeste (lat, lon) de las teselas de `paso` grados que tocan bbox."""
    oeste, sur, este, norte = bbox
    eps = 1e-9
    lat0 = math.floor(sur / paso) * paso
    lat1 = math.floor((norte - eps) / paso) * paso
    lon0 = math.floor(oeste / paso) * paso
    lon1 = math.floor((este - eps) / paso) * paso
    return [(lat, lon)
            for lat in range(lat0, lat1 + 1, paso)
            for lon in range(lon0, lon1 + 1, paso)]


def _ns(lat):
    return f"{'S' if lat < 0 else 'N'}{abs(lat):02d}"


def _ew(lon):
    return f"{'W' if lon < 0 else 'E'}{abs(lon):03d}"


def teselas_worldcover(bbox):
    """Nombres de teselas WorldCover (3 grados), p. ej. 'S27W066'."""
    return sorted(f"{_ns(lat)}{_ew(lon)}" for lat, lon in _esquinas(bbox, 3))


def teselas_dem(bbox):
    """Nombres de teselas Copernicus GLO-30 (1 grado), p. ej. 'S27_00_W066_00'."""
    return sorted(f"{_ns(lat)}_00_{_ew(lon)}_00" for lat, lon in _esquinas(bbox, 1))
