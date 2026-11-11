"""Rellena la plantilla del póster y lo exporta a JPG A1 a 300 ppp."""
import html
import io
import json
import re

from PIL import Image

from scripts import cifras, config

Image.MAX_IMAGE_PIXELS = None
CARPETA = config.RAIZ / "poster"
PLANTILLA = CARPETA / "poster.html"
RENDER = CARPETA / "_render.html"
FINAL = CARPETA / f"{config.NOMBRE_BASE}.jpg"
TEXTOS = config.RAIZ / "contenido" / "textos.json"

ANCHO_PX, ALTO_PX = 7016, 9933  # A1 a 300 ppp
VISTA = (1754, 2483)
ESCALA = 4


def rellenar(plantilla, valores):
    """Reemplaza cada {{clave}}. Falla si alguna clave no tiene valor."""
    def reemplazo(m):
        clave = m.group(1)
        if clave not in valores:
            raise KeyError(clave)
        return valores[clave]

    return re.sub(r"\{\{(\w+)\}\}", reemplazo, plantilla)


def _entero(numero):
    return f"{numero:.0f}"


def valores_poster():
    t = json.loads(TEXTOS.read_text(encoding="utf-8"))
    c = cifras.leer()
    e = html.escape
    return {
        "titulo": e(t["titulo"]),
        "subtitulo": e(t["subtitulo"]),
        "cita_texto": e(t["cita"]["texto"]),
        "cita_traduccion": e(t["cita"]["traduccion"]),
        "cita_autor": e(t["cita"]["autor"]),
        "ideas_html": "".join(
            f'<div class="idea"><h3>{e(i["idea"])} <span>{e(i["autor"])}</span></h3>'
            f'<p>{e(i["texto"])}</p></div>'
            for i in t["ensayo"]),
        "shuicheng_html": " ".join(e(f) for f in t["shuicheng"]),
        "titulo_caso": e(t["titulo_caso"]),
        "datos_html": "".join(
            f'<p class="dato">{e(d["texto"])}<small>{e(d["fuente"])}</small></p>'
            for d in t["datos_sali"][0:4]),
        "paralelo_html": "".join(
            f'<tr><td>{e(p["shuicheng"])}</td><td>{e(p["sali"])}</td></tr>'
            for p in t["paralelo"]),
        "limites_html": "".join(f"<li>{e(x)}</li>" for x in t["limites"]),
        "referencias_html": " · ".join(e(x.rstrip(".")) for x in t["referencias"]) + ".",
        "aporte_html": "".join(f"<li>{e(x)}</li>" for x in t["aporte_gis"]),
        "integrantes_html": "<br>".join(e(n) for n in config.INTEGRANTES),
        "materia": e(config.MATERIA),
        "anio": e(config.ANIO),
        "propuesta_humedal": _entero(c["propuesta"]["humedal"]),
        "propuesta_bosque": _entero(c["propuesta"]["bosque"]),
        "propuesta_accesos": str(c["propuesta"]["accesos"]),
        "ribera_largo": _entero(c["ribera"]["largo_km"]),
        "ribera_construido": _entero(c["ribera"]["construido"]),
        "altura_pct": _entero(c["altura"]["pct_bajo"]),
        "umbral": _entero(c["altura"]["umbral_bajo_m"]),
    }


def exportar(pagina_html, destino):
    """Captura la página con Edge sin interfaz y la guarda como JPG A1 a 300 ppp."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge")
        pagina = navegador.new_page(viewport={"width": VISTA[0], "height": VISTA[1]},
                                    device_scale_factor=ESCALA)
        pagina.goto(pagina_html.resolve().as_uri())
        pagina.wait_for_load_state("networkidle")
        desborde = pagina.evaluate(
            "() => [...document.querySelectorAll('.poster > *')]"
            ".filter(el => el.scrollHeight > el.clientHeight + 2)"
            ".map(el => el.className + ': ' + el.scrollHeight + ' > ' + el.clientHeight)")
        captura = pagina.screenshot(type="png")
        navegador.close()
    imagen = Image.open(io.BytesIO(captura)).convert("RGB")
    if imagen.size != (ANCHO_PX, ALTO_PX):
        imagen = imagen.resize((ANCHO_PX, ALTO_PX), Image.LANCZOS)
    imagen.save(destino, "JPEG", quality=92, dpi=(300, 300), subsampling=0)
    return destino, desborde


def main():
    RENDER.write_text(rellenar(PLANTILLA.read_text(encoding="utf-8"), valores_poster()),
                      encoding="utf-8")
    destino, desborde = exportar(RENDER, FINAL)
    print(destino)
    if desborde:
        print("ATENCIÓN, secciones que desbordan:", desborde)


if __name__ == "__main__":
    main()
