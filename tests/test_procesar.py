import geopandas as gpd
from shapely.geometry import LineString, box

from scripts import procesar


def test_unir_rio_normaliza_nombre_y_une_tramos():
    gdf = gpd.GeoDataFrame(
        {"name": ["Río Salí", "Rio Sali", "Arroyo Otro"]},
        geometry=[LineString([(0, 0), (0, 1)]), LineString([(0, 1), (0, 2)]),
                  LineString([(5, 5), (6, 6)])], crs="EPSG:5345")
    linea = procesar.unir_rio(gdf)
    assert linea.geom_type == "LineString"
    assert linea.length == 2


def test_cuenca_aguas_arriba_recorre_next_down():
    hybas = gpd.GeoDataFrame(
        {"HYBAS_ID": [1, 2, 3, 4], "NEXT_DOWN": [2, 3, 0, 0]},
        geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1), box(2, 0, 3, 1), box(3, 0, 4, 1)],
        crs="EPSG:4326")
    resultado = procesar.cuenca_aguas_arriba(hybas, (2.5, 0.5))
    assert set(resultado["HYBAS_ID"]) == {1, 2, 3}
