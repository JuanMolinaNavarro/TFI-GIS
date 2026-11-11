"""Funciones de análisis sobre arreglos. No leen ni escriben archivos."""
import numpy as np
from scipy import ndimage

from scripts import config


def porcentajes_cobertura(cob, mascara):
    """Porcentaje de cada grupo de cobertura dentro de `mascara`, sobre píxeles con dato."""
    validos = mascara & (cob != 0)
    total = int(validos.sum())
    if total == 0:
        return {nombre: 0.0 for nombre in config.CLASES_WC}
    return {nombre: round(100.0 * int((validos & np.isin(cob, clases)).sum()) / total, 1)
            for nombre, clases in config.CLASES_WC.items()}


def distancia_y_altura(dem, rio, pixel_m, nodata=-9999):
    """Distancia (m) a la celda de río más cercana y altura del terreno sobre esa celda."""
    dist, (fi, co) = ndimage.distance_transform_edt(~rio, return_indices=True)
    dem = dem.astype("float64")
    dem[dem == nodata] = np.nan
    altura = dem - dem[fi, co]
    return dist * pixel_m, altura


def zonificar(cob, altura, distancia, franja, umbral_bajo_m, ancho_bosque_m):
    """1 = humedal en terrazas, 2 = bosque de ribera, 0 = sin intervención.

    El bosque es una franja continua junto al cauce; el humedal ocupa el terreno
    bajo que queda más allá. Ninguno incluye lo edificado ni el agua.
    """
    zonas = np.zeros(cob.shape, dtype=np.uint8)
    apto = franja & ~np.isin(cob, (0, 50, 80))
    bosque = apto & (distancia <= ancho_bosque_m)
    humedal = apto & (altura <= umbral_bajo_m) & ~bosque
    zonas[humedal] = 1
    zonas[bosque] = 2
    return zonas


def hectareas_por_zona(zonas, pixel_m):
    ha_por_pixel = pixel_m * pixel_m / 10000.0
    return {"humedal": round(float((zonas == 1).sum()) * ha_por_pixel, 1),
            "bosque": round(float((zonas == 2).sum()) * ha_por_pixel, 1)}


def puntos_de_acceso(vias, rio, dist_m, separacion_m):
    """Puntos donde las vías cruzan el borde de la franja de `dist_m` del río.

    Se ordenan a lo largo del río y, en cada margen, se descartan los que quedan a
    menos de `separacion_m` (medidos sobre el río) del último aceptado.
    """
    borde = rio.buffer(dist_m).boundary
    margen_izq = rio.buffer(dist_m * 1.05, single_sided=True)
    candidatos = []
    for geom in vias.intersection(borde):
        if geom is None or geom.is_empty:
            continue
        partes = getattr(geom, "geoms", [geom])
        candidatos.extend(p for p in partes if p.geom_type == "Point")
    candidatos.sort(key=rio.project)
    aceptados, ultimo = [], {}
    for p in candidatos:
        lado = margen_izq.contains(p)
        pos = rio.project(p)
        if lado in ultimo and pos - ultimo[lado] < separacion_m:
            continue
        ultimo[lado] = pos
        aceptados.append(p)
    return aceptados


def perfil_descendente(cotas):
    """Perfil del río sin subidas aguas abajo (mínimo acumulado en el sentido de escurrimiento).

    `cotas` va ordenado a lo largo del río; el sentido se deduce de qué extremo es más alto.
    """
    cotas = np.asarray(cotas, dtype="float64")
    n = max(1, len(cotas) // 10)
    if np.nanmean(cotas[:n]) >= np.nanmean(cotas[-n:]):
        return np.minimum.accumulate(cotas)
    return np.minimum.accumulate(cotas[::-1])[::-1]


def cota_del_rio(dem, rio, orden, ventana_px, nodata=-9999):
    """Cota del agua en cada celda de río (en el orden de np.nonzero(rio)).

    El eje del río no siempre cae sobre el agua y el modelo es de superficie (incluye
    árboles y techos), así que se toma el mínimo local en una ventana y se quitan las
    subidas aguas abajo. `orden` es la posición de cada celda a lo largo del río.
    """
    valido = np.where(dem == nodata, np.inf, dem.astype("float64"))
    minimo = ndimage.minimum_filter(valido, size=2 * ventana_px + 1, mode="nearest")
    cotas = minimo[rio]
    indice = np.argsort(orden, kind="stable")
    resultado = np.empty_like(cotas)
    resultado[indice] = perfil_descendente(cotas[indice])
    return resultado


def bosque_existente_y_a_restaurar(zonas, cob, pixel_m):
    """Hectáreas del corredor de bosque que ya son arbolado (clase 10) y las que no."""
    ha = pixel_m * pixel_m / 10000.0
    bosque = zonas == 2
    return {"bosque_existente": round(float((bosque & (cob == 10)).sum()) * ha, 1),
            "bosque_restaurar": round(float((bosque & (cob != 10)).sum()) * ha, 1)}
