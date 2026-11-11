from scripts import cifras, config


def test_guardar_fusiona_secciones(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CIFRAS", tmp_path / "cifras.json")
    cifras.guardar("ribera", {"vegetacion": 40.0})
    cifras.guardar("propuesta", {"humedal": 12.5})
    assert cifras.leer() == {"ribera": {"vegetacion": 40.0}, "propuesta": {"humedal": 12.5}}


def test_leer_sin_archivo_devuelve_vacio(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CIFRAS", tmp_path / "no_existe.json")
    assert cifras.leer() == {}
