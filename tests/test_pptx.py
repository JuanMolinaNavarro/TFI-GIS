from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from scripts import cifras, config

RUTA = config.RAIZ / "presentacion" / f"{config.NOMBRE_BASE}.pptx"


def _texto(diapositiva):
    return " ".join(sh.text_frame.text for sh in diapositiva.shapes if sh.has_text_frame)


def test_once_diapositivas_16_9_con_notas():
    p = Presentation(RUTA)
    assert len(p.slides) == 11
    assert round(p.slide_width / p.slide_height, 3) == round(16 / 9, 3)
    assert all(s.notes_slide.notes_text_frame.text.strip() for s in p.slides)


def test_mapas_en_diapositivas_6_a_9():
    p = Presentation(RUTA)
    for i in (5, 6, 7, 8):
        assert any(sh.shape_type == MSO_SHAPE_TYPE.PICTURE for sh in p.slides[i].shapes)


def test_cifras_salen_de_cifras_json():
    c = cifras.leer()
    p = Presentation(RUTA)
    assert str(c["ribera"]["vegetacion"]).replace(".", ",") in _texto(p.slides[6])
    assert f"{c['propuesta']['humedal']:.0f}" in _texto(p.slides[8])
    assert f"{c['propuesta']['bosque']:.0f}" in _texto(p.slides[8])


def test_portada_con_integrantes():
    p = Presentation(RUTA)
    portada = _texto(p.slides[0])
    for nombre in config.INTEGRANTES:
        assert nombre in portada


def test_preguntas_previsibles_en_notas_de_cierre():
    p = Presentation(RUTA)
    notas = p.slides[9].notes_slide.notes_text_frame.text
    assert notas.count("P:") == 6
