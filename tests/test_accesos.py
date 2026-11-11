import geopandas as gpd
from shapely.geometry import LineString

from scripts import analisis


def test_puntos_de_acceso_separa_por_distancia():
    rio = LineString([(0, 0), (0, 2000)])
    vias = gpd.GeoSeries([LineString([(-500, y), (-10, y)]) for y in (100, 300, 900)])
    pts = analisis.puntos_de_acceso(vias, rio, dist_m=150, separacion_m=500)
    assert [round(p.y) for p in pts] == [100, 900]
    assert all(round(p.x) == -150 for p in pts)


def test_puntos_de_acceso_cada_margen_por_separado():
    rio = LineString([(0, 0), (0, 2000)])
    vias = gpd.GeoSeries([LineString([(-500, 100), (-10, 100)]),
                          LineString([(500, 200), (10, 200)])])
    pts = analisis.puntos_de_acceso(vias, rio, dist_m=150, separacion_m=500)
    assert sorted(round(p.x) for p in pts) == [-150, 150]
