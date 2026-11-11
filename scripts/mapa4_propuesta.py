"""Mapa 4: ¿Cómo podría cambiar? Propuesta de corredor ecológico."""
import geopandas as gpd
import numpy as np
from matplotlib.colors import ListedColormap
from rasterio import features
from scipy import ndimage
from shapely.geometry import shape

from scripts import analisis, aoi, cifras, config, estilo, procesar

P = config.PALETA
PARCHE_MINIMO_HA = 0.5
NOMBRE_ZONA = {1: "humedal", 2: "bosque"}


def quitar_parches_chicos(zonas, minimo_ha, pixel_m):
    """Pone en 0 los parches de cada zona menores a `minimo_ha`."""
    minimo_px = minimo_ha * 10000 / (pixel_m * pixel_m)
    limpio = zonas.copy()
    for valor in (1, 2):
        etiquetas, n = ndimage.label(zonas == valor)
        if n == 0:
            continue
        tamanios = ndimage.sum(zonas == valor, etiquetas, index=np.arange(1, n + 1))
        chicos = np.isin(etiquetas, np.flatnonzero(tamanios < minimo_px) + 1)
        limpio[chicos] = 0
    return limpio


def main():
    d = aoi.Datos()
    zonas = analisis.zonificar(d.cob, d.altura, d.distancia, d.franja_celdas,
                               config.UMBRAL_BAJO_M, config.ANCHO_BOSQUE_M)
    zonas = quitar_parches_chicos(zonas, PARCHE_MINIMO_HA, config.PIXEL_M)
    ha = analisis.hectareas_por_zona(zonas, config.PIXEL_M)
    rio = d.rio.geometry.iloc[0]
    accesos = analisis.puntos_de_acceso(d.vias.geometry, rio, config.ACCESO_DIST_M,
                                        config.ACCESO_SEPARACION_M)

    procesar.guardar_raster(config.PROCESADOS / "zonas.tif", zonas, d.transf, 255)
    poligonos = [{"zona": NOMBRE_ZONA[int(v)], "geometry": shape(g)}
                 for g, v in features.shapes(zonas, mask=zonas > 0, transform=d.transf)]
    if poligonos:
        gpd.GeoDataFrame(poligonos, crs=config.CRS_PROY).to_file(
            config.GPKG, layer="zonas", driver="GPKG")
    if accesos:
        gpd.GeoDataFrame(geometry=accesos, crs=config.CRS_PROY).to_file(
            config.GPKG, layer="accesos", driver="GPKG")
    reparto = analisis.bosque_existente_y_a_restaurar(zonas, d.cob, config.PIXEL_M)
    cifras.guardar("propuesta", {**ha, **reparto, "accesos": len(accesos),
                                 "umbral_bajo_m": config.UMBRAL_BAJO_M,
                                 "ancho_bosque_m": config.ANCHO_BOSQUE_M,
                                 "parche_minimo_ha": PARCHE_MINIMO_HA})

    fig, ax = estilo.nuevo_mapa(
        "¿Cómo podría cambiar?",
        "Corredor ecológico del Salí: ejercicio académico de geodiseño",
        lado_in=16, caja=estilo.CAJA_IZQUIERDA)
    k = fig._escala
    ax.imshow(aoi.imagen_cobertura(d.cob), extent=d.ext, interpolation="nearest", zorder=1)
    ax.imshow(aoi.velo(np.ones(d.cob.shape, bool), 0.74), extent=d.ext, zorder=2)
    d.vias.plot(ax=ax, color=P["tinta"], linewidth=0.18 * k, alpha=0.35, zorder=3)
    ax.imshow(np.ma.masked_equal(zonas, 0), extent=d.ext, interpolation="nearest",
              cmap=ListedColormap([P["humedal"], P["vegetacion"]]), vmin=1, vmax=2, zorder=4)
    d.franja.boundary.plot(ax=ax, color=P["tinta"], linewidth=0.7 * k, alpha=0.7, zorder=5)
    d.rio.plot(ax=ax, color=P["agua"], linewidth=1.5 * k, zorder=6)
    if accesos:
        ax.scatter([p.x for p in accesos], [p.y for p in accesos], s=26 * k * k,
                   color=P["acento"], edgecolor=P["tinta"], linewidth=0.5 * k, zorder=7)
    aoi.encuadrar(ax, d)

    y = aoi.panel(fig, 0.86, f"{aoi.es(ha['bosque'], 0)} ha", tam=54, fontweight="bold",
                  color=P["vegetacion"])
    y = aoi.panel(fig, y,
                  f"de corredor de bosque de ribera: {aoi.es(reparto['bosque_existente'], 0)} "
                  f"ya arboladas y {aoi.es(reparto['bosque_restaurar'], 0)} a restaurar.",
                  tam=15, ancho=30)
    y = aoi.panel(fig, y - 0.012, f"{aoi.es(ha['humedal'], 0)} ha", tam=30, fontweight="bold",
                  color=P["humedal"])
    y = aoi.panel(fig, y, "aptas para humedales en terrazas que retienen y filtran el agua.",
                  tam=13, ancho=34)
    y = aoi.panel(fig, y - 0.012, f"{len(accesos)}", tam=30, fontweight="bold",
                  color="#B07F12")
    y = aoi.panel(fig, y, f"posibles accesos: calles que hoy llegan a {config.ACCESO_DIST_M} m "
                          "del río.", tam=13, ancho=34)

    y -= 0.03
    fig.text(estilo.PANEL_X, y, "Cómo se definió cada zona", fontsize=12.5 * k,
             fontweight="bold")
    reglas = [
        (P["vegetacion"], f"Bosque de ribera: los primeros {config.ANCHO_BOSQUE_M} m "
                          "junto al cauce, sin edificar."),
        (P["humedal"], f"Humedal: más allá del bosque, terreno a "
                       f"{aoi.es(config.UMBRAL_BAJO_M, 0)} m o menos sobre el cauce, "
                       "sin edificar."),
        (P["acento"], f"Acceso: cruce de una calle con la línea de {config.ACCESO_DIST_M} m "
                      f"del río, uno cada {config.ACCESO_SEPARACION_M} m por margen."),
    ]
    y -= 0.045
    for color, texto in reglas:
        aoi.muestra(fig, y, color, "")
        import textwrap
        lineas = textwrap.wrap(texto, 34)
        fig.text(estilo.PANEL_X + 0.05, y + 0.026, "\n".join(lineas), fontsize=11 * k,
                 va="top", linespacing=1.25)
        y -= max(2, len(lineas)) * 0.0195 + 0.022

    aoi.panel(fig, 0.135,
              "Son superficies aptas según la regla, no terreno disponible, y son "
              "orientativas: dependen de datos de 10 y 30 m. Los 100 m se miden desde el "
              f"eje del río. Se descartaron parches menores a {aoi.es(PARCHE_MINIMO_HA)} ha.",
              tam=10.5, alpha=0.8, ancho=46)

    print(estilo.terminar_mapa(
        fig, ax, "Elaboración propia sobre ESA WorldCover 2021, Copernicus DEM GLO-30 y "
                 "OpenStreetMap.", config.MAPAS / "mapa4_propuesta.png"))
    print(ha, "accesos:", len(accesos))


if __name__ == "__main__":
    main()
