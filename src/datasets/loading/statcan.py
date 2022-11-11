## load, list statistis canada related data
### including shapefiles
### including census data?

import os, re
import dotenv
import pandas as pd
import geopandas as gp
import json
import functools
import requests

import logging
import zipfile

from pathlib import Path

import warnings

from src.config import DATA_DIRECTORY

# DATA_DIRECTORY = Path(dotenv.dotenv_values()['DATA_DIRECTORY'])


### StatCan Boundary files
STATCAN_SUBDIR = DATA_DIRECTORY / "boundaries"

AUTO_DOWNLOAD = True


def statcan_links():
    with open(STATCAN_SUBDIR / "statcan_links.json") as f:
        links = json.load(f)["links"]
    return links


def boundary_names():
    return list(statcan_links().keys())


@functools.cache
def all_boundaries():
    gpfs = {name: boundary(name) for name in boundary_names()}
    return gpfs


@functools.cache
def boundary(name):
    links = statcan_links()
    statscan_shapefiles = {key: value.split("/")[-1] for key, value in links.items()}
    shapefile_path = STATCAN_SUBDIR / statscan_shapefiles[name]
    if AUTO_DOWNLOAD and not shapefile_path.exists():
        logging.info(f"Downloading file for {name}:{statscan_shapefiles[name]} data.")
        download_boundary(name)
    gpf = gp.read_file(shapefile_path)
    return gpf


def download_boundary(name):
    url = statcan_links()[name]
    r = requests.get(url)
    name = url.split("/")[-1]
    with open(STATCAN_SUBDIR / name, "wb") as file:
        file.write(r.content)


def download_boundaries():
    names = statcan_links().keys()
    for name in names:
        download_boundary(name)


def _donwload_unzip_check(url, dir, fname=None):
    dir.mkdir(exist_ok=True)
    r = requests.get(url)

    tempfile = dir / "downloaded_file.zip"

    with open(tempfile, "wb") as file:
        file.write(r.content)
    with open(tempfile, "rb") as file:
        zipfile.ZipFile(tempfile).extractall(dir)
    os.remove(tempfile)
    if fname is not None and not (dir / fname).exists():
        warnings.warn(f"Expected to find {fname} in zip archive, but it is missing.")


### Hexagon data
# MAP_DATA_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/Map_Data_Shapefile.zip/$file/Map_Data_Shapefile.zip" ## no longer hosted by Gov.
MAP_DATA_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/Map_Data_CSV.zip/$file/Map_Data_CSV.zip"
# MAP_DATA_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/Map_Data_MapInfo.zip/$file/Map_Data_MapInfo.zip"
HEX_URLS = [
    "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/CHX_EXO_geo.TAB/$file/CHX_EXO_geo.TAB",
    "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/CHX_EXO_geo.MAP/$file/CHX_EXO_geo.MAP",
    "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/CHX_EXO_geo.IND/$file/CHX_EXO_geo.IND",
    "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/CHX_EXO_geo.ID/$file/CHX_EXO_geo.ID",
    "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/CHX_EXO_geo.DAT/$file/CHX_EXO_geo.DAT",
]
HEXAGON_MAP_DIR = DATA_DIRECTORY / "CRTC_NBD_Map_Data"
HEXAGON_SHAPEFILE = HEXAGON_MAP_DIR / "CHX_EXO_geo.TAB"

HEXAGON_SPEED_INFO_FILE = DATA_DIRECTORY / "CRTC_NBD_Map_Data" / "Data_Hex_Données.csv"

# PHH_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/PHH_Data_ShapeFile.zip/$file/PHH_Data_ShapeFile.zip"
PHH_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/PHH_Data_MapInfo.zip/$file/PHH_Data_MapInfo.zip"
PHH_DIR = DATA_DIRECTORY / "PHH"


PHH_URL_SINGLECSV = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/PHH_Data_CSV.zip/$file/PHH_Data_CSV.zip"
PHH_SPEEDS_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/NBD_PHH_Speeds.zip/$file/NBD_PHH_Speeds.zip"


def download_map_data():
    _donwload_unzip_check(MAP_DATA_URL, HEXAGON_MAP_DIR)


def download_hexagons():
    for url in HEX_URLS:
        HEXAGON_MAP_DIR.mkdir(exist_ok=True)
        r = requests.get(url)

        fname = ""
        if "Content-Disposition" in r.headers.keys():
            fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
        else:
            fname = url.split("/")[-1]

        tabfile = HEXAGON_MAP_DIR / fname

        with open(tabfile, "wb") as file:
            file.write(r.content)


def download_phh():
    _donwload_unzip_check(PHH_URL, PHH_DIR)
    _donwload_unzip_check(PHH_URL_SINGLECSV, PHH_DIR)
    _donwload_unzip_check(PHH_SPEEDS_URL, PHH_DIR / "CRTC_Speed_Data")


