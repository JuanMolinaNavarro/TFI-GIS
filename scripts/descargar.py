"""Descarga los datos crudos a datos/crudos/. Se puede volver a correr: no repite lo ya bajado."""
import datetime
import json
import time
import zipfile
from pathlib import Path

import geopandas as gpd
import rasterio
import requests
from rasterio.enums import Resampling
from rasterio.merge import merge
from rasterio.windows import from_bounds

from scripts import config

CABECERAS = {"User-Agent": "tfi-gis-academico"}
IGN_WFS = "https://wms.ign.gob.ar/geoserver/ign/ows"
OVERPASS = "https://overpass-api.de/api/interpreter"
URL_WC = ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
          "ESA_WorldCover_10m_2021_v200_{t}_Map.tif")
URL_DEM = ("https://copernicus-dem-30m.s3.amazonaws.com/"
           "Copernicus_DSM_COG_10_{t}_DEM/Copernicus_DSM_COG_10_{t}_DEM.tif")
URL_HYBAS = "https://data.hydrosheds.org/file/hydrobasins/standard/hybas_sa_lev07_v1c.zip"

_fuentes = []


def bajar(url, destino, minimo_bytes=1024, **kwargs):
    """Descarga `url` a `destino` de forma atómica. Si falla no deja ningún archivo."""
    destino = Path(destino)
    if destino.exists():
        return destino
    parcial = destino.with_suffix(destino.suffix + ".part")
    try:
        resp = requests.get(url, headers=CABECERAS, stream=True, timeout=180, **kwargs)
        try:
            if resp.status_code != 200:
                raise RuntimeError(f"Descarga fallida ({resp.status_code}): {url}")
            total = 0
            with open(parcial, "wb") as f:
                for bloque in resp.iter_content(chunk_size=1 << 20):
                    f.write(bloque)
                    total += len(bloque)
        finally:
            resp.close()
        if total < minimo_bytes:
            raise RuntimeError(f"Descarga incompleta ({total} bytes): {url}")
    except Exception:
        parcial.unlink(missing_ok=True)
        raise
    parcial.replace(destino)
    return destino


def _reintentar(funcion, intentos=3, espera=15):
    for i in range(intentos):
        try:
            return funcion()
        except Exception as e:  # noqa: BLE001
            if i == intentos - 1:
                raise
            print(f"  reintento {i + 1}: {e}")
            time.sleep(espera)


def _anotar(nombre, url):
    _fuentes.append((nombre, url))


def _ampliar(bbox, margen):
    o, s, e, n = bbox
    return (o - margen, s - margen, e + margen, n + margen)


def ign(capa, destino, bbox):
    o, s, e, n = bbox
    params = {"service": "WFS", "version": "1.0.0", "request": "GetFeature",
              "typeName": f"ign:{capa}", "outputFormat": "application/json",
              "srsName": "EPSG:4326", "bbox": f"{o},{s},{e},{n}"}
    _reintentar(lambda: bajar(IGN_WFS, destino, params=params))
    _anotar(destino.name, f"{IGN_WFS} (WFS, capa ign:{capa})")


def overpass(consulta, destino):
    """Guarda como GeoJSON las vías (ways) que devuelve una consulta Overpass."""
    if destino.exists():
        return
    crudo = destino.with_suffix(".overpass.json")

    def pedir():
        resp = requests.post(OVERPASS, data={"data": consulta}, headers=CABECERAS, timeout=300)
        if resp.status_code != 200:
            raise RuntimeError(f"Overpass respondió {resp.status_code}")
        return resp.json()

    datos = _reintentar(pedir)
    crudo.write_text(json.dumps(datos), encoding="utf-8")
    entidades = []
    for el in datos["elements"]:
        if el["type"] != "way" or "geometry" not in el:
            continue
        coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
        if len(coords) < 2:
            continue
        props = {"osm_id": el["id"], **{k: v for k, v in el.get("tags", {}).items()
                                        if k in ("name", "waterway", "highway")}}
        entidades.append({"type": "Feature", "properties": props,
                          "geometry": {"type": "LineString", "coordinates": coords}})
    if not entidades:
        raise RuntimeError(f"Overpass no devolvió geometrías para {destino.name}")
    destino.write_text(json.dumps({"type": "FeatureCollection", "features": entidades}),
                       encoding="utf-8")
    crudo.unlink()
    _anotar(destino.name, f"{OVERPASS} (OpenStreetMap)")


