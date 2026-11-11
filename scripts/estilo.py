"""Marco común de los mapas: tipografía, título, escala, norte, fuente y leyenda."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib_scalebar.scalebar import ScaleBar  # noqa: E402

from scripts import config  # noqa: E402

P = config.PALETA
plt.rcParams["font.family"] = config.FUENTE
plt.rcParams["text.color"] = P["tinta"]

CAJA_COMPLETA = (0.04, 0.07, 0.92, 0.79)
# Para el área de estudio (vertical): mapa a la izquierda y panel a la derecha
CAJA_IZQUIERDA = (0.04, 0.07, 0.50, 0.79)
PANEL_X = 0.59


def halo(ancho=3):
    return [pe.withStroke(linewidth=ancho, foreground=P["fondo"])]


def nuevo_mapa(pregunta, titulo, lado_in=10, caja=CAJA_COMPLETA):
    """Figura cuadrada con la pregunta como título principal y `titulo` como subtítulo."""
    fig = plt.figure(figsize=(lado_in, lado_in), facecolor=P["fondo"])
    k = lado_in / 10
    fig.text(0.04, 0.955, pregunta, fontsize=30 * k, fontweight="bold", va="top")
    fig.text(0.04, 0.898, titulo, fontsize=14.5 * k, va="top", alpha=0.85)
    ax = fig.add_axes(caja)
    ax.set_facecolor(P["fondo"])
    ax.set_xticks([])
    ax.set_yticks([])
    for lado in ax.spines.values():
        lado.set_edgecolor(P["tinta"])
        lado.set_linewidth(0.8 * k)
    ax.set_aspect("equal", adjustable="datalim")
    fig._escala = k
    return fig, ax


def encuadrar(ax, limites, margen=0.0):
    """Fija el encuadre (minx, miny, maxx, maxy) con un margen relativo."""
    o, s, e, n = limites
    dx, dy = (e - o) * margen, (n - s) * margen
    ax.set_xlim(o - dx, e + dx)
    ax.set_ylim(s - dy, n + dy)


def leyenda(ax, items, titulo=None, **kwargs):
    """items: lista de (etiqueta, color)."""
    k = ax.figure._escala
    manijas = [Patch(facecolor=color, edgecolor=P["tinta"], linewidth=0.4 * k, label=etiqueta)
               for etiqueta, color in items]
    opciones = {"loc": "lower left", "frameon": True, "facecolor": P["fondo"],
                "edgecolor": "none", "framealpha": 0.9, "fontsize": 11 * k,
                "title_fontsize": 11.5 * k, "handlelength": 1.3, "handleheight": 1.1,
                "labelspacing": 0.5, "borderpad": 0.7}
    opciones.update(kwargs)
    leg = ax.legend(handles=manijas, title=titulo, **opciones)
    leg._legend_box.align = "left"
    if titulo:
        leg.get_title().set_fontweight("bold")
    return leg


def terminar_mapa(fig, ax, fuente, ruta):
    """Agrega escala gráfica, norte y fuente, y guarda el PNG a 300 ppp."""
    k = fig._escala
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.add_artist(ScaleBar(1, units="m", location="lower right", box_color=P["fondo"],
                           box_alpha=0.85, color=P["tinta"], length_fraction=0.22,
                           font_properties={"family": config.FUENTE, "size": 10.5 * k},
                           border_pad=0.6, pad=0.5))
    ax.annotate("N", xy=(0.955, 0.975), xytext=(0.955, 0.895), xycoords="axes fraction",
                ha="center", va="center", fontsize=13 * k, fontweight="bold",
                path_effects=halo(3 * k), zorder=20,
                arrowprops={"arrowstyle": "-|>", "color": P["tinta"], "lw": 1.6 * k,
                            "mutation_scale": 16 * k})
    fig.text(0.04, 0.035, fuente, fontsize=9.5 * k, va="center", alpha=0.8)
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)
    return ruta
