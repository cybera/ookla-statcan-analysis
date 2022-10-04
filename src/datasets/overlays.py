from .loading import statcan, ookla
import geopandas as gp
import dotenv 

from pathlib import Path

from datetime import datetime

DATA_DIRECTORY = Path(dotenv.dotenv_values()['DATA_DIRECTORY'])
DA_OVERLAY_DIR = DATA_DIRECTORY / 'boundary_overlays'
DA_OVERLAY_DIR.mkdir(exist_ok=True)


def overlay(left:gp.GeoDataFrame, right:gp.GeoDataFrame, crs=None):
    if crs:
        left = left.to_crs(crs)
    right = right.to_crs(left.crs)
    left['left_area'] = left.area
    right['right_area'] = right.area
    
    ol = gp.overlay(left, right, how='union')
    ol['right_frac'] = ol.area/ol['right_area']
    ol['left_frac'] = ol.area/ol['left_area']

    return ol


def save_overlay(statcan_boundary, short_name):
    output_shapefile = DA_OVERLAY_DIR / f'tile_{short_name}_overlay'
    
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








