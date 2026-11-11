import pytest
from PIL import Image

from scripts import cifras, config, exportar_poster

Image.MAX_IMAGE_PIXELS = None
PLANTILLA = config.RAIZ / "poster" / "poster.html"
FINAL = config.RAIZ / "poster" / f"{config.NOMBRE_BASE}.jpg"


def test_rellenar_reemplaza_valores():
    assert exportar_poster.rellenar("<p>{{a}}-{{b}}</p>", {"a": "1", "b": "2"}) == "<p>1-2</p>"


def test_rellenar_falla_si_queda_marcador():
    with pytest.raises(KeyError, match="falta"):
        exportar_poster.rellenar("<p>{{ok}} {{falta}}</p>", {"ok": "1"})


def test_plantilla_completa_sin_marcadores():
    html = exportar_poster.rellenar(PLANTILLA.read_text(encoding="utf-8"),
                                    exportar_poster.valores_poster())
    assert "{{" not in html
    for nombre in config.INTEGRANTES:
        assert nombre in html
    assert config.MATERIA in html and config.ANIO in html


def test_poster_usa_cifras_calculadas():
    valores = exportar_poster.valores_poster()
    c = cifras.leer()
    assert valores["propuesta_humedal"] == f"{c['propuesta']['humedal']:.0f}"
    assert valores["propuesta_bosque"] == f"{c['propuesta']['bosque']:.0f}"
    assert valores["propuesta_accesos"] == str(c["propuesta"]["accesos"])


def test_poster_final_dimensiones():
    im = Image.open(FINAL)
    assert im.size == (7016, 9933)
    assert im.mode == "RGB"
    assert round(im.info["dpi"][0]) == 300
