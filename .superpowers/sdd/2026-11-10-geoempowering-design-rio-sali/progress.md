# SDD ledger — plan: docs/superpowers/plans/2026-11-10-geoempowering-design-rio-sali.md
Setup: Ruling: sin git ni worktree (la carpeta no es un repositorio y el usuario no pidió git); los scripts task-start/task-done no se usan y el avance se anota a mano — costo si está mal: no hay historial para revertir.
Pre-flight: T1 config -> T2..T11 (constantes y rutas): consistente. T4 analisis -> T6/T7/T8: firmas consistentes. T6 cifras.guardar/leer -> T8/T10/T11: consistente. T3 procesar escribe dem/cobertura -> T7 agrega altura/distancia en procesar: consistente.
Task 1: complete (tests: pytest tests/test_config.py -> 5 passed; Python 3.14 instaló todo)
Task 2: complete (tests: pytest tests/test_descargar.py -> 4 passed; descarga real OK, URLs del IGN y HydroBASINS confirmadas)
Task 3: Ruling: altura_cauce.tif y distancia_cauce.tif se calculan ya en procesar (paso 1 de Task 7 adelantado) para poder proponer el umbral en el punto de control — costo si está mal: ninguno, es el mismo código.
Task 3: Ruling: se agregó config.PROV_BBOX y config.COTA_RIO_VENTANA_M (=0) no previstos en el plan — necesarios para descarga provincial y para la alternativa del DEM — costo: ninguno.
Task 3: pasos 1-5 completos (pytest tests/test_procesar.py -> 2 passed; grillas alineadas; río LineString 31 km). Altura en franja p25=1.1 m, p50=3.3 m. Pendiente: punto de control con el usuario.
Task 4: complete (tests: pytest tests/test_analisis.py -> 8 passed)
Task 5: Ruling: el Salí del mapa 1 sale de OSM a escala provincial (osm_rio_prov.geojson, capa rio_prov) porque el IGN no nombra "Salí" el tramo completo — costo: ninguno, fuente ya citada.
Task 5: Ruling: nuevo_mapa acepta `caja` y estilo expone CAJA_IZQUIERDA/PANEL_X y encuadrar() para los mapas verticales del área de estudio — costo: ninguno.
Task 5: pasos 1-6 completos (pytest -> 20 passed; mapa1 revisado). Pendiente: visto bueno del usuario.
Hallazgo para Task 7: la altura sobre el cauce muestra cuñas y valores falsos lejos del río (asignación a la celda de río más cercana sobre un terreno con pendiente N-S). El mapa 3 debe mostrar el indicador solo cerca del cauce.
Task 3: complete (usuario aprobó tramo, franja 500 m y UMBRAL_BAJO_M=2.0)
Task 6: complete salvo visto bueno (pytest tests/test_cifras.py -> 2 passed; porcentajes suman 99.9). Ruling: el texto dice "tiene cobertura vegetal" y no "conserva vegetación" porque WorldCover no distingue monte nativo de plantaciones — costo: ninguno.
Task 7: complete salvo visto bueno. Ruling: el mapa 3 muestra la altura solo dentro de la franja (no en todo el AOI) por los artefactos lejos del cauce — costo: menos contexto visual.
Task 8: complete salvo visto bueno (pytest tests/test_accesos.py -> 2 passed; sin humedales con umbral -100 el mapa se genera con 0.0 ha). Hallazgo: bosque de ribera = 17 ha, porque casi toda la franja contigua al cauce ya es humedal candidato o tiene árboles.
Task 8: Ruling (pedido del usuario): bosque = franja continua de 100 m junto al cauce; humedal = terreno bajo más allá. Spec actualizado. test_zonificar_bosque_continuo... RED->GREEN.
Task 9: complete salvo visto bueno (pytest tests/test_contenido.py -> 2 passed; 5 datos del Salí con fuente abierta y verificada: argentina.gob.ar y La Gaceta 2019). Ruling: sin fotos del Shuicheng; esquema propio.
Task 10: complete salvo visto bueno (pytest tests/test_poster.py -> 5 passed; JPG 7016x9933, 300 ppp; revisado completo y al 100%). Ruling: título a 100 px (no 110) para que entre en una línea — costo: ninguno visible. Ruling: el bloque de cifras a la derecha se reemplazó por 'Qué aporta el GIS' porque duplicaba los números del mapa 4. Queda un desborde de 5 px en la sección propuesta, dentro del espacio entre filas.
Task 11: complete salvo revisión visual (pytest tests/test_pptx.py -> 5 passed). Ruling: sin PowerPoint ni LibreOffice en la PC, el diseño se verificó por geometría y no renderizado — costo: puede haber un desborde de texto que solo se ve al abrirlo. Ruling: diapositiva de fuentes a 18 pt (no 20) para que entren las 8 referencias.
Task 12: complete (regeneración completa OK; pytest -> 36 passed). ENTREGA.md escrito.
Final review: self-review (sin subagente; la sesión no lanza agentes salvo pedido del usuario).
Final review: revisor independiente (subagente), sin hallazgos críticos, 9 importantes.
Final: fixed cota del río mal resuelta (H1) — test_perfil_descendente_*, test_cota_del_rio_* RED→GREEN; COTA_RIO_VENTANA_M=30; franja baja 35,2 % → 12,3 %, humedal 475 → 109 ha; rango declarado en mapa 3, diapositiva 8 y ENTREGA.
Final: fixed respuesta preparada del umbral (H2), frase de inundación del mapa 3 (H3), "accesos públicos" → "posibles accesos" (H4), afirmaciones sin fuente (H5), bosque existente/a restaurar (H6) — test_cobertura_por_zona_separa_lo_ya_arbolado RED→GREEN, recuadro de la diapositiva 4 (H7), doble cifra en diapositivas 7-9 (H8), autores en el póster (H9). Suite 40/40.
Final: Ruling: se mantiene el umbral de 2 m aprobado por el usuario aunque la corrección baja mucho el humedal — costo: propuesta de humedal modesta; lo decide el usuario.
Final: minor (deferred): texto interno chico en los mapas 1-3 del póster.
Final: minor (deferred): franja_ha con all_touched (+1,2 %); porcentajes suman 99,9.
Final: minor (deferred): FUENTES.md no lista osm_rio_prov.geojson; overpass/recorte_remoto sin validar respuestas parciales.
Final: minor (deferred): pruebas de Review Focus 4 y 5 parcialmente triviales; quitar_parches_chicos sin prueba.
Final: minor (deferred): nombres sin tildes; dato del Comité 2007 sin usar.
