"""Recorta, reproyecta y alinea los datos crudos. Escribe datos/procesados/."""
import math
import unicodedata

import geopandas as gpd
import numpy as np
import rasterio
from rasterio import features
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject
from shapely.geometry import Point, box
from shapely.ops import linemerge, unary_union

from scripts import analisis, config


def _normalizar(texto):
    sin_tildes = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return sin_tildes.lower()


def unir_rio(gdf):
    """Une en una sola traza los tramos cuyo nombre contiene 'sali' (sin tildes)."""
    es_sali = gdf["name"].map(lambda n: "sali" in _normalizar(n))
    return linemerge(unary_union(list(gdf.geometry[es_sali])))


def cuenca_aguas_arriba(hybas, punto):
    """Subcuencas que drenan hacia la que contiene `punto` (incluida)."""
    inicio = hybas[hybas.contains(Point(punto))]["HYBAS_ID"]
    elegidas = set(inicio)
    while True:
        nuevas = set(hybas[hybas["NEXT_DOWN"].isin(elegidas)]["HYBAS_ID"]) - elegidas
        if not nuevas:
            break
        elegidas |= nuevas
    return hybas[hybas["HYBAS_ID"].isin(elegidas)]


def _solo_lineas(gdf):
    """Descarta los puntos sueltos que deja un recorte sobre un borde."""
    return gdf[gdf.geom_type.isin(["LineString", "MultiLineString"])]


def aoi_proyectada():
    return gpd.GeoSeries([box(*config.AOI_BBOX)], crs="EPSG:4326").to_crs(config.CRS_PROY).iloc[0]


def grilla(aoi):
    """Transformación y forma de la grilla común de PIXEL_M metros que cubre el AOI."""
    px = config.PIXEL_M
    o, s, e, n = aoi.bounds
    o, n = math.floor(o / px) * px, math.ceil(n / px) * px
    ancho, alto = math.ceil((e - o) / px), math.ceil((n - s) / px)
    return from_origin(o, n, px, px), (alto, ancho)


def _a_grilla(rutas, transf, forma, remuestreo, dtype, nodata):
    """Reproyecta una o más teselas a la grilla común."""
    destino = np.full(forma, nodata, dtype=dtype)
    for ruta in rutas:
        parcial = np.full(forma, nodata, dtype=dtype)
        with rasterio.open(ruta) as src:
            reproject(rasterio.band(src, 1), parcial, dst_transform=transf,
                      dst_crs=config.CRS_PROY, dst_nodata=nodata, resampling=remuestreo)
        falta = destino == nodata
        destino[falta] = parcial[falta]
    return destino


def guardar_raster(ruta, datos, transf, nodata):
    with rasterio.open(ruta, "w", driver="GTiff", height=datos.shape[0], width=datos.shape[1],
                       count=1, dtype=datos.dtype, crs=config.CRS_PROY, transform=transf,
                       nodata=nodata, compress="deflate") as dst:
        dst.write(datos, 1)


def leer_raster(nombre):
    with rasterio.open(config.PROCESADOS / nombre) as src:
        return src.read(1), src.transform


def rasterizar(geometria, transf, forma):
    return features.rasterize([(geometria, 1)], out_shape=forma, transform=transf,
                              all_touched=True, dtype="uint8").astype(bool)


def extension(transf, forma):
    """(izquierda, derecha, abajo, arriba) para imshow."""
    alto, ancho = forma
    return (transf.c, transf.c + ancho * transf.a, transf.f + alto * transf.e, transf.f)


