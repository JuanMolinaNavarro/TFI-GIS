"""Mapa 2: ¿Funciona bien? Cobertura del suelo en la franja de ribera."""
from scripts import analisis, aoi, cifras, config, estilo

P = config.PALETA
ORDEN = ["vegetacion", "cultivo", "construido", "desnudo", "agua"]


def main():
    d = aoi.Datos()
    pct = analisis.porcentajes_cobertura(d.cob, d.franja_celdas)
    largo_km = round(d.rio.length.iloc[0] / 1000, 1)
    franja_ha = round(float(d.franja_celdas.sum()) * config.PIXEL_M ** 2 / 10000)
    cifras.guardar("ribera", {**pct, "franja_m": config.FRANJA_M, "largo_km": largo_km,
                              "franja_ha": franja_ha})

    fig, ax = estilo.nuevo_mapa(
        "¿Funciona bien?",
        f"Cobertura del suelo en la franja de {config.FRANJA_M} m a cada lado del Salí",
        caja=estilo.CAJA_IZQUIERDA)
    k = fig._escala
    ax.imshow(aoi.imagen_cobertura(d.cob), extent=d.ext, interpolation="nearest", zorder=1)
    ax.imshow(aoi.velo(~d.franja_celdas, 0.62), extent=d.ext, interpolation="nearest", zorder=2)
    d.franja.boundary.plot(ax=ax, color=P["tinta"], linewidth=1.0 * k, zorder=3)
    d.rio.plot(ax=ax, color="#123E55", linewidth=1.3 * k, zorder=4)
    aoi.encuadrar(ax, d)

    y = aoi.panel(fig, 0.86, f"{aoi.es(pct['vegetacion'], 0)} %", tam=54, fontweight="bold",
                  color=P["vegetacion"])
    y = aoi.panel(fig, y, "de la franja de ribera tiene cobertura vegetal.", tam=15,
                  ancho=30)
    aoi.panel(fig, y - 0.004,
              "El resto está cultivado, construido o sin cobertura: "
              f"{aoi.es(pct['construido'], 0)} % ya está edificado.", tam=12.5, alpha=0.85)

    fig.text(estilo.PANEL_X, 0.585, "Cobertura dentro de la franja", fontsize=12.5 * k,
             fontweight="bold")
    barras = fig.add_axes([estilo.PANEL_X + 0.115, 0.31, 0.245, 0.25])
    barras.set_facecolor(P["fondo"])
    posiciones = list(range(len(ORDEN)))[::-1]
    barras.barh(posiciones, [pct[g] for g in ORDEN],
                color=[aoi.COLOR_GRUPO[g] for g in ORDEN], height=0.62)
    for pos, g in zip(posiciones, ORDEN):
        barras.text(pct[g] + 1.2, pos, f"{aoi.es(pct[g])} %", va="center", fontsize=12 * k,
                    fontweight="bold")
    barras.set_yticks(posiciones, [aoi.ETIQUETA_GRUPO[g] for g in ORDEN], fontsize=12 * k)
    barras.set_xlim(0, max(pct.values()) * 1.45)
    barras.set_xticks([])
    barras.tick_params(length=0)
    for lado in barras.spines.values():
        lado.set_visible(False)

    aoi.panel(fig, 0.26,
              f"Franja analizada: {aoi.es(franja_ha, 0)} ha a lo largo de "
              f"{aoi.es(largo_km, 0)} km de río. Fuera de la franja la cobertura "
              "se muestra atenuada.", tam=11, alpha=0.8, ancho=44)

    print(estilo.terminar_mapa(
        fig, ax, "Fuentes: ESA WorldCover 2021 (10 m), OpenStreetMap. Elaboración propia.",
        config.MAPAS / "mapa2_ribera.png"))
    print(pct, "suma:", round(sum(pct.values()), 1))


if __name__ == "__main__":
    main()