@functools.cache
def _hexagons():
    if not HEXAGON_SHAPEFILE.exists() and AUTO_DOWNLOAD:
        download_hexagons()
    gdf = gp.read_file(HEXAGON_SHAPEFILE)
    return gdf


def hexagon_geometry():
    return _hexagons().copy()


def hexagon_data():
    return pd.read_csv(HEXAGON_SPEED_INFO_FILE)


@functools.cache
def _phh_MapInfo():
    shapefiles = list(PHH_DIR.glob("./PHH_DATA_MapInfo/*.TAB"))
    if len(shapefiles) == 0 and AUTO_DOWNLOAD:
        download_phh()
        shapefiles = list(PHH_DIR.glob("./PHH_DATA_MapInfo/*.TAB"))

    gdf = pd.concat([gp.read_file(f) for f in shapefiles], axis=0).reset_index(
        drop=True
    )
    return gdf


def phh_geometry():
    return _phh_MapInfo().copy()[["PHH_ID", "geometry"]]


def phh_data():
    df = pd.DataFrame(_phh_MapInfo().copy())
    del df["geometry"]
    return df


@functools.cache
def phh_csv_data():
    csv_files = list(PHH_DIR.glob("./PHH_DATA_CSV/*.csv"))
    if len(csv_files) == 0 and AUTO_DOWNLOAD:
        download_phh()
        csv_files = list(PHH_DIR.glob("./PHH_DATA_CSV/*.csv"))
    return pd.concat([pd.read_csv(f) for f in csv_files], axis=0).reset_index(drop=True)


@functools.cache
def phh_hex_data():
    grps = _phh_MapInfo().groupby("HEXUID_IdUHEX")
    agg = pd.concat(
        [
            grps["Pop2016"].sum(),
            grps["TDwell2016_TLog2016"].sum(),
            grps["URDwell2016_RH2016"].sum(),
            grps["PHH_ID"].count().rename("PHH_Count"),
            grps["Type"]
            .apply(lambda df: df.value_counts().iloc[0])
            .rename("Common_Type"),
        ],
        axis=1,
    )
    return agg


@functools.cache
def hexagons_phh():
    # return hexagons().merge(phh_hex_pop(), left_on="HEXuid_HEX", right_index=True)
    return hexagon_data().merge(
        phh_hex_data(), left_on="HEXuid_HEXidu", right_index=True
    )


### Demographic data
POP_DIR = DATA_DIRECTORY / "census_data"
POP_FILE = POP_DIR / "98-400-X2016003_English_CSV_data.csv"
FILE_URL = "https://www12.statcan.gc.ca/census-recensement/2016/dp-pd/dt-td/CompDataDownload.cfm?LANG=E&PID=109525&OFT=CSV"


def download_pop_data():
    POP_DIR.mkdir(exist_ok=True)
    r = requests.get(FILE_URL)
    with open(POP_DIR / "zip_download.zip", "wb") as file:
        file.write(r.content)
    with open(POP_DIR / "zip_download.zip", "rb") as file:
        zipfile.ZipFile(file).extractall(POP_DIR)
    os.remove(POP_DIR / "zip_download.zip")


@functools.cache
def populations():
    if not POP_FILE.exists() and AUTO_DOWNLOAD:
        download_pop_data()
    return pd.read_csv(POP_FILE)


def _total_pops(id_name, level):
    total_pops = populations().loc[
        lambda s: s["DIM: Age (in single years) and average age (127)"] == "Total - Age"
    ]
    total_pops = total_pops[
        [
            "GEO_CODE (POR)",
            "GEO_LEVEL",
            "GEO_NAME",
            "Dim: Sex (3): Member ID: [1]: Total - Sex",
        ]
    ]
    total_pops = total_pops.rename(
        columns={
            "GEO_CODE (POR)": "ID",
            "Dim: Sex (3): Member ID: [1]: Total - Sex": "DAPOP",
        }
    )

    total_pops = total_pops.loc[lambda s: s.GEO_LEVEL == level]
    del total_pops["GEO_LEVEL"]
    total_pops = total_pops.rename(columns={"ID": id_name})
    return total_pops.copy()


def dissemination_areas_populations():
    return _total_pops("DAUID", 4)


def census_subdivisions_populations():
    return _total_pops("CSDUID", 3)


def census_divisions_populations():
    return _total_pops("CDUID", 2)


if __name__ == "__main__":

    print("Downloading all statcan census boundary files")
    download_boundaries()

    print("Downloading census population data")
    download_pop_data()

    print("Downloading map data (CSV)")
    download_map_data()

    print("Downloading hexagon files (MapFile)")
    download_hexagons()

    print("Downloading PHH data")
    download_phh()
