"""Carga y elementos comunes de los mapas del área de estudio (mapas 2, 3 y 4)."""
import textwrap

import geopandas as gpd
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle

from scripts import config, estilo, procesar

P = config.PALETA
COLOR_GRUPO = {"vegetacion": P["vegetacion"], "cultivo": P["cultivo"],
               "construido": P["construido"], "desnudo": P["desnudo"], "agua": P["agua"]}
ETIQUETA_GRUPO = {"vegetacion": "Vegetación", "cultivo": "Cultivo", "construido": "Construido",
                  "desnudo": "Suelo desnudo", "agua": "Agua"}


class Datos:
    def __init__(self):
        self.cob, self.transf = procesar.leer_raster("cobertura.tif")
        self.dem, _ = procesar.leer_raster("dem.tif")
        alt, _ = procesar.leer_raster("altura_cauce.tif")
        self.altura = np.where(alt == -9999, np.nan, alt)
        self.distancia, _ = procesar.leer_raster("distancia_cauce.tif")
        self.ext = procesar.extension(self.transf, self.cob.shape)

        def capa(nombre):
            return gpd.read_file(config.GPKG, layer=nombre)

        self.rio, self.franja, self.aoi, self.vias = (capa("rio"), capa("franja"),
                                                      capa("aoi"), capa("vias"))
        self.franja_celdas = procesar.rasterizar(self.franja.geometry.iloc[0],
                                                 self.transf, self.cob.shape)


def imagen_cobertura(cob, alfa=1.0):
    """Arreglo RGBA de la cobertura agrupada, con la paleta común."""
    rgba = np.zeros(cob.shape + (4,))
    for grupo, clases in config.CLASES_WC.items():
        rgba[np.isin(cob, clases)] = to_rgba(COLOR_GRUPO[grupo], alfa)
    return rgba


def velo(mascara, alfa):
    """Capa del color de fondo, semitransparente, donde `mascara` es verdadera."""
    rgba = np.zeros(mascara.shape + (4,))
    rgba[mascara] = to_rgba(P["fondo"], alfa)
    return rgba


def encuadrar(ax, d):
    estilo.encuadrar(ax, d.aoi.total_bounds)


def panel(fig, y, texto, tam=12, ancho=40, **kwargs):
    """Escribe un bloque de texto en el panel derecho y devuelve la y siguiente."""
    k = fig._escala
    lineas = []
    for parrafo in texto.split("\n"):
        lineas.extend(textwrap.wrap(parrafo, ancho) or [""])
    opciones = {"fontsize": tam * k, "va": "top", "linespacing": 1.25}
    opciones.update(kwargs)
    fig.text(estilo.PANEL_X, y, "\n".join(lineas), **opciones)
    return y - len(lineas) * tam * 1.25 / 720 - 0.012


def muestra(fig, y, color, etiqueta, tam=12):
    """Cuadro de color con etiqueta en el panel derecho."""
    k = fig._escala
    fig.patches.append(Rectangle((estilo.PANEL_X, y), 0.035, 0.024, transform=fig.transFigure,
                                 facecolor=color, edgecolor=P["tinta"], linewidth=0.4 * k))
    fig.text(estilo.PANEL_X + 0.05, y + 0.012, etiqueta, fontsize=tam * k, va="center")


def es(numero, decimales=1):
    """Número con coma decimal y punto de miles."""
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")
