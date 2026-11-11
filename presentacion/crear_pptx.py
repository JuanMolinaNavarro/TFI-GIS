"""Genera la presentación (11 diapositivas, 16:9) con python-pptx."""
import json

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from scripts import cifras, config

Image.MAX_IMAGE_PIXELS = None
P = config.PALETA
TEXTOS = config.RAIZ / "contenido" / "textos.json"
SALIDA = config.RAIZ / "presentacion" / f"{config.NOMBRE_BASE}.pptx"
RECORTES = config.SALIDAS / "diapositivas"
ANCHO, ALTO = 13.333, 7.5
MARGEN = 0.6
# Parte de cada mapa que se usa en la diapositiva: solo el mapa, sin título, panel ni pie
RECORTE = (0.035, 0.132, 0.545, 0.935)


def color(clave):
    return RGBColor.from_string(P[clave].lstrip("#"))


def coma(numero, decimales=1):
    return f"{numero:.{decimales}f}".replace(".", ",")


def recortar(nombre):
    """Recorta el mapa compuesto y devuelve (ruta, ancho/alto)."""
    RECORTES.mkdir(parents=True, exist_ok=True)
    im = Image.open(config.MAPAS / f"{nombre}.png")
    w, h = im.size
    caja = (int(RECORTE[0] * w), int(RECORTE[1] * h), int(RECORTE[2] * w), int(RECORTE[3] * h))
    im = im.crop(caja)
    im.thumbnail((2600, 2600))
    ruta = RECORTES / f"{nombre}.png"
    im.save(ruta)
    return ruta, im.size[0] / im.size[1]


class Mazo:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(ANCHO)
        self.prs.slide_height = Inches(ALTO)

    def nueva(self, titulo=None, notas=""):
        d = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        fondo = d.background.fill
        fondo.solid()
        fondo.fore_color.rgb = color("fondo")
        if titulo:
            self.texto(d, titulo, MARGEN, 0.4, ANCHO - 2 * MARGEN, 0.9, tam=36, negrita=True)
            barra = d.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(MARGEN), Inches(1.28),
                                       Inches(1.1), Inches(0.07))
            barra.fill.solid()
            barra.fill.fore_color.rgb = color("acento")
            barra.line.fill.background()
        d.notes_slide.notes_text_frame.text = notas
        return d

    def texto(self, d, contenido, x, y, w, h, tam=20, negrita=False, clave="tinta",
              alinear=PP_ALIGN.LEFT, ancla=MSO_ANCHOR.TOP, espacio=6):
        """Caja de texto. `contenido` es un string o una lista de párrafos."""
        caja = d.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        marco = caja.text_frame
        marco.word_wrap = True
        marco.vertical_anchor = ancla
        for lado in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(marco, lado, 0)
        parrafos = contenido if isinstance(contenido, list) else [contenido]
        for i, linea in enumerate(parrafos):
            p = marco.paragraphs[0] if i == 0 else marco.add_paragraph()
            p.alignment = alinear
            p.space_after = Pt(espacio)
            r = p.add_run()
            r.text = linea
            r.font.size = Pt(tam)
            r.font.bold = negrita
            r.font.name = config.FUENTE
            r.font.color.rgb = color(clave)
        return caja

    def imagen(self, d, ruta, x, y, w=None, h=None):
        return d.shapes.add_picture(str(ruta), Inches(x), Inches(y),
                                    Inches(w) if w else None, Inches(h) if h else None)

    def mapa(self, titulo, nombre, numero, clave, frase, puntos, notas):
        """Diapositiva de mapa: imagen a la izquierda, cifra y lectura a la derecha."""
        d = self.nueva(titulo, notas)
        ruta, proporcion = recortar(nombre)
        alto = 5.75
        ancho = alto * proporcion
        self.imagen(d, ruta, MARGEN, 1.5, h=alto)
        x = MARGEN + ancho + 0.4
        w = ANCHO - x - MARGEN
        self.texto(d, numero, x, 1.55, w, 1.0, tam=54, negrita=True, clave=clave)
        self.texto(d, frase, x, 2.65, w, 1.2, tam=22, negrita=True)
        self.texto(d, puntos, x, 4.0, w, 3.0, tam=20, espacio=10)
        return d


