"""Mapa 3: ¿Cómo funciona el agua? Altura del terreno sobre el cauce."""
import numpy as np
from matplotlib.colors import BoundaryNorm, LightSource, ListedColormap

from scripts import analisis, aoi, cifras, config, estilo, procesar

P = config.PALETA
NIVELES = [-1000, 1, 2, 3, 5, 10, 1000]
COLORES = ["#17475F", "#2B6C8F", "#5E97B3", "#97BCCD", "#CBDADB", "#E9E6DA"]
ETIQUETAS = ["hasta 1 m", "1 a 2 m", "2 a 3 m", "3 a 5 m", "5 a 10 m", "más de 10 m"]
ALCANCE_M = config.FRANJA_M  # el indicador solo se muestra dentro de la franja


def main():
    d = aoi.Datos()
    en_franja = d.franja_celdas & ~np.isnan(d.altura)
    pct_bajo = round(100.0 * float((d.altura[en_franja] <= config.UMBRAL_BAJO_M).sum())
                     / float(en_franja.sum()), 1)
    # Variante sin corregir la cota del río (celda del eje tal cual), para informar el rango
    rio_celdas = procesar.rasterizar(d.rio.geometry.iloc[0], d.transf, d.cob.shape)
    _, cruda = analisis.distancia_y_altura(d.dem, rio_celdas, config.PIXEL_M)
    pct_crudo = round(100.0 * float((cruda[en_franja] <= config.UMBRAL_BAJO_M).sum())
                      / float(en_franja.sum()), 1)
    cifras.guardar("altura", {"pct_bajo": pct_bajo, "pct_bajo_sin_corregir": pct_crudo,
                              "cota_rio_ventana_m": config.COTA_RIO_VENTANA_M,
                              "umbral_bajo_m": config.UMBRAL_BAJO_M,
                              "alcance_m": ALCANCE_M})

    fig, ax = estilo.nuevo_mapa("¿Cómo funciona el agua?",
                                "Altura de la superficie sobre el cauce (indicador topográfico)",
                                caja=estilo.CAJA_IZQUIERDA)
    k = fig._escala
    sombra = LightSource(azdeg=315, altdeg=45).hillshade(
        d.dem.astype(float), vert_exag=6, dx=config.PIXEL_M, dy=config.PIXEL_M)
    ax.imshow(sombra, extent=d.ext, cmap="gray", vmin=-0.4, vmax=1.3, alpha=0.5, zorder=1)
    cmap = ListedColormap(COLORES)
    visible = np.ma.masked_where(~d.franja_celdas | np.isnan(d.altura), d.altura)
    ax.imshow(visible, extent=d.ext, cmap=cmap, norm=BoundaryNorm(NIVELES, cmap.N),
              interpolation="nearest", zorder=2)
    d.franja.boundary.plot(ax=ax, color=P["tinta"], linewidth=1.0 * k, zorder=3)
    d.rio.plot(ax=ax, color="#0B2E40", linewidth=1.3 * k, zorder=4)
    aoi.encuadrar(ax, d)

    y = aoi.panel(fig, 0.86, f"{aoi.es(pct_bajo, 0)} %", tam=54, fontweight="bold",
                  color=P["agua"])
    y = aoi.panel(fig, y,
                  f"de la franja de ribera está a {aoi.es(config.UMBRAL_BAJO_M, 0)} m o menos "
                  "sobre el nivel del cauce.", tam=15, ancho=30)
    aoi.panel(fig, y - 0.004,
              "Son los terrenos más bajos respecto del río.",
              tam=12.5, alpha=0.85)

    fig.text(estilo.PANEL_X, 0.555, "Altura sobre el cauce", fontsize=12.5 * k,
             fontweight="bold")
    for i, (color, etiqueta) in enumerate(zip(COLORES, ETIQUETAS)):
        aoi.muestra(fig, 0.515 - i * 0.034, color, etiqueta)

    aoi.panel(fig, 0.29,
              "No es un modelo hidráulico de inundación.\n"
              "Compara cada punto con la cota del tramo de río más cercano, dentro de la "
              f"franja de {aoi.es(ALCANCE_M, 0)} m. El modelo de elevación es de superficie "
              "(30 m, incluye árboles y techos). Según cómo se tome la cota del río, la "
              f"cifra va de {aoi.es(pct_bajo, 0)} a {aoi.es(pct_crudo, 0)} %.",
              tam=11, alpha=0.85, ancho=44)

    print(estilo.terminar_mapa(
        fig, ax, "Fuentes: Copernicus DEM GLO-30, OpenStreetMap. Elaboración propia.",
        config.MAPAS / "mapa3_altura.png"))
    print("pct_bajo", pct_bajo)


if __name__ == "__main__":
    main()