def main():
    c, p = config.CRUDOS, config.PROCESADOS
    p.mkdir(parents=True, exist_ok=True)
    config.GPKG.unlink(missing_ok=True)
    crs = config.CRS_PROY

    aoi = aoi_proyectada()
    capas = {"aoi": gpd.GeoDataFrame(geometry=[aoi], crs=crs)}

    prov = gpd.read_file(c / "provincia.geojson")
    prov = prov[prov["nam"].map(lambda n: _normalizar(n).startswith("tucum"))].to_crs(crs)
    prov_geom = prov.geometry.iloc[0]
    capas["provincia"] = prov[["nam", "geometry"]]

    dep = gpd.read_file(c / "departamentos.geojson").to_crs(crs)
    dep = dep[dep.representative_point().within(prov_geom)]
    capas["departamentos"] = dep[["nam", "geometry"]]

    hidro = gpd.read_file(c / "hidro_ign.geojson").to_crs(crs)
    capas["hidro"] = _solo_lineas(gpd.clip(hidro[["nam", "geometry"]], prov_geom))

    hybas = gpd.read_file(c / "hybas_sa_lev07.gpkg")
    cuenca = cuenca_aguas_arriba(hybas, config.PUNTO_CIERRE_CUENCA).to_crs(crs)
    capas["cuenca"] = gpd.GeoDataFrame(geometry=[unary_union(list(cuenca.geometry))], crs=crs)

    rio_total = unir_rio(gpd.read_file(c / "osm_rio.geojson").to_crs(crs))
    capas["rio_total"] = gpd.GeoDataFrame(geometry=[rio_total], crs=crs)
    rio_prov = unir_rio(gpd.read_file(c / "osm_rio_prov.geojson").to_crs(crs))
    capas["rio_prov"] = gpd.GeoDataFrame(geometry=[rio_prov], crs=crs)
    corte = rio_total.intersection(aoi)
    rio = linemerge(corte) if corte.geom_type == "MultiLineString" else corte
    capas["rio"] = gpd.GeoDataFrame(geometry=[rio], crs=crs)
    franja = rio.buffer(config.FRANJA_M).intersection(aoi)
    capas["franja"] = gpd.GeoDataFrame(geometry=[franja], crs=crs)

    vias = gpd.read_file(c / "osm_vias.geojson").to_crs(crs)
    capas["vias"] = _solo_lineas(gpd.clip(vias[["highway", "geometry"]], aoi))

    for nombre, gdf in capas.items():
        gdf.to_file(config.GPKG, layer=nombre, driver="GPKG")

    transf, forma = grilla(aoi)
    cob = _a_grilla(sorted(c.glob("worldcover_S*.tif")), transf, forma,
                    Resampling.nearest, "uint8", 0)
    guardar_raster(p / "cobertura.tif", cob, transf, 0)
    dem = _a_grilla(sorted(c.glob("dem_*.tif")), transf, forma,
                    Resampling.bilinear, "float32", -9999)
    guardar_raster(p / "dem.tif", dem, transf, -9999)

    # Mancha urbana a escala provincial (100 m)
    o, s, e, n = prov_geom.bounds
    t_prov = from_origin(math.floor(o / 100) * 100, math.ceil(n / 100) * 100, 100, 100)
    f_prov = (math.ceil((n - s) / 100) + 1, math.ceil((e - o) / 100) + 1)
    wc_prov = _a_grilla([c / "worldcover_prov_100m.tif"], t_prov, f_prov,
                        Resampling.nearest, "uint8", 0)
    guardar_raster(p / "urbano_prov.tif", (wc_prov == 50).astype("uint8"), t_prov, 255)

    # Altura y distancia respecto del cauce
    rio_celdas = rasterizar(rio, transf, forma)
    dem_rio = dem.copy()
    if config.COTA_RIO_VENTANA_M:
        filas, columnas = np.nonzero(rio_celdas)
        xs, ys = rasterio.transform.xy(transf, filas, columnas)
        orden = np.array([rio.project(Point(x, y)) for x, y in zip(xs, ys)])
        ventana_px = max(1, round(config.COTA_RIO_VENTANA_M / config.PIXEL_M))
        dem_rio[rio_celdas] = analisis.cota_del_rio(dem, rio_celdas, orden, ventana_px)
    distancia, altura = analisis.distancia_y_altura(dem_rio, rio_celdas, config.PIXEL_M)
    guardar_raster(p / "distancia_cauce.tif", distancia.astype("float32"), transf, -9999)
    guardar_raster(p / "altura_cauce.tif",
                   np.where(np.isnan(altura), -9999, altura).astype("float32"), transf, -9999)

    if rio.geom_type != "LineString":
        raise RuntimeError(f"El río quedó como {rio.geom_type}: revisar la traza en el área")
    print("AOI (km):", round((aoi.bounds[2] - aoi.bounds[0]) / 1000, 1), "x",
          round((aoi.bounds[3] - aoi.bounds[1]) / 1000, 1))
    print("Río en AOI:", rio.geom_type, round(rio.length / 1000, 1), "km")
    print("Grilla:", forma, "| cobertura sin dato:", int((cob == 0).sum()),
          "| dem sin dato:", int((dem == -9999).sum()))


if __name__ == "__main__":
    main()
