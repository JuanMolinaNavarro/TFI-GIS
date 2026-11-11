"""Cifras calculadas por los mapas. Póster y presentación leen de acá."""
import json

from scripts import config


def leer():
    if not config.CIFRAS.exists():
        return {}
    return json.loads(config.CIFRAS.read_text(encoding="utf-8"))


def guardar(seccion, datos):
    todo = leer()
    todo[seccion] = datos
    config.CIFRAS.parent.mkdir(parents=True, exist_ok=True)
    config.CIFRAS.write_text(json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
