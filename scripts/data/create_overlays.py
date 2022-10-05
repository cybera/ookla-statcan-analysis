from src.datasets.loading import statcan, ookla
from src.datasets.overlays import overlay

from datetime import datetime

from src.config import DATA_DIRECTORY, OVERLAYS_DIR

DA_OVERLAY_DIR = OVERLAYS_DIR # DATA_DIRECTORY / 'boundary_overlays'
DA_OVERLAY_DIR.mkdir(exist_ok=True)

files = [
    ('population_centres', 'popctrs'),
    ('dissemination_areas', 'das'),
    ('census_subdivisions', 'subdivs'),
    ('census_divisions', 'divs')
]

def save_overlay(statcan_boundary, short_name):
    output_shapefile = DA_OVERLAY_DIR / f'tile_{short_name}_overlay'
    if output_shapefile.exists():
        print(f"File exists, skipping {output_shapefile}")
        return 
    print(f"Processing {statcan_boundary}")

    provinces = statcan.boundary('provinces_digital')
    tiles = ookla.canada_tiles().to_crs(provinces.crs)
    print(f"Calculating tile overlay with {statcan_boundary}")
    das = statcan.boundary(statcan_boundary)

    start = datetime.now()
    print(f'Started at {start}')
    da_tile_overlay = overlay(das, tiles)
    da_tile_overlay.rename(columns={'right_frac':'tile_frac','right_area':'tile_area','left_frac':f'{short_name}_frac','left_area':f'{short_name}_area'},inplace=True)
    da_tile_overlay.to_file(output_shapefile, driver="ESRI Shapefile")
    end = datetime.now()
    print(f"Ended at {end}")
    print(f"Elapsed duration {end-start}")

for name, short_name in files:
    save_overlay(name, short_name)
    print()
    print()