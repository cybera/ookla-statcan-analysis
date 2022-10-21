# from .loading import statcan, ookla
import geopandas as gp
import dotenv

from pathlib import Path

from datetime import datetime
from src.config import DATA_DIRECTORY, OVERLAYS_DIR

# DATA_DIRECTORY = Path(dotenv.dotenv_values()['DATA_DIRECTORY'])
# DA_OVERLAY_DIR = DATA_DIRECTORY / 'boundary_overlays'
# DA_OVELAY_DIR = OVERLAYS_DIR
# DA_OVERLAY_DIR.mkdir(exist_ok=True)


def overlay(left: gp.GeoDataFrame, right: gp.GeoDataFrame, crs=None):
    if crs:
        left = left.to_crs(crs)
    else:
        left = left.copy()
    right = right.to_crs(left.crs)
    left["left_area"] = left.area
    right["right_area"] = right.area

    ol = gp.overlay(left, right, how="union")
    ol["right_frac"] = ol.area / ol["right_area"]
    ol["left_frac"] = ol.area / ol["left_area"]

    return ol
