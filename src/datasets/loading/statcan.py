## load, list statistis canada related data
### including shapefiles
### including census data?

import os
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
MAP_DATA_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/Map_Data_Shapefile.zip/$file/Map_Data_Shapefile.zip"
HEXAGON_SHAPEFILE_DIR = DATA_DIRECTORY / "Map_Data_Shapefile"
HEXAGON_SHAPEFILE = HEXAGON_SHAPEFILE_DIR / "Data_Hex_Donnees.SHP"

PHH_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/PHH_Data_ShapeFile.zip/$file/PHH_Data_ShapeFile.zip"
PHH_DIR = DATA_DIRECTORY / "PHH"


PHH_URL_SINGLECSV = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/PHH_Data_CSV.zip/$file/PHH_Data_CSV.zip"
PHH_SPEEDS_URL = "https://www.ic.gc.ca/eic/site/720.nsf/vwapj/NBD_PHH_Speeds.zip/$file/NBD_PHH_Speeds.zip"


def download_hexagons():
    _donwload_unzip_check(MAP_DATA_URL, HEXAGON_SHAPEFILE_DIR, HEXAGON_SHAPEFILE.name)


def download_phh():
    _donwload_unzip_check(PHH_URL, PHH_DIR)
    _donwload_unzip_check(PHH_URL_SINGLECSV, PHH_DIR)
    _donwload_unzip_check(PHH_SPEEDS_URL, PHH_DIR)


@functools.cache
def hexagons():
    if not HEXAGON_SHAPEFILE.exists() and AUTO_DOWNLOAD:
        download_hexagons()
    gdf = gp.read_file(HEXAGON_SHAPEFILE)
    del gdf["LAYER"]
    del gdf["BORDER_STY"]
    del gdf["BORDER_COL"]
    del gdf["FILL_STYLE"]
    del gdf["CLOSED"]
    del gdf["BORDER_WID"]
    chopped_cols = {
        "SumPop_201": "SumPop_2016_SommePop",
        "SumURD_201": "SumURD_2016_SommeRH",
        "SumTD_2016": "SumTD_2016_SommeTL",
        "Avail_5_1_": "Avail_5_1_75PctPlus_Dispo",
        "Avail_50_1": "Avail_50_10_Gradient_Dispo",
    }
    return gdf.rename(columns=chopped_cols)


@functools.cache
def phh():
    csv_files = list(PHH_DIR.glob("./PHH_DATA_CSV/*.csv"))
    if len(csv_files) == 0 and AUTO_DOWNLOAD:
        download_phh()
        csv_files = list(PHH_DIR.glob("./PHH_DATA_CSV/*.csv"))
    return pd.concat([pd.read_csv(f) for f in csv_files], axis=0).reset_index(drop=True)


@functools.cache
def phh_shapefiles():
    shapefiles = list(PHH_DIR.glob("./PHH_DATA_Shapefile/*.shp"))
    if len(shapefiles) == 0 and AUTO_DOWNLOAD:
        download_phh()
        shapefiles = list(PHH_DIR.glob("./PHH_DATA_Shapefile/*.shp"))

    gdf = pd.concat([gp.read_file(f) for f in shapefiles], axis=0).reset_index(
        drop=True
    )
    del gdf["LAYER"]
    del gdf["GM_TYPE"]
    chopped_cols = {
        "TDwell2016": "TDwell2016_TLog2016",
        "URDwell206": "URDwell2016_RH2016",
        "DBUID_Idid": "DBUID_Ididu",
        "HEXUID_IdU": "HEXUID_IdUHEX",
        "Pruid_Prid": "Pruid_Pridu",
    }
    return gdf.rename(columns=chopped_cols)


@functools.cache
def phh_hex_pop():
    grps = phh().groupby("HEXUID_IdUHEX")
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
    return hexagons().merge(phh_hex_pop(), left_on="HEXuid_HEX", right_index=True)


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
    # print("Downloading all statcan related files")
    # download_boundaries()
    # download_pop_data()

    print("Downloading hexagon files")
    download_hexagons()

    print("Downloading PHH data")
    download_phh()
