from PIL import Image

from scripts import estilo


def test_terminar_mapa_guarda_png_300ppp(tmp_path):
    fig, ax = estilo.nuevo_mapa("¿Pregunta?", "Título")
    ax.plot([0, 1000], [0, 1000])
    ruta = estilo.terminar_mapa(fig, ax, "Fuente: prueba", tmp_path / "m.png")
    im = Image.open(ruta)
    assert im.size == (3000, 3000)
    assert round(im.info["dpi"][0]) == 300
