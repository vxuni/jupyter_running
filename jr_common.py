import activityio as aio
import branca
import folium
import numpy as np
import pandas as pd
from pathlib import Path

FIT_FILE = Path.home() / 'Desktop/2018-08-30-080506-cpbotha-watch.fit'

def load_fit_file() -> pd.DataFrame:
    """Convenience function to load fit file from disk and return in dataframe."""
    return aio.read(FIT_FILE)

def make_folium_map_with_run(runt: pd.DataFrame) -> folium.Map:
    """Given a dataframe with .fit data, show run route on a map."""

    # OpenStreetMap really nice, but CartoDB Positron lighter and better for overlaid route
    map = folium.Map(location=[np.mean(runt.lat), np.mean(runt.lon)], tiles="cartodbpositron")

    folium.Marker(
        location=[runt.lat[0], runt.lon[0]],
        popup='Start',
        icon=folium.Icon(color='green')
    ).add_to(map)

    # Blues_09
    cm: branca.colormap.LinearColormap = branca.colormap.linear.Oranges_05
    cm = cm.scale(np.min(runt.cad), np.max(runt.cad))
    print(cm.vmin, cm.vmax)

    poly_line = folium.ColorLine(
        list(zip(runt.lat.values, runt.lon.values)),
        colors=runt.cad.values, colormap=cm).add_to(map)

    # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.idxmax.html
    # True is > False, so idxmax() will return idx of first occurrence of True
    for km in range(1, int(runt.dist.max() / 1000) + 1):
        idx = (runt.dist > km * 1000).idxmax()

        idx_1km_back = (runt.dist > (runt.dist[idx] - 1000)).idxmax()

        time_per_km = runt.time[idx] - runt.time[idx_1km_back]

        info_msg = (
            f"Stats<br>"
            f"distance <b>{runt.dist[idx]}</b>"
        )

        if time_per_km is not None:
            info_msg += f"<br>1km split: <b>{time_per_km:.2f}/km</b>"

        folium.Marker((runt.lat[idx], runt.lon[idx]), popup=info_msg).add_to(map)
        prev_km_idx = idx

    map.fit_bounds(poly_line.get_bounds())

    return map

