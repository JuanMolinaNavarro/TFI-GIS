"""Esquema propio: río canalizado en hormigón frente a humedales en terrazas."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from scripts import config  # noqa: E402

P = config.PALETA
plt.rcParams["font.family"] = config.FUENTE
SUELO = "#C9B79A"
HORMIGON = "#9A9A96"


def _arbol(ax, x, y, alto=0.9):
    ax.plot([x, x], [y, y + alto * 0.45], color="#6B4F36", lw=4, solid_capstyle="round")
    ax.add_patch(plt.Circle((x, y + alto * 0.75), alto * 0.36, color=P["vegetacion"]))


def _juncos(ax, x, y):
    for dx, h in ((-0.08, 0.32), (0, 0.42), (0.08, 0.3)):
        ax.plot([x + dx, x + dx * 1.6], [y, y + h], color=P["humedal"], lw=3,
                solid_capstyle="round")


def _lluvia(ax, xs, y):
    for x in xs:
        ax.annotate("", xy=(x, y - 0.5), xytext=(x + 0.12, y),
                    arrowprops={"arrowstyle": "-|>", "color": P["agua"], "lw": 2})


def _base(ax, titulo, subtitulo):
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.6, 5.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0, 5.15, titulo, fontsize=17, fontweight="bold", color=P["tinta"], va="top")
    ax.text(0, 4.5, subtitulo, fontsize=11.5, color=P["tinta"], alpha=0.85, va="top")


def canalizado(ax):
    _base(ax, "Río canalizado", "Evacúa rápido el agua: crecidas bruscas, ribera sin vida")
    x = np.array([0, 3.6, 3.6, 6.4, 6.4, 10])
    y = np.array([2.2, 2.2, 0.5, 0.5, 2.2, 2.2])
    ax.fill_between(x, y, -0.6, color=SUELO)
    ax.plot(x, y, color=HORMIGON, lw=12, solid_joinstyle="miter")
    ax.fill_between([3.72, 6.28], 0.62, 1.25, color=P["agua"])
    for bx in (0.5, 1.5, 2.5, 7.5, 8.5):
        ax.add_patch(plt.Rectangle((bx, 2.32), 0.7, 0.8 + 0.3 * (bx % 2), color=P["construido"]))
    _lluvia(ax, (1.2, 2.6, 7.6, 9.0), 4.05)


def terrazas(ax):
    _base(ax, "Infraestructura ecológica", "Humedales en terrazas: retienen y filtran el agua")
    x = np.array([0, 1.2, 1.5, 2.6, 2.9, 3.9, 4.3, 5.7, 6.1, 7.1, 7.4, 8.5, 8.8, 10])
    y = np.array([2.6, 2.6, 2.0, 2.0, 1.3, 1.3, 0.5, 0.5, 1.3, 1.3, 2.0, 2.0, 2.6, 2.6])
    ax.fill_between(x, y, -0.6, color=SUELO)
    ax.plot(x, y, color="#7C6A4E", lw=2)
    ax.fill_between([4.25, 5.75], 0.5, 1.1, color=P["agua"])
    for x0, x1, y0 in ((1.55, 2.6, 2.0), (2.95, 3.9, 1.3), (6.1, 7.05, 1.3), (7.4, 8.45, 2.0)):
        ax.fill_between([x0, x1], y0, y0 + 0.16, color=P["humedal"], alpha=0.75)
        for jx in np.linspace(x0 + 0.2, x1 - 0.2, 3):
            _juncos(ax, jx, y0 + 0.1)
    for ax_ in (0.5, 9.5):
        _arbol(ax, ax_, 2.6, 1.1)
    for ax_ in (4.05, 5.95):
        _arbol(ax, ax_, 0.95, 0.9)
    _lluvia(ax, (2.0, 3.4, 6.6, 8.0), 3.6)
    for (x0, y0), (x1, y1) in (((1.3, 2.5), (1.9, 2.15)), ((2.7, 1.9), (3.2, 1.45)),
                               ((8.7, 2.5), (8.1, 2.15)), ((7.3, 1.9), (6.8, 1.45))):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops={"arrowstyle": "-|>", "color": P["agua"], "lw": 2,
                                "connectionstyle": "arc3,rad=0.25"})


def main():
    fig, ejes = plt.subplots(1, 2, figsize=(10, 3.2), facecolor=P["fondo"])
    fig.subplots_adjust(left=0.03, right=0.97, top=0.99, bottom=0.01, wspace=0.06)
    canalizado(ejes[0])
    terrazas(ejes[1])
    ruta = config.MAPAS / "esquema_infra.png"
    fig.savefig(ruta, dpi=300, facecolor=fig.get_facecolor())
    print(ruta)


if __name__ == "__main__":
    main()
