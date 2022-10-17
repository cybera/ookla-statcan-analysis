###
import dotenv
import pandas as pd
import geopandas as gp
from pathlib import Path

from collections import namedtuple
import glob
import re
import datetime

import src.datasets.loading.statcan as statcan

OoklaPerformanceData = namedtuple(
    "OoklaPerformanceData", ["path", "type", "year", "quarter"]
)

DATA_DIRECTORY = Path(dotenv.dotenv_values()["DATA_DIRECTORY"])
RAW_TILES_DIR = DATA_DIRECTORY / "ookla-raw"
CANADA_TILES_DIR = DATA_DIRECTORY / "ookla-canada-tiles"

CANADA_TILES_DIR.mkdir(exist_ok=True)

pat = re.compile(
    ".*/type=(?P<type>fixed|mobile)/year=(?P<year>[0-9]{4})/quarter=(?P<quarter>[1-4])/.*"
)


def as_namedtuple(path):
    m = pat.match(str(path))
    return OoklaPerformanceData(path, **m.groupdict())


raw_files = list(RAW_TILES_DIR.glob("**/*.zip"))
raw_files = [as_namedtuple(p) for p in raw_files]

provinces_digital = statcan.boundary("provinces_digital").to_crs(epsg=4326)

# raw_file = raw_files[0]
for raw_file in raw_files:
    filtered_filename = (
        f"ookla-canada-{raw_file.year}-Q{raw_file.quarter}-{raw_file.type}"
    )
    speed_file = CANADA_TILES_DIR / (filtered_filename + "-tiles.csv")
    geotile_file = CANADA_TILES_DIR / (filtered_filename + "-tiles")

    if speed_file.exists():
        print(f"Skiping {raw_file} because {speed_file} exists.")
        continue

    print(f"Processing {raw_file}")

    start = datetime.datetime.now()
    a_tile = gp.read_file(str(raw_file.path), bbox=provinces_digital)
    only_canada: gp.GeoDataFrame = gp.sjoin(a_tile, provinces_digital)
    only_canada = only_canada.drop_duplicates(subset=["quadkey"])
    only_canada = only_canada.iloc[:, 0 : a_tile.shape[1]]

    tile_geometries: gp.GeoDataFrame = only_canada.loc[:, ["quadkey", "geometry"]]
    tile_data = pd.DataFrame(only_canada)
    tile_data["conn_type"] = raw_file.type
    tile_data["year"] = int(raw_file.year)
    tile_data["quarter"] = int(raw_file.quarter)
    del tile_data["geometry"]

    print(f"Saving {speed_file}")
    tile_data.to_csv(speed_file, index=False)
    print(f"Saving {geotile_file}")
    tile_geometries.to_file(geotile_file, driver="ESRI Shapefile")
    end = datetime.datetime.now()
    print(f"Time Elapsed {end-start}")
