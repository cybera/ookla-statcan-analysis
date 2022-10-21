import sys

import pandas as pd

from src.datasets.loading import statcan, ookla
from src.datasets.overlays import overlay

from datetime import datetime

import warnings

from src.config import DATA_DIRECTORY, OVERLAYS_DIR

DA_OVERLAY_DIR = OVERLAYS_DIR  # DATA_DIRECTORY / 'boundary_overlays'
DA_OVERLAY_DIR.mkdir(exist_ok=True)

default_files = [
    ("population_centres", "pops"),
    ("dissemination_areas", "das"),
    ("census_subdivisions", "subs"),
    ("census_divisions", "divs"),
]


def save_overlay(statcan_boundary, short_name):
    output_shapefile = DA_OVERLAY_DIR / f"tile_{short_name}_overlay"
    if output_shapefile.exists():
        print(f"File exists, skipping {output_shapefile}")
        return
    print(f"Processing {statcan_boundary}")

    provinces = statcan.boundary("provinces_digital")
    tiles = ookla.canada_tiles().to_crs(provinces.crs)
    print(f"Calculating tile overlay with {statcan_boundary}")
    das = statcan.boundary(statcan_boundary)

    start = datetime.now()
    print(f"Started at {start}")
    tile_overlay = overlay(das, tiles)
    print("done overlays, cleaning up")
    ## reduce precision to prevent saving error/warning savingto shapefile
    # tile_overlay["left_area"] = tile_overlay["left_area"].astype("float32")
    # tile_overlay["right_area"] = tile_overlay["left_area"].astype("float32")
    tile_overlay["left_area"] /= 1e6
    tile_overlay["right_area"] /= 1e6
    tile_overlay.rename(
        columns={
            "right_frac": "tile_frac",
            "right_area": "tile_area",
            "left_frac": f"{short_name}_frac",
            "left_area": f"{short_name}_area",
        },
        inplace=True,
    )
    # da_tile_overlay["quadkey"] = da_tile_overlay.astype(str)
    # quadkey field needs to be str to avoid errors related to field width on save to Shapefile
    tile_overlay["quadkey"] = (
        tile_overlay["quadkey"]
        .astype("Int64")
        .astype(str)
        .apply(lambda s: s if s != "<NA>" else None)
    )

    with warnings.catch_warnings():
        warnings.filterwarnings("once")
        tile_overlay.to_file(output_shapefile, driver="ESRI Shapefile")
    end = datetime.now()
    print(f"Ended at {end}")
    print(f"Elapsed duration {end-start}")


# shapefile schema, may be useful to specify if errors persist.
# {'properties': OrderedDict([('PCUID', 'str:80'), ('PCNAME', 'str:80'), ('PCTYPE', 'str:80'), ('PCPUID', 'str:80'), ('PCCLASS', 'str:80'), ('PRUID', 'str:80'), ('PRNAME', 'str:80'), ('CMAUID', 'str:80'), ('CMANAME', 'str:80'), ('CMATYPE', 'str:80'), ('CMAPUID', 'str:80'), ('popctrs_ar', 'float:24.15'), ('quadkey', 'str:80'), ('tile_area', 'float:24.15'), ('tile_frac', 'float:24.15'), ('popctrs_fr', 'float:24.15')]), 'geometry': 'Polygon'}

if __name__ == "__main__":
    import warnings

    if len(sys.argv) == 1:
        files = default_files
        print("No name, shortname pairs provided as args, using defaults.")
    else:
        files = list(zip(sys.argv[1::2], sys.argv[2::2]))

    print("Creating overlays using the following boundary names and short names:")
    import pprint

    pprint.pprint(files)

    for name, short_name in files:
        save_overlay(name, short_name)
        print()
