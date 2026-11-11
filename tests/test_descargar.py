import pytest

from scripts import descargar


class _Resp:
    def __init__(self, status, cuerpo):
        self.status_code = status
        self._cuerpo = cuerpo

    def iter_content(self, chunk_size=1):
        yield self._cuerpo

    def close(self):
        pass


def test_bajar_respuesta_chica_no_deja_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(descargar.requests, "get", lambda *a, **k: _Resp(200, b"x" * 10))
    with pytest.raises(RuntimeError, match="http://x/y.tif"):
        descargar.bajar("http://x/y.tif", tmp_path / "y.tif")
    assert list(tmp_path.iterdir()) == []


def test_bajar_error_http_no_deja_archivo(tmp_path, monkeypatch):
    monkeypatch.setattr(descargar.requests, "get", lambda *a, **k: _Resp(503, b"x" * 5000))
    with pytest.raises(RuntimeError):
        descargar.bajar("http://x/y.tif", tmp_path / "y.tif")
    assert list(tmp_path.iterdir()) == []


def test_bajar_no_repite_si_existe(tmp_path, monkeypatch):
    destino = tmp_path / "y.tif"
    destino.write_bytes(b"x" * 2000)

    def _no(*a, **k):
        raise AssertionError("no debía descargar")

    monkeypatch.setattr(descargar.requests, "get", _no)
    assert descargar.bajar("http://x/y.tif", destino) == destino


def test_bajar_guarda_contenido(tmp_path, monkeypatch):
    monkeypatch.setattr(descargar.requests, "get", lambda *a, **k: _Resp(200, b"x" * 5000))
    destino = descargar.bajar("http://x/y.tif", tmp_path / "y.tif")
    assert destino.read_bytes() == b"x" * 5000
    assert [p.name for p in tmp_path.iterdir()] == ["y.tif"]
