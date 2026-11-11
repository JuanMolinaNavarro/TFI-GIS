# Geoempowering Design aplicado al Río Salí (Tucumán)

Spec de diseño. Parcial 2 de 4K07 Sistemas de Información Geográfica (GIS), UTN, 2º semestre 2026.

Fecha del spec: 10/11/2026.

## 1. Objetivo

Exponer el ensayo *Geoempowering Design* (Essays on Geography and GIS, vol. 7, Esri, 2014, pág. 48) y aplicarlo a una situación local: el tramo urbano del Río Salí frente al Gran San Miguel de Tucumán, repensado como corredor ecológico mediante geodiseño.

El trabajo tiene éxito si cumple los criterios de evaluación de la consigna:

- claridad del tema presentado;
- capacidad de relacionar el tema con una situación local en la Provincia;
- respuesta a las preguntas del curso;
- calidad de diseño del póster;
- calidad de diseño de la presentación.

## 2. Grupo y nombres de archivo

Integrantes:

- Juan Martin Molina Navarro
- Sebastian Zelarayan
- Juan Simon
- Agustin Darelli

Archivos a entregar:

- `PA2-Geoempowering-Design-MolinaNavarro.pptx`
- `PA2-Geoempowering-Design-MolinaNavarro.jpg`

Rótulo del póster (margen inferior derecho): los cuatro integrantes, "4K07 Sistemas de Información Geográfica (GIS)", "2026".

Aviso al grupo de WhatsApp del curso: `NN-Geoempowering Design-Molina Navarro-Zelarayan-Simon-Darelli`. El número `NN` hay que confirmarlo con la cátedra: el ensayo es el 13º título del índice y está en la página 48, y la consigna no aclara cuál de los dos se usa.

## 3. Fechas

| Fecha | Hito |
|---|---|
| Miércoles 18/11/2026, 16 a 19 hs | Exposición de póster, Hall Central UTN |
| Antes del 24/11/2026 | Subir `.pptx` y `.jpg` a la tarea |
| Martes 24/11/2026, 16.15 hs | Evaluación, Lab 151 ISI |

## 4. Contenido del ensayo a transmitir

- **Geodiseño:** unión del poder analítico del GIS con los métodos creativos del diseño. El GIS ayuda a entender lo que es y a diseñar lo que podría ser (Thomas Fisher).
- **GIS como plataforma:** integra la ciencia y da el medio práctico para "geoempoderar" el diseño (Jack Dangermond).
- **Infraestructura ecológica:** refleja el ambiente natural en lugar de hormigón y acero. El agua de lluvia se captura y filtra en humedales en terrazas, y lo que históricamente se inundaba se deja inundar (Kongjian Yu, Turenscape).
- **Caso del ensayo:** río Shuicheng y parque de humedales Minghu, en Liupanshui (China). Se retiraron los terraplenes de hormigón, se replantó vegetación nativa y un curso contaminado volvió a ser pescable.
- **Biomímesis:** la naturaleza como mentora; hacen falta métricas para definir estándares de desempeño ecológico (Janine Benyus).
- **Herramientas mencionadas:** CityEngine, ArcGIS Pro, Landscape Planner. Se nombran, no se desarrollan.

## 5. Caso local: Río Salí

### 5.1 Área de estudio

Tramo urbano del Salí entre San Miguel de Tucumán (margen oeste) y Banda del Río Salí / Alderetes (margen este), con una franja de ribera a cada lado del cauce.

La extensión exacta del tramo y el ancho de la franja se fijan en el primer paso de implementación, al ver los datos, y se registran en un único archivo de configuración que usan todos los scripts.

### 5.2 Enfoque

Diagnóstico → propuesta, siguiendo las preguntas del geodiseño. Cada mapa responde una pregunta.

### 5.3 Mapas

| # | Pregunta | Contenido | Datos |
|---|---|---|---|
| 1 | ¿Cómo es el territorio? | Cuenca Salí-Dulce dentro de la provincia, red hídrica, manchas urbanas, área de estudio | IGN, OpenStreetMap |
| 2 | ¿Funciona bien? | Cobertura del suelo en la franja de ribera: construido, suelo desnudo, vegetación, agua. Incluye el porcentaje de la franja en cada clase | ESA WorldCover 10 m |
| 3 | ¿Cómo funciona el agua? | Altura del terreno respecto del cauce | Copernicus DEM GLO-30 |
| 4 | ¿Cómo podría cambiar? | Corredor ecológico: corredor de bosque de ribera, humedales en terrazas, posibles accesos. Incluye hectáreas por zona | Derivado de los mapas 2 y 3 |

Regla de la propuesta (mapa 4):

- **Bosque de ribera:** franja continua de 100 m junto al cauce, donde no esté construido ni sea agua.
- **Humedal en terrazas:** más allá del bosque, terreno a 2 m o menos sobre el cauce y no construido.
- **Accesos públicos:** puntos donde la trama vial existente llega a la ribera.

