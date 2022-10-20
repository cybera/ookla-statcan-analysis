"""
Loads files from the DATA_DIRECTORY/ookla-raw folder 
and creates filtered files which contain only those speed tiles contained 
within Canada's borders. 

Includes a caching mechanism for identifying tiles that are inside 
Canada's bounding box, but which aren't in Canada.
The shapefile loading can be filtered to a bounding box
but some areas, 
e.g. areas in the northern United states are included 
in the load because they are higher north than 
Windsor and 
must subsequently be tested for if they are inside 
Canada's (complex) geometry. Saving these 
tile's labels as being in/out of Canada
speeds up subsequen data files when they are loaded.

On my M1 MacBook Air each file can take 20-30 minutes to filter, 
but this is sped up to a few minutes once enough of the Canadian/US
tiles are cached. This cache is stored and reloaded as a file, or created
if one doesn't exist. 

"""

import dotenv
import pandas as pd
import geopandas as gp
from pathlib import Path

from collections import namedtuple
import glob
import re
import datetime

import src.datasets.loading.statcan as statcan
from src.config import DATA_DIRECTORY
import warnings

# warnings.filterwarnings("ignore", "SettingWithCopyWarning*")
pd.options.mode.chained_assignment = None

OoklaPerformanceData = namedtuple(
    "OoklaPerformanceData", ["path", "type", "year", "quarter"]
)

# DATA_DIRECTORY = Path(dotenv.dotenv_values()['DATA_DIRECTORY'])

RAW_TILES_DIR = DATA_DIRECTORY / "ookla-raw"
CANADA_TILES_DIR = DATA_DIRECTORY / "ookla-canada-tiles"

CANADA_TILES_DIR.mkdir(exist_ok=True, parents=True)

pat = re.compile(
    ".*/type=(?P<type>fixed|mobile)/year=(?P<year>[0-9]{4})/quarter=(?P<quarter>[1-4])/.*"
)


def as_namedtuple(path):
    m = pat.match(str(path))
    return OoklaPerformanceData(path, **m.groupdict())


raw_files = list(RAW_TILES_DIR.glob("**/*.zip"))
raw_files = [as_namedtuple(p) for p in raw_files]
raw_files = sorted(raw_files)

if len(raw_files) == 0:
    raise ValueError(f"Couldn't locate Ookla shapefiles at {RAW_TILES_DIR}")

provinces_digital = statcan.boundary("provinces_digital").to_crs(epsg=4326)

## Allows for new quarters to be calculated faster
tile_labels = None
if (CANADA_TILES_DIR / "all-tile-labels.csv").exists():
    print("Loading cached tile labels")
    tile_labels = gp.read_file(CANADA_TILES_DIR / "all-tile-labels")
    tile_labels["in_canada"] = tile_labels["in_canada"].astype("bool")

results = []
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

    if tile_labels is None:
        tile_labels = a_tile[["quadkey", "geometry"]].iloc[0:0]
        tile_labels["in_canada"] = False

    known_tiles = a_tile.loc[lambda s: s.quadkey.isin(tile_labels.quadkey)]
    unknown_tiles = a_tile.loc[lambda s: ~s.quadkey.isin(tile_labels.quadkey)]

    inner_intersection = gp.sjoin(unknown_tiles, provinces_digital, how="inner")
    unknown_tiles["in_canada"] = False
    unknown_tiles.loc[
        lambda s: s.quadkey.isin(inner_intersection.quadkey), "in_canada"
    ] = True
    tile_labels = pd.concat(
        [tile_labels, unknown_tiles[["quadkey", "geometry", "in_canada"]]], axis=0
    )
    tile_labels.drop_duplicates(subset=["quadkey"], inplace=True)

    only_canada = a_tile.loc[
        lambda s: s.quadkey.isin(tile_labels.loc[lambda s: s.in_canada].quadkey)
    ]
    only_canada = only_canada.drop_duplicates(subset=["quadkey"])
    only_canada = only_canada.iloc[:, 0 : a_tile.shape[1]]

    tile_geometries: gp.GeoDataFrame = only_canada.loc[:, ["quadkey", "geometry"]]
    tile_data = pd.DataFrame(only_canada)
    tile_data["conn_type"] = raw_file.type
    tile_data["year"] = int(raw_file.year)
    tile_data["quarter"] = int(raw_file.quarter)
    del tile_data["geometry"]

    results.append((tile_geometries, tile_data))

    print(f"Saving {speed_file}")
    tile_data.to_csv(speed_file, index=False)
    print(f"Saving {geotile_file}")
    tile_geometries.to_file(geotile_file, driver="ESRI Shapefile")
    end = datetime.datetime.now()
    print(f"Time Elapsed {end-start}")

if len(results) == 0:
    print("No new tile files found, exiting without updating all-tile-labels.")
    quit()

print("Saving tile labels...")
tile_labels.to_csv(CANADA_TILES_DIR / "all-tile-labels.csv", index=False)
tile_labels.to_file(CANADA_TILES_DIR / "all-tile-labels", driver="ESRI Shapefile")
