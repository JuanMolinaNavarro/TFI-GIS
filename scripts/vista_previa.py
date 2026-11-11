"""Vista previa del área de estudio: cobertura, río y franja, y altura sobre el cauce."""
import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402

from scripts import config, procesar  # noqa: E402

P = config.PALETA
COLORES_WC = {10: P["vegetacion"], 20: P["vegetacion"], 30: "#8FB07A", 90: P["humedal"],
              40: P["cultivo"], 50: P["construido"], 60: P["desnudo"], 80: P["agua"]}


def imagen_cobertura(cob):
    """Arreglo RGBA de la cobertura con la paleta común."""
    from matplotlib.colors import to_rgba
    rgba = np.zeros(cob.shape + (4,))
    for clase, color in COLORES_WC.items():
        rgba[cob == clase] = to_rgba(color)
    return rgba


def main():
    cob, transf = procesar.leer_raster("cobertura.tif")
    alt, _ = procesar.leer_raster("altura_cauce.tif")
    ext = procesar.extension(transf, cob.shape)
    rio = gpd.read_file(config.GPKG, layer="rio")
    franja = gpd.read_file(config.GPKG, layer="franja")

    fig, ejes = plt.subplots(1, 2, figsize=(12, 10), facecolor=P["fondo"])
    ejes[0].imshow(imagen_cobertura(cob), extent=ext)
    ejes[0].set_title(f"Cobertura, río y franja de {config.FRANJA_M} m")
    niveles = [-50, 1, 2, 3, 5, 10, 500]
    cmap = ListedColormap(["#1B4F6B", "#2B6C8F", "#6FA3BD", "#B9D2DD", "#E4E0D2", "#F4F1EA"])
    im = ejes[1].imshow(np.ma.masked_equal(alt, -9999), extent=ext, cmap=cmap,
                        norm=BoundaryNorm(niveles, cmap.N))
    ejes[1].set_title("Altura sobre el cauce (m)")
    fig.colorbar(im, ax=ejes[1], shrink=0.6, ticks=[1, 2, 3, 5, 10])
    for ax in ejes:
        franja.boundary.plot(ax=ax, color=P["tinta"], linewidth=0.8)
        rio.plot(ax=ax, color="#0B2E40", linewidth=1.0)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    ruta = config.SALIDAS / "vista_previa_aoi.png"
    fig.savefig(ruta, dpi=110)
    print(ruta)


if __name__ == "__main__":
    main()
