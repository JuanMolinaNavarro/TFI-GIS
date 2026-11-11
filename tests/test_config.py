from scripts import config


def test_teselas_worldcover_aoi():
    assert config.teselas_worldcover(config.AOI_BBOX) == ["S27W066"]


def test_teselas_worldcover_cruza_paralelo_27():
    assert config.teselas_worldcover((-65.5, -27.5, -65.0, -26.5)) == ["S27W066", "S30W066"]


def test_teselas_dem_aoi():
    assert config.teselas_dem(config.AOI_BBOX) == ["S27_00_W066_00"]


def test_teselas_dem_cruza_meridiano_65():
    assert config.teselas_dem((-65.1, -26.9, -64.9, -26.8)) == ["S27_00_W065_00", "S27_00_W066_00"]


def test_paleta_completa():
    assert set(config.PALETA) == {"fondo", "tinta", "agua", "vegetacion", "humedal",
                                  "construido", "desnudo", "cultivo", "acento"}
