import json

from scripts import config

RUTA = config.RAIZ / "contenido" / "textos.json"


def _textos():
    return json.loads(RUTA.read_text(encoding="utf-8"))


def test_datos_sali_tienen_fuente():
    t = _textos()
    assert 3 <= len(t["datos_sali"]) <= 5
    for d in t["datos_sali"]:
        assert d["fuente"].strip() and d["url"].startswith("http")


def test_estructura_textos():
    t = _textos()
    assert len(t["ensayo"]) == 4 and len(t["paralelo"]) == 3 and len(t["limites"]) == 4
    assert all(len(e["texto"].split()) <= 35 for e in t["ensayo"])
    assert len(t["cita"]["texto"].split()) < 15
    assert len(t["preguntas_previsibles"]) == 6