def recorte_remoto(url, destino, bbox, factor=1, remuestreo=Resampling.nearest):
    """Lee por ventana un GeoTIFF remoto (COG) y guarda solo el recuadro pedido."""
    if destino.exists():
        return destino

    def leer():
        with rasterio.open(url) as src:
            b = src.bounds
            o, s, e, n = (max(bbox[0], b.left), max(bbox[1], b.bottom),
                          min(bbox[2], b.right), min(bbox[3], b.top))
            if o >= e or s >= n:
                return None
            ventana = from_bounds(o, s, e, n, src.transform).round_offsets().round_lengths()
            alto = max(1, int(ventana.height / factor))
            ancho = max(1, int(ventana.width / factor))
            datos = src.read(1, window=ventana, out_shape=(alto, ancho), resampling=remuestreo)
            transf = rasterio.transform.from_bounds(
                *rasterio.windows.bounds(ventana, src.transform), ancho, alto)
            perfil = {"driver": "GTiff", "height": alto, "width": ancho, "count": 1,
                      "dtype": datos.dtype, "crs": src.crs, "transform": transf,
                      "nodata": src.nodata, "compress": "deflate"}
        parcial = destino.with_suffix(".part.tif")
        with rasterio.open(parcial, "w", **perfil) as dst:
            dst.write(datos, 1)
        parcial.replace(destino)
        return destino

    resultado = _reintentar(leer)
    if resultado is not None:
        _anotar(destino.name, url)
    return resultado


def main():
    config.CRUDOS.mkdir(parents=True, exist_ok=True)
    c = config.CRUDOS
    aoi = _ampliar(config.AOI_BBOX, 0.1)

    print("IGN...")
    ign("provincia", c / "provincia.geojson", config.PROV_BBOX)
    ign("departamento", c / "departamentos.geojson", config.PROV_BBOX)
    ign("lineas_de_aguas_continentales_perenne", c / "hidro_ign.geojson", config.PROV_BBOX)

    print("OpenStreetMap...")
    o, s, e, n = aoi
    overpass(f'[out:json][timeout:180];way["waterway"="river"]["name"~"Sal",i]'
             f'({s},{o},{n},{e});out geom;', c / "osm_rio.geojson")
    o, s, e, n = config.PROV_BBOX
    overpass(f'[out:json][timeout:180];way["waterway"="river"]["name"~"Sal[ií]$",i]'
             f'({s},{o},{n},{e});out geom;', c / "osm_rio_prov.geojson")
    o, s, e, n = config.AOI_BBOX
    overpass(f'[out:json][timeout:180];way["highway"~"^(primary|secondary|tertiary|residential)$"]'
             f'({s},{o},{n},{e});out geom;', c / "osm_vias.geojson")

    print("ESA WorldCover (área de estudio)...")
    for t in config.teselas_worldcover(aoi):
        recorte_remoto(URL_WC.format(t=t), c / f"worldcover_{t}.tif", aoi)

    print("ESA WorldCover (provincia, 100 m)...")
    prov = c / "worldcover_prov_100m.tif"
    if not prov.exists():
        partes = []
        for t in config.teselas_worldcover(config.PROV_BBOX):
            p = recorte_remoto(URL_WC.format(t=t), c / f"_wc_prov_{t}.tif",
                               config.PROV_BBOX, factor=12)
            if p:
                partes.append(p)
        abiertos = [rasterio.open(p) for p in partes]
        mosaico, transf = merge(abiertos)
        perfil = abiertos[0].profile | {"height": mosaico.shape[1], "width": mosaico.shape[2],
                                        "transform": transf}
        for a in abiertos:
            a.close()
        with rasterio.open(prov, "w", **perfil) as dst:
            dst.write(mosaico)
        for p in partes:
            p.unlink()
        _anotar(prov.name, URL_WC.format(t="<tesela>") + " (remuestreado)")

    print("Copernicus DEM...")
    for t in config.teselas_dem(aoi):
        recorte_remoto(URL_DEM.format(t=t), c / f"dem_{t}.tif", aoi)

    print("HydroBASINS...")
    hy = c / "hybas_sa_lev07.gpkg"
    if not hy.exists():
        zip_ = _reintentar(lambda: bajar(URL_HYBAS, c / "hybas_sa_lev07_v1c.zip", 1 << 20))
        with zipfile.ZipFile(zip_) as z:
            shp = next(nm for nm in z.namelist() if nm.endswith(".shp"))
        gdf = gpd.read_file(f"zip://{zip_}!{shp}", bbox=_ampliar(config.PROV_BBOX, 1.5))
        gdf.to_file(hy, driver="GPKG")
        _anotar(hy.name, URL_HYBAS)

    if _fuentes:
        hoy = datetime.date.today().isoformat()
        with open(c / "FUENTES.md", "a", encoding="utf-8") as f:
            for nombre, url in _fuentes:
                f.write(f"- `{nombre}`: {url} (descargado el {hoy})\n")
    restos = list(c.glob("*.part*"))
    if restos:
        raise RuntimeError(f"Quedaron descargas incompletas: {restos}")
    print("Listo:", sorted(p.name for p in c.iterdir()))


if __name__ == "__main__":
    main()
