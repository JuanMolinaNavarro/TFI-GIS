# Entrega: Geoempowering Design aplicado al Río Salí

Parcial 2 de 4K07 Sistemas de Información Geográfica (GIS), UTN, 2026.

## Archivos que se suben a la tarea

| Archivo | Qué es |
|---|---|
| `presentacion/PA2-Geoempowering-Design-MolinaNavarro.pptx` | Presentación de 11 diapositivas, 16:9, con el guion en las notas |
| `poster/PA2-Geoempowering-Design-MolinaNavarro.jpg` | Póster A1 vertical, 7016 × 9933 px, 300 ppp |

## Fechas

- Miércoles 18/11, 16 a 19 hs: exposición de póster, Hall Central UTN.
- Martes 24/11, 16.15 hs: evaluación, Lab 151 ISI. Subir los dos archivos antes.

## Lo que el grupo tiene que hacer a mano

1. **Avisar el tema en el grupo de WhatsApp.** Texto: `NN-Geoempowering Design-Molina Navarro-Zelarayan-Simon-Darelli`. Confirmar con la cátedra si `NN` es 13 (orden en el índice) o 48 (página).
2. **Abrir el `.pptx` en PowerPoint y revisarlo diapositiva por diapositiva.** En esta PC no hay PowerPoint, así que el diseño se verificó por geometría (nada fuera de la diapositiva ni superpuesto), pero no se vio renderizado.
3. **Diapositiva 4:** es solo texto. Si quieren sumar una foto del parque de humedales del Shuicheng, que sea con licencia y con el crédito de su autor.
4. **Imprimir el póster** en A1 color. Pedir impresión al 100 %, sin "ajustar a página".
5. **Ensayar los 10 minutos.** Cada diapositiva tiene su tiempo sugerido en las notas, y la diapositiva 10 trae seis preguntas previsibles con su respuesta.
6. **Revisar los nombres.** Están escritos tal como se informaron, sin tildes (Martin, Sebastian, Zelarayan, Simon, Agustin). Si llevan tilde, se cambian en `scripts/config.py`.

## Cifras del trabajo

Todas salen de `salidas/cifras.json`, que escriben los propios mapas.

| Dato | Valor |
|---|---|
| Tramo de río analizado | 31 km |
| Franja de ribera (500 m a cada lado) | 2.721 ha |
| Franja con cobertura vegetal | 57,1 % |
| Franja cultivada | 21,0 % |
| Franja edificada | 18,1 % |
| Franja a 2 m o menos sobre el cauce | 12,3 % (35,2 % sin corregir la cota del río) |
| Corredor de bosque de ribera | 582 ha (389 ya arboladas, 193 a restaurar) |
| Superficie apta para humedales | 109 ha |
| Posibles accesos (calles que llegan a 150 m del río) | 19 |

## Qué decir con cuidado

- El mapa 3 es un indicador topográfico, no un modelo de inundación.
- Las hectáreas son superficie apta según la regla, no terreno libre: parte ya tiene árboles o cultivos.
- "Cobertura vegetal" no distingue monte nativo de plantaciones.
- El modelo de elevación es de superficie (incluye árboles y techos), tiene 30 m de resolución y un error vertical del orden del umbral de 2 m. La cota del río se toma como el mínimo en 30 m y se le quitan las subidas aguas abajo; sin esa corrección el terreno bajo pasa de 12 % a 35 % de la franja. Decir ese rango.
- Los 19 accesos son posibles, no existentes: calles que hoy llegan a 150 m del río.
- La propuesta es un ejercicio académico, no un proyecto de obra.

## Cómo regenerar todo

Desde la carpeta del proyecto, en este orden:

```
.venv/Scripts/python -m scripts.descargar
.venv/Scripts/python -m scripts.procesar
.venv/Scripts/python -m scripts.mapa1_contexto
.venv/Scripts/python -m scripts.mapa2_ribera
.venv/Scripts/python -m scripts.mapa3_altura
.venv/Scripts/python -m scripts.mapa4_propuesta
.venv/Scripts/python -m scripts.esquema_infra
.venv/Scripts/python -m scripts.exportar_poster
.venv/Scripts/python -m presentacion.crear_pptx
.venv/Scripts/python -m pytest
```

Para cambiar el tramo, la franja o los umbrales, editar `scripts/config.py` y volver a correr desde `procesar`. Los textos del póster y de la presentación están en `contenido/textos.json`.

## Fuentes de datos

Instituto Geográfico Nacional (WFS), OpenStreetMap, ESA WorldCover 2021 (10 m), Copernicus DEM GLO-30 e HydroBASINS. Las direcciones y fechas de descarga están en `datos/crudos/FUENTES.md`. Los datos sobre el estado del Salí salen de Argentina.gob.ar (Cuenca del Río Salí Dulce) y de La Gaceta (23/03/2019).
