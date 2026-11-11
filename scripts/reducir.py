"""Guarda copias reducidas de imágenes para revisarlas rápido. Uso: python -m scripts.reducir a.png b.png"""
import sys
from pathlib import Path

from PIL import Image

from scripts import config

Image.MAX_IMAGE_PIXELS = None


def main(rutas, lado=1000):
    destino = config.SALIDAS / "revision"
    destino.mkdir(parents=True, exist_ok=True)
    for ruta in map(Path, rutas):
        im = Image.open(ruta)
        im.thumbnail((lado, lado * 2))
        im.convert("RGB").save(destino / (ruta.stem + ".png"))
        print(destino / (ruta.stem + ".png"))


if __name__ == "__main__":
    main(sys.argv[1:])