Los umbrales numéricos (altura sobre el cauce, ancho de franja) se eligen al ver los datos y se documentan en el mapa y en las notas del orador.

### 5.4 Límites que se declaran

- El mapa 3 es un indicador topográfico, no un modelo hidráulico de inundación. No se presenta como mapa de riesgo.
- El modelo de elevación es de superficie. La cota del río se toma como el mínimo local en 30 m, sin subidas aguas abajo, y se informa el rango respecto del valor sin corregir.
- Las hectáreas son superficie apta según la regla, no terreno disponible.
- La propuesta es un ejercicio académico de geodiseño, no un proyecto de obra.
- La resolución de los datos (10 m y 30 m) alcanza para escala de corredor, no de parcela.

### 5.5 Datos sobre el Salí

Toda cifra o afirmación sobre contaminación, fuentes de vertido o efectos aguas abajo lleva una fuente citable. Lo que no tenga fuente no entra en la presentación ni en el póster.

## 6. Entregables

### 6.1 Mapas

Cuatro imágenes PNG en alta resolución en `salidas/mapas/`, con título, leyenda, escala gráfica, norte y fuente de datos. Una sola paleta y tipografía para los cuatro.

### 6.2 Presentación

Generada con python-pptx, formato 16:9, 11 diapositivas:

1. Título
2. Qué es el geodiseño
3. Infraestructura ecológica contra hormigón
4. Kongjian Yu y el río Shuicheng
5. Paralelo Shuicheng ↔ Salí
6. Mapa 1
7. Mapa 2
8. Mapa 3
9. Mapa 4
10. Qué aporta el GIS y límites del análisis
11. Fuentes

Reparto del tiempo: ensayo 3 min, paralelo 1 min, caso 5 min, cierre 1 min.

Poco texto por diapositiva y mapas a pantalla completa. El detalle va en notas del orador, incluidas respuestas preparadas a preguntas previsibles.

### 6.3 Póster

- A1 vertical, 594 × 841 mm, 7016 × 9933 px a 300 ppp, JPG color.
- Se arma en HTML y se exporta a imagen en ese tamaño exacto.
- Estructura: franja de título; columna con la idea del ensayo; mapa 4 como pieza central; mapas 1 a 3 en tamaño menor, cada uno con su pregunta; rótulo abajo a la derecha.
- Misma paleta y tipografía que la presentación.
- La consigna pide imprimirlo. Se reserva el 17/11 para la impresión.

## 7. Herramientas y estructura

Python con geopandas, rasterio, shapely y matplotlib para datos y mapas; python-pptx para la presentación; HTML más un navegador sin interfaz para exportar el póster.

```
TFI-GIS/
  datos/crudos/        descargas sin modificar
  datos/procesados/    capas recortadas al área de estudio
  scripts/             configuración, descarga, procesamiento y un script por mapa
  salidas/mapas/       los 4 mapas
  poster/              HTML del póster y .jpg final
  presentacion/        script generador y .pptx final
  docs/                spec y plan
```

Cada mapa tiene su propio script y depende solo de `datos/procesados/` y de la configuración común. Se puede rehacer un mapa sin tocar los demás.

## 8. Calendario de trabajo

| Fecha | Trabajo |
|---|---|
| 10 y 11/11 | Entorno, datos, área de estudio, mapas 1 y 2 |
| 12 y 13/11 | Mapas 3 y 4 |
| 14 y 15/11 | Póster |
| 16/11 | Revisión del grupo y ajustes |
| 17/11 | Margen e impresión |
| 18/11 | Exposición de póster |
| 19 a 22/11 | Presentación y notas del orador |
| 23/11 | Ensayo de los 10 minutos |
| 24/11 | Evaluación |

## 9. Controles

- Cada mapa se revisa renderizado antes de darlo por bueno, y el grupo lo aprueba antes de que entre al póster.
- Del póster se verifican las dimensiones en píxeles y los 300 ppp en el archivo final.
- El `.pptx` se abre y se revisa diapositiva por diapositiva.
- Cada cifra del póster y de la presentación se coteja con su fuente.

## 10. Riesgos

| Riesgo | Respuesta |
|---|---|
| Una librería geoespacial no instala en Python 3.14 | Crear un entorno con una versión anterior de Python |
| WorldCover clasifica mal la ribera | Clasificar una imagen Sentinel-2 del área |
| Un servicio de datos no responde | Usar una fuente alternativa equivalente y registrarla |
| El DEM de 30 m no distingue bien el cauce | Usar la traza del río de IGN u OSM como referencia de altura |

## 11. Fuera de alcance

- Demo interactiva o mapa web.
- Modelación hidráulica o hidrológica.
- Análisis multicriterio ponderado.
- Trabajo en ArcGIS o QGIS.
- Relevamiento de campo.