def construir():
    t = json.loads(TEXTOS.read_text(encoding="utf-8"))
    c = cifras.leer()
    rib, alt, pro = c["ribera"], c["altura"], c["propuesta"]
    m = Mazo()
    ancho_util = ANCHO - 2 * MARGEN

    # 1. Portada
    d = m.nueva(notas="Presentación del grupo y del tema. Decir en una frase de qué se trata: "
                      "tomamos el ensayo Geoempowering Design y lo aplicamos al Río Salí. (20 s)")
    franja = d.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.35), Inches(ALTO))
    franja.fill.solid()
    franja.fill.fore_color.rgb = color("agua")
    franja.line.fill.background()
    m.texto(d, t["titulo"], 1.0, 1.5, 11.5, 1.4, tam=66, negrita=True)
    m.texto(d, t["subtitulo"], 1.0, 2.95, 11.5, 0.8, tam=32, negrita=True, clave="agua")
    m.texto(d, t["bajada"], 1.0, 3.7, 11.5, 0.6, tam=22)
    m.texto(d, config.INTEGRANTES, 1.0, 4.9, 5.5, 1.8, tam=20, negrita=True, espacio=2)
    m.texto(d, [config.MATERIA, f"UTN · {config.ANIO}"], 7.0, 5.65, 5.7, 1.0, tam=20,
            alinear=PP_ALIGN.RIGHT, espacio=2)

    # 2. Geodiseño
    d = m.nueva("¿Qué es el geodiseño?",
                "El geodiseño une dos cosas: el poder analítico del GIS y los métodos creativos "
                "del diseño. Primero entendemos cómo es y cómo funciona un lugar; después "
                "proyectamos cómo podría ser. Dangermond dice que el GIS es la plataforma que "
                "integra la ciencia y le da poder al diseño: de ahí el título, geoempowering. "
                "Leer la cita de Fisher. (50 s)")
    m.texto(d, "GIS", 0.6, 1.9, 3.6, 0.8, tam=44, negrita=True, clave="agua")
    m.texto(d, "Entender lo que es", 0.6, 2.75, 3.6, 0.6, tam=24)
    m.texto(d, "+", 4.2, 1.9, 0.8, 0.8, tam=44, negrita=True, alinear=PP_ALIGN.CENTER)
    m.texto(d, "Diseño", 5.2, 1.9, 3.6, 0.8, tam=44, negrita=True, clave="vegetacion")
    m.texto(d, "Proyectar lo que podría ser", 5.2, 2.75, 4.2, 0.6, tam=24)
    m.texto(d, "=", 9.3, 1.9, 0.8, 0.8, tam=44, negrita=True, alinear=PP_ALIGN.CENTER)
    m.texto(d, "Geodiseño", 10.1, 1.9, 3.0, 0.8, tam=40, negrita=True, clave="humedal")
    barra = d.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(4.35), Inches(0.09),
                               Inches(1.9))
    barra.fill.solid()
    barra.fill.fore_color.rgb = color("acento")
    barra.line.fill.background()
    m.texto(d, [f"«{t['cita']['traduccion']}»"], 0.95, 4.3, 11.5, 1.1, tam=30, negrita=True)
    m.texto(d, [f"“{t['cita']['texto']}”", t["cita"]["autor"]], 0.95, 5.45, 11.5, 0.9, tam=20,
            espacio=2)

    # 3. Infraestructura ecológica
    d = m.nueva("Infraestructura ecológica, no hormigón",
                "La idea central de Kongjian Yu: en vez de sacar el agua rápido con caños y "
                "canales, se la retiene y se la filtra en humedales en terrazas. Lo que "
                "históricamente se inundaba se deja inundar. En el mismo encuentro, Benyus "
                "propone la biomímesis: tomar a la naturaleza como mentora, que una ciudad "
                "funcione como un bosque. (50 s)")
    with Image.open(config.MAPAS / "esquema_infra.png") as im:
        prop = im.size[0] / im.size[1]
    m.imagen(d, config.MAPAS / "esquema_infra.png", MARGEN, 1.6, w=ancho_util)
    m.texto(d, "Lo que históricamente se inundaba, se deja inundar.",
            MARGEN, 1.6 + ancho_util / prop + 0.3, ancho_util, 0.7, tam=26, negrita=True,
            clave="agua")

    # 4. Shuicheng
    d = m.nueva("Kongjian Yu y el río Shuicheng",
                "Yu es hijo de agricultores, fundó Turenscape y usa GIS desde hace décadas para "
                "modelar el relieve. El ejemplo del ensayo es el río Shuicheng, en Liupanshui: "
                "estaba contaminado y encauzado en hormigón. Sacaron el hormigón, dejaron crecer "
                "vegetación natural y hoy es un humedal nacional donde se puede pescar. (40 s)")
    m.texto(d, ["Río contaminado y encauzado en hormigón.",
                "Se retira el hormigón y vuelve la vegetación natural.",
                "El agua de lluvia vuelve al río por humedales en terrazas.",
                "Resultado: un humedal nacional, otra vez pescable."],
            MARGEN, 1.9, ancho_util, 4.5, tam=28, espacio=22)

    # 5. Paralelo
    dato = t["datos_sali"][2]
    d = m.nueva("Del Shuicheng al Salí",
                "El mismo problema, en casa. El Salí recibe residuos de ingenios, destilerías y "
                "cloacas; su ribera está fragmentada entre lo edificado y lo cultivado. Y el efecto "
                "llega aguas abajo, hasta el embalse de Río Hondo. La pregunta es si la receta "
                "de Yu se puede ensayar acá con datos abiertos. (50 s)")
    m.texto(d, "RÍO SHUICHENG", MARGEN, 1.65, 5.8, 0.4, tam=20, negrita=True, clave="agua")
    m.texto(d, "RÍO SALÍ", 6.9, 1.65, 5.8, 0.4, tam=20, negrita=True, clave="construido")
    y = 2.2
    for fila in t["paralelo"]:
        linea = d.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(MARGEN), Inches(y - 0.08),
                                   Inches(ancho_util), Inches(0.015))
        linea.fill.solid()
        linea.fill.fore_color.rgb = color("tinta")
        linea.line.fill.background()
        m.texto(d, fila["shuicheng"], MARGEN, y, 5.8, 0.9, tam=22)
        m.texto(d, fila["sali"], 6.9, y, 5.8, 0.9, tam=22)
        y += 1.0
    m.texto(d, [dato["texto"], f"Fuente: {dato['fuente']}"], MARGEN, 5.55, ancho_util, 1.4,
            tam=20, clave="agua", espacio=2)

    # 6 a 9. Mapas
    m.mapa("¿Cómo es el territorio?", "mapa1_contexto", "Río Salí", "agua",
           "El eje hídrico de Tucumán",
           ["Recorre la provincia de norte a sur.",
            "Atraviesa su mayor área urbana.",
            "Desemboca en el embalse de Río Hondo."],
           "Primer paso del geodiseño: describir. El Salí es el eje de la cuenca Salí-Dulce, "
           "que ocupa unas tres cuartas partes de la provincia. Pasa por el Gran San Miguel de Tucumán y termina "
           "en el embalse de Río Hondo. El recuadro amarillo es nuestro tramo de estudio: "
           f"{coma(rib['largo_km'], 0)} km de río frente a la ciudad. (1 min)")
    m.mapa("¿Funciona bien?", "mapa2_ribera", f"{coma(rib['vegetacion'])} %", "vegetacion",
           "de la franja de ribera tiene cobertura vegetal",
           [f"Franja de {rib['franja_m']} m a cada lado del río.",
            f"{coma(rib['construido'])} % ya está edificado.",
            f"{coma(rib['cultivo'])} % está cultivado."],
           "Segundo paso: evaluar. Tomamos una franja de 500 m a cada lado del río y medimos "
           "qué hay con una cobertura satelital de 10 m. Más de la mitad tiene cobertura "
           "vegetal, pero ojo: el dato no distingue monte nativo de plantaciones. En el tramo "
           "céntrico la ribera está edificada casi hasta el agua. (1 min 10 s)")
    m.mapa("¿Cómo funciona el agua?", "mapa3_altura", f"{coma(alt['pct_bajo'], 0)} %", "agua",
           f"de la franja está a {coma(alt['umbral_bajo_m'], 0)} m o menos sobre el cauce",
           ["Indicador topográfico, no un modelo hidráulico de inundación.",
            "Modelo de superficie de 30 m: incluye árboles y techos.",
            f"Según cómo se tome la cota del río, va de {coma(alt['pct_bajo'], 0)} a "
            f"{coma(alt['pct_bajo_sin_corregir'], 0)} %."],
           "Tercer paso: entender el proceso. Con un modelo de elevación calculamos cuánto más "
           "alto está cada punto respecto del río. Aclarar antes de que pregunten: esto no es "
           "un mapa de inundación, no simula caudales. El modelo es de superficie, así que "
           "tomamos como cota del río el mínimo local y le quitamos las subidas aguas abajo. "
           f"Sin esa corrección la cifra sube a {coma(alt['pct_bajo_sin_corregir'], 0)} %: "
           "decir el rango nosotros mismos. (1 min 10 s)")
    m.mapa("¿Cómo podría cambiar?", "mapa4_propuesta", f"{pro['bosque']:.0f} ha", "vegetacion",
           f"de corredor de bosque de ribera: {pro['bosque_existente']:.0f} ya arboladas, "
           f"{pro['bosque_restaurar']:.0f} a restaurar",
           [f"{pro['humedal']:.0f} ha aptas para humedales en terrazas.",
            f"{pro['accesos']} posibles accesos: calles que llegan a "
            f"{config.ACCESO_DIST_M} m del río.",
            "Superficie apta, no terreno disponible."],
           "Acá pasamos de GIS a geodiseño. La regla es explícita: bosque de ribera en los "
           f"primeros {pro['ancho_bosque_m']} m junto al cauce, y humedales en el terreno que "
           f"está a {coma(pro['umbral_bajo_m'], 0)} m o menos, siempre sin tocar lo edificado. "
           "Los posibles accesos son calles existentes que hoy llegan cerca del río. Son "
           "superficies aptas, no terrenos libres: es un ejercicio académico y un techo "
           "para discutir. (1 min 30 s)")

    # 10. Aporte y límites
    preguntas = "\n\n".join(f"P: {p['pregunta']}\nR: {p['respuesta']}"
                            for p in t["preguntas_previsibles"])
    d = m.nueva("Qué aporta el GIS, y sus límites",
                "Cierre: el GIS integró datos distintos en una misma grilla, convirtió una idea "
                "en una regla revisable y midió el resultado. Y decir los límites nosotros "
                "mismos. (40 s)\n\nPREGUNTAS PREVISIBLES\n\n" + preguntas)
    m.texto(d, "Aporta", MARGEN, 1.7, 5.8, 0.5, tam=26, negrita=True, clave="agua")
    m.texto(d, t["aporte_gis"], MARGEN, 2.35, 5.8, 4.8, tam=20, espacio=12)
    m.texto(d, "Límites", 6.9, 1.7, 5.8, 0.5, tam=26, negrita=True, clave="construido")
    m.texto(d, t["limites"], 6.9, 2.35, 5.8, 4.8, tam=20, espacio=12)

    # 11. Fuentes
    d = m.nueva("Fuentes", "Mencionar que todos los datos son abiertos y que el análisis se "
                           "puede reproducir de punta a punta. Agradecer y abrir a preguntas. "
                           "(15 s)")
    m.texto(d, t["referencias"], MARGEN, 1.7, ancho_util, 5.3, tam=18, espacio=8)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    m.prs.save(SALIDA)
    return SALIDA


if __name__ == "__main__":
    print(construir())
