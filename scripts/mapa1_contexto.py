"""Mapa 1: ¿Cómo es el territorio? Contexto provincial y de cuenca."""
import geopandas as gpd
import numpy as np
from matplotlib.colors import ListedColormap
from shapely.geometry import Point

from scripts import config, estilo, procesar

P = config.PALETA


def _xy(lon, lat):
    p = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(config.CRS_PROY).iloc[0]
    return p.x, p.y


def main():
    capa = lambda n: gpd.read_file(config.GPKG, layer=n)  # noqa: E731
    prov, dep, hidro = capa("provincia"), capa("departamentos"), capa("hidro")
    cuenca, aoi, rio = capa("cuenca"), capa("aoi"), capa("rio_prov")
    urbano, t_urb = procesar.leer_raster("urbano_prov.tif")

    fig, ax = estilo.nuevo_mapa("¿Cómo es el territorio?",
                                "El Río Salí y su cuenca en la provincia de Tucumán")
    k = fig._escala

    cuenca.plot(ax=ax, color=P["agua"], alpha=0.13, zorder=1)
    prov.plot(ax=ax, facecolor="#FFFFFF", alpha=0.55, edgecolor="none", zorder=2)
    cuenca.boundary.plot(ax=ax, color=P["agua"], linewidth=1.1, linestyle=(0, (5, 3)), zorder=3)
    dep.boundary.plot(ax=ax, color=P["tinta"], linewidth=0.3, alpha=0.35, zorder=4)
    hidro.plot(ax=ax, color=P["agua"], linewidth=0.45, alpha=0.6, zorder=5)

    ax.imshow(np.ma.masked_where(urbano != 1, urbano), cmap=ListedColormap([P["construido"]]),
              extent=procesar.extension(t_urb, urbano.shape), interpolation="nearest", zorder=6)

    rio.plot(ax=ax, color=P["agua"], linewidth=2.4, zorder=7)
    prov.boundary.plot(ax=ax, color=P["tinta"], linewidth=1.4, zorder=8)
    aoi.boundary.plot(ax=ax, color=P["acento"], linewidth=2.6, zorder=9)

    estilo.encuadrar(ax, prov.total_bounds, margen=0.06)

    o, s, e, n = aoi.total_bounds
    ax.annotate("Área de estudio\ntramo urbano del Salí", xy=(e, (s + n) / 2),
                xytext=(e + 22000, n + 14000), fontsize=12, fontweight="bold", zorder=12,
                path_effects=estilo.halo(), va="center",
                arrowprops={"arrowstyle": "-", "color": P["acento"], "lw": 1.6})
    x, y = _xy(-65.222, -26.83)
    ax.text(x - 9000, y + 2000, "San Miguel\nde Tucumán", fontsize=10.5, ha="right",
            va="center", path_effects=estilo.halo(), zorder=12)
    x, y = _xy(*config.PUNTO_CIERRE_CUENCA)
    ax.plot(x, y, marker="v", color=P["tinta"], markersize=7, zorder=12)
    ax.text(x - 4000, y - 6500, "Embalse de\nRío Hondo", fontsize=10, ha="center", va="top",
            path_effects=estilo.halo(), zorder=12)
    x, y = _xy(-65.19, -27.34)
    ax.text(x, y, "Río Salí", fontsize=11, color=P["agua"], fontweight="bold", style="italic",
            rotation=-62, ha="center", va="center", path_effects=estilo.halo(), zorder=12)

    estilo.leyenda(ax, [("Cuenca Salí-Dulce (hasta Río Hondo)", "#C9DCE6"),
                        ("Río Salí y red hídrica", P["agua"]),
                        ("Áreas urbanas", P["construido"]),
                        ("Área de estudio", P["acento"])], loc="upper left")

    ruta = estilo.terminar_mapa(
        fig, ax, "Fuentes: IGN, OpenStreetMap, HydroBASINS (HydroSHEDS), ESA WorldCover 2021. "
                 "Proyección POSGAR 2007 / Argentina 3.",
        config.MAPAS / "mapa1_contexto.png")
    print(ruta)


if __name__ == "__main__":
    main()
