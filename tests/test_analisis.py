import numpy as np

from scripts import analisis


def test_porcentajes_ignoran_nodata_y_suman_100():
    cob = np.array([[10, 50, 0], [80, 60, 40]], dtype=np.uint8)
    p = analisis.porcentajes_cobertura(cob, np.ones_like(cob, dtype=bool))
    assert p == {"vegetacion": 20.0, "cultivo": 20.0, "construido": 20.0,
                 "desnudo": 20.0, "agua": 20.0}


def test_porcentajes_respetan_mascara():
    cob = np.array([[10, 50], [50, 50]], dtype=np.uint8)
    mascara = np.array([[True, True], [False, False]])
    p = analisis.porcentajes_cobertura(cob, mascara)
    assert p["vegetacion"] == 50.0 and p["construido"] == 50.0


def test_porcentajes_sin_pixeles_validos():
    cob = np.zeros((2, 2), dtype=np.uint8)
    assert set(analisis.porcentajes_cobertura(cob, np.ones((2, 2), bool)).values()) == {0.0}


def test_distancia_y_altura():
    dem = np.array([[105., 100., 103.], [106., 101., -9999.]], dtype=np.float32)
    rio = np.array([[False, True, False], [False, True, False]])
    dist, alt = analisis.distancia_y_altura(dem, rio, 10)
    assert dist[0].tolist() == [10.0, 0.0, 10.0]
    assert alt[0].tolist() == [5.0, 0.0, 3.0]
    assert alt[1, 0] == 5.0 and np.isnan(alt[1, 2])


def test_zonificar_bosque_continuo_junto_al_cauce_y_humedal_mas_alla():
    #                 pastizal edificado desnudo pastizal arboles cultivo  agua
    cob = np.array([[30, 50, 60, 30, 10, 40, 80]], dtype=np.uint8)
    altura = np.array([[1.0, 1.0, 8.0, 8.0, 8.0, 1.0, 0.0]])
    distancia = np.array([[20., 20., 50., 300., 50., 300., 0.]])
    franja = np.ones((1, 7), bool)
    z = analisis.zonificar(cob, altura, distancia, franja, 3.0, 100)
    assert z.tolist() == [[2, 0, 2, 0, 2, 1, 0]]


def test_zonificar_fuera_de_franja_es_cero():
    z = analisis.zonificar(np.array([[30]], np.uint8), np.array([[1.0]]),
                           np.array([[10.]]), np.zeros((1, 1), bool), 3.0, 100)
    assert z.tolist() == [[0]]


def test_hectareas_sin_candidatos():
    assert analisis.hectareas_por_zona(np.zeros((10, 10), np.uint8), 10) == {
        "humedal": 0.0, "bosque": 0.0}


def test_hectareas():
    z = np.zeros((10, 10), np.uint8)
    z[0] = 1
    z[1, :5] = 2
    assert analisis.hectareas_por_zona(z, 100) == {"humedal": 10.0, "bosque": 5.0}


def test_perfil_descendente_quita_subidas_aguas_abajo():
    cotas = np.array([10.0, 12.0, 9.0, 9.5, 7.0])
    assert analisis.perfil_descendente(cotas).tolist() == [10.0, 10.0, 9.0, 9.0, 7.0]


def test_perfil_descendente_detecta_el_sentido_del_rio():
    cotas = np.array([7.0, 9.5, 9.0, 12.0, 10.0])
    assert analisis.perfil_descendente(cotas).tolist() == [7.0, 9.0, 9.0, 10.0, 10.0]


def test_cota_del_rio_usa_minimo_local_y_perfil_descendente():
    # Río vertical en la columna 1; el eje pasa por celdas "altas" (árboles) salvo el agua al lado
    dem = np.array([[20., 14., 10.],
                    [20., 15., 13.],
                    [20., 12., 8.]])
    rio = np.zeros((3, 3), bool)
    rio[:, 1] = True
    orden = np.array([0.0, 10.0, 20.0])  # posición a lo largo del río de cada celda de río
    cotas = analisis.cota_del_rio(dem, rio, orden, ventana_px=1)
    # mínimos locales en ventana de 3x3: 10, 8, 8 (la fila central ve el 8 de abajo)
    assert cotas.tolist() == [10.0, 8.0, 8.0]


def test_cobertura_por_zona_separa_lo_ya_arbolado():
    zonas = np.array([[2, 2, 2, 1, 0]], dtype=np.uint8)
    cob = np.array([[10, 10, 30, 40, 10]], dtype=np.uint8)
    r = analisis.bosque_existente_y_a_restaurar(zonas, cob, 100)
    assert r == {"bosque_existente": 2.0, "bosque_restaurar": 1.0}
