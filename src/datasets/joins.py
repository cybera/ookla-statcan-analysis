import geopandas as gp
import pandas as pd
import numpy as np

from src.datasets.loading import statcan
from src.datasets import overlays

import statsmodels as sm
import statsmodels.stats.weightstats
from scipy.stats import lognorm
import scipy.stats

import functools
import warnings


@functools.cache
def hexagons_popctrs_overlay():
    hexagons = statcan.hexagon_geometry()
    popctrs = statcan.boundary("population_centres")[["PCPUID", "geometry"]]
    o = overlays.overlay(popctrs, hexagons).reset_index(drop=True)

    o = o.rename(
        columns={
            "right_frac": "hex_frac",
            "right_area": "hex_area",
            "left_frac": "pc_frac",
            "left_area": "pc_area",
        }
    )

    #overlay generate some very narrow slices of empty areas,
    #looks like its where small slivers of the cities overlap in between 
    # hexagons where they don't 100% tesselate.
    o  = o.dropna(subset=["HEXuid_HEXidu"])
    
    o["HEXUID_PCPUID"] = o.HEXuid_HEXidu + "-" + o.PCPUID.fillna("XXXXXX").astype(str)

    #take first two letters of Hex ID to generate province two letter alpha code
    o["PRCODE"] = o["HEXuid_HEXidu"].apply(lambda s:s[0:2])

    return o


def hexagons_popctrs_combined():
    o = hexagons_popctrs_overlay()

    rural_hexes = o[pd.isna(o.PCPUID)]
    city_hexes = o[~pd.isna(o.PCPUID)]

    rural_hexes["HEXUID_PCPUID"] = rural_hexes["HEXUID_PCPUID"].str.replace(
        "-XXXXXX", ""
    )

    dissolved_cities = city_hexes.dissolve(
        by="PCPUID", aggfunc={"HEXuid_HEXidu": list}
    ).reset_index()
    dissolved_cities["HEXUID_PCPUID"] = dissolved_cities["PCPUID"]

    return pd.concat([dissolved_cities, rural_hexes])


def hexagons_small_popctrs_combined():
    o = hexagons_popctrs_overlay()

    popctrs = statcan.boundary("population_centres")

    o = o.merge(popctrs[["PCPUID", "PCNAME", "PCCLASS"]], on="PCPUID", how="outer")

    rural_hexes = o[pd.isna(o.PCPUID)]
    city_hexes = o[~pd.isna(o.PCPUID)]

    rural_hexes["HEXUID_PCPUID"] = rural_hexes["HEXUID_PCPUID"].str.replace(
        "-XXXXXX", ""
    )

    # dissolving on PCPUID includes the province code so Lloydminster and other 
    # multi-province cities aren't merged accross provincial borders.
    dissolved_cities = (
        city_hexes.loc[lambda s: s.PCCLASS != "4"]
        .dissolve(
            by="PCPUID",
            aggfunc={"HEXuid_HEXidu": list, "PCNAME": "first", "PCCLASS": "first", "PRCODE":"first"},
        )
        .reset_index()
    )
    dissolved_cities["HEXUID_PCPUID"] = dissolved_cities["PCPUID"]

    major_cities = city_hexes.loc[lambda s: s.PCCLASS == "4"]

    return pd.concat([major_cities, dissolved_cities, rural_hexes])

def _tile_join(geom, tiles, geom_index):
    if geom_index in tiles:
        warnings.warn(f"Tiles already have labels matching {geom_index}, skipping labelling.")
        return tiles
    
    unique_tiles = tiles[["quadkey", "geometry"]].drop_duplicates()

    join_result = (
        geom[[geom_index, "geometry"]]
        .to_crs(unique_tiles.crs)
        .sjoin(unique_tiles)
    )

    geom_labelled_tiles = tiles.merge(
        join_result[["quadkey", geom_index]], on="quadkey", how="left"
    )
    
    return geom_labelled_tiles

def add_simple_stats(boundary_geom, tiles, geom_index):
    geom_labelled_tiles = _tile_join(boundary_geom, tiles, geom_index)

    unique_devices = (
        geom_labelled_tiles.groupby(["quadkey", geom_index])["devices"]
        .sum()
        .reset_index()
        .groupby(geom_index)["devices"]
        .sum()
        .rename("unique_devices")
    )

    grps = geom_labelled_tiles.groupby(geom_index)
    ## calculate the obvious simple statistics
    aggs = pd.concat(
        [
            grps["avg_d_kbps"].mean(),
            grps["avg_d_kbps"].std().rename("std_d_kbps"),
            grps["avg_d_kbps"].min().rename("min_d_kbps"),
            grps["avg_d_kbps"].quantile(0.25).rename("25p_d_kbps"),
            grps["avg_d_kbps"].quantile(0.50).rename("50p_d_kbps"),
            grps["avg_d_kbps"].quantile(0.75).rename("75p_d_kbps"),
            grps["avg_d_kbps"].max().rename("max_d_kbps"),
            grps["avg_u_kbps"].mean(),
            grps["avg_d_kbps"].std().rename("std_u_kbps"),
            grps["avg_u_kbps"].min().rename("min_u_kbps"),
            grps["avg_u_kbps"].quantile(0.25).rename("25p_u_kbps"),
            grps["avg_u_kbps"].quantile(0.50).rename("50p_u_kbps"),
            grps["avg_u_kbps"].quantile(0.75).rename("75p_u_kbps"),
            grps["avg_u_kbps"].max().rename("max_u_kbps"),
            grps["avg_lat_ms"].mean(),
            # grps["avg_d_kbps"]
            # .agg(lambda x: np.mean(np.log(x)))
            # .rename("logmean_d_kbps"),
            # grps["avg_d_kbps"].agg(lambda x: np.var(np.log(x))).rename("logvar_d_kbps"),
            # grps["avg_u_kbps"]
            # .agg(lambda x: np.mean(np.log(x)))
            # .rename("logmean_u_kbps"),
            # grps["avg_u_kbps"].agg(lambda x: np.var(np.log(x))).rename("logvar_u_kbps"),
            # grps.apply(
            #     lambda df: sm.stats.weightstats.DescrStatsW(
            #         np.log(df["avg_d_kbps"]), df["tests"]
            #     ).mean
            # ).rename("weighted_logmean_d_kbps"),
            # grps.apply(
            #     lambda df: sm.stats.weightstats.DescrStatsW(
            #         np.log(df["avg_d_kbps"]), df["tests"]
            #     ).var
            # ).rename("weighted_logvar_d_kbps"),
            # grps.apply(
            #     lambda df: sm.stats.weightstats.DescrStatsW(
            #         np.log(df["avg_u_kbps"]), df["tests"]
            #     ).mean
            # ).rename("weighted_logmean_u_kbps"),
            # grps.apply(
            #     lambda df: sm.stats.weightstats.DescrStatsW(
            #         np.log(df["avg_u_kbps"]), df["tests"]
            #     ).var
            # ).rename("weighted_logvar_u_kbps"),
            grps["tests"].sum(),
            grps["tests"].mean().rename("ave_tests_per_tile"),
            unique_devices,
            # grps["devices"].sum(),
            grps["devices"].mean().rename("ave_devices_per_tile"),
            grps["avg_d_kbps"].count().rename("num_tiles"),
        ],
        axis=1,
    )

    return boundary_geom.merge(aggs, left_on=geom_index, right_index=True, how="left")


def add_50_10_stats(boundary_geom, tiles, geom_index):
    geom_labelled_tiles = _tile_join(boundary_geom, tiles, geom_index)

    grps = geom_labelled_tiles.groupby(geom_index)
    ## calculate the obvious simple statistics
    aggs = pd.concat(
        [
            grps["avg_d_kbps"]
            .apply(lambda s: 100 - scipy.stats.percentileofscore(s, 50_000))
            .rename("50_down_percentile"),
            grps["avg_u_kbps"]
            .apply(lambda s: 100 - scipy.stats.percentileofscore(s, 10_000))
            .rename("10_up_percentile"),
        ],
        axis=1,
    )

    return boundary_geom.merge(aggs, left_on=geom_index, right_index=True, how="left")


def add_tile_info(boundary_geom, tiles, geom_index):
    geom_labelled_tiles = _tile_join(boundary_geom, tiles, geom_index)

    geom_labelled_tiles["year+quarter"] = geom_labelled_tiles[
        ["year", "quarter"]
    ].apply(tuple, axis=1)

    grps = geom_labelled_tiles.groupby(geom_index)

    max_year = grps["year+quarter"].max()
    # max_year = max_year.year.astype(str) + " Q" + max_year.quarter.astype(str)
    # max_year = max_year.apply(lambda s: s[0] + " Q" + s[1], axis=1)
    max_year = max_year.rename("max_year")

    min_year = grps["year+quarter"].min()
    # min_year = min_year.year.astype(str) + " Q" + min_year.quarter.astype(str)
    min_year = min_year.rename("min_year")

    connections = grps["conn_type"].apply(set)
    connections = connections.rename("connections")

    aggs = pd.concat([min_year, max_year, connections], axis=1)

    return boundary_geom.merge(aggs, left_on=geom_index, right_index=True, how="left")


def add_logvar_stats(boundary_geom, tiles, geom_index):
    raise ValueError("Not implemented proplerly yet.")
    # TODO: remove stats from simple stat func
    unique_tiles = tiles[["quadkey", "geometry"]].drop_duplicates()

    join_result = (
        boundary_geom[[geom_index, "geometry"]]
        .to_crs(unique_tiles.crs)
        .sjoin(unique_tiles)
    )

    geom_labelled_tiles = tiles.merge(
        join_result[["quadkey", geom_index]], on="quadkey", how="left"
    )

    grps = geom_labelled_tiles.groupby(geom_index)
    aggs = pd.concat(
        [
            grps["avg_d_kbps"].mean(),
            grps["avg_d_kbps"].std().rename("std_d_kbps"),
            grps["avg_d_kbps"].min().rename("min_d_kbps"),
            grps["avg_d_kbps"].max().rename("max_d_kbps"),
            grps["avg_u_kbps"].mean(),
            grps["avg_lat_ms"].mean(),
            grps["avg_d_kbps"].std().rename("std_u_kbps"),
            grps["avg_u_kbps"].min().rename("min_u_kbps"),
            grps["avg_u_kbps"].max().rename("max_u_kbps"),
            grps["avg_d_kbps"]
            .agg(lambda x: np.mean(np.log(x)))
            .rename("logmean_d_kbps"),
            grps["avg_d_kbps"].agg(lambda x: np.var(np.log(x))).rename("logvar_d_kbps"),
            grps["avg_u_kbps"]
            .agg(lambda x: np.mean(np.log(x)))
            .rename("logmean_u_kbps"),
            grps["avg_u_kbps"].agg(lambda x: np.var(np.log(x))).rename("logvar_u_kbps"),
            grps.apply(
                lambda df: sm.stats.weightstats.DescrStatsW(
                    np.log(df["avg_d_kbps"]), df["tests"]
                ).mean
            ).rename("weighted_logmean_d_kbps"),
            grps.apply(
                lambda df: sm.stats.weightstats.DescrStatsW(
                    np.log(df["avg_d_kbps"]), df["tests"]
                ).var
            ).rename("weighted_logvar_d_kbps"),
            grps.apply(
                lambda df: sm.stats.weightstats.DescrStatsW(
                    np.log(df["avg_u_kbps"]), df["tests"]
                ).mean
            ).rename("weighted_logmean_u_kbps"),
            grps.apply(
                lambda df: sm.stats.weightstats.DescrStatsW(
                    np.log(df["avg_u_kbps"]), df["tests"]
                ).var
            ).rename("weighted_logvar_u_kbps"),
            grps["tests"].sum(),
            grps["tests"].mean().rename("ave_tests_per_tile"),
            grps["devices"].sum(),
            grps["devices"].mean().rename("ave_devices_per_tile"),
            grps["avg_d_kbps"].count().rename("num_tiles"),
        ],
        axis=1,
    )

    rvs_down = aggs.apply(
        lambda s: lognorm(
            s=np.sqrt(s.weighted_logvar_d_kbps),
            scale=np.exp(s.weighted_logmean_d_kbps),
        ),
        axis=1,
    )
    aggs["q25_down_kbps"] = rvs_down.apply(lambda x: x.ppf(0.25))
    aggs["q50_down_kbps"] = rvs_down.apply(lambda x: x.ppf(0.50))
    aggs["q75_down_kbps"] = rvs_down.apply(lambda x: x.ppf(0.75))
    aggs["q90_down_kbps"] = rvs_down.apply(lambda x: x.ppf(0.90))
    aggs["p>50Mbps_down"] = rvs_down.apply(lambda x: x.sf(50000))
    aggs["p>100Mbps_down"] = rvs_down.apply(lambda x: x.sf(100000))

    rvs_up = aggs.apply(
        lambda s: lognorm(
            s=np.sqrt(s.weighted_logvar_u_kbps),
            scale=np.exp(s.logmean_u_kbps),
        ),
        axis=1,
    )
    aggs["q25_up_kbps"] = rvs_up.apply(lambda x: x.ppf(0.25))
    aggs["q50_up_kbps"] = rvs_up.apply(lambda x: x.ppf(0.50))
    aggs["q75_up_kbps"] = rvs_up.apply(lambda x: x.ppf(0.75))
    aggs["q90_up_kbps"] = rvs_up.apply(lambda x: x.ppf(0.90))
    aggs["p>10Mbps_up"] = rvs_up.apply(lambda x: x.sf(10000))
    aggs["p>20Mbps_up"] = rvs_up.apply(lambda x: x.sf(20000))

    return boundary_geom.merge(aggs, left_on=geom_index, right_index=True, how="left")


def add_phh_pop(boundary_geom, phh, geom_index):
    phh = phh.loc[lambda s: s.Type != 8]  # remove PHH null points.

    if "Combined_50_10_Combine" in phh:
        phh["Pop2016_at_50_10_Combined"] = (
            phh["Combined_50_10_Combine"] * phh["Pop2016"]
        )
        phh["TDwell2016_at_50_10_Combined"] = (
            phh["Combined_50_10_Combine"] * phh["TDwell2016_TLog2016"]
        )
        phh["URDwell_at_50_10_Combined"] = (
            phh["Combined_50_10_Combine"] * phh["URDwell2016_RH2016"]
        )

    join_result = boundary_geom[[geom_index, "geometry"]].to_crs(phh.crs).sjoin(phh)

    grps = join_result.groupby(geom_index)
    aggs = pd.concat(
        [
            grps["Pop2016"].sum(),
            grps["TDwell2016_TLog2016"].sum(),
            grps["URDwell2016_RH2016"].sum(),
            grps["PHH_ID"].count().rename("PHH_Count"),
            grps["Type"]
            .apply(lambda df: df.value_counts().index[0])
            .rename("Common_Type"),
        ],
        axis=1,
    )

    if "Combined_50_10_Combine" in phh:
        speed_aggs = pd.concat(
            [
                grps["Pop2016_at_50_10_Combined"].sum(),
                grps["TDwell2016_at_50_10_Combined"].sum(),
                grps["URDwell_at_50_10_Combined"].sum(),
            ],
            axis=1,
        )

        aggs = pd.concat([aggs, speed_aggs], axis=1)

        # calculate percentages
        aggs["Pop_Avail_50_10"] = (
            aggs["Pop2016_at_50_10_Combined"] / aggs["Pop2016"] * 100
        )
        aggs["TDwell_Avail_50_10"] = (
            aggs["TDwell2016_at_50_10_Combined"] / aggs["TDwell2016_TLog2016"] * 100
        )

        aggs["URDwell_Avail_50_10"] = (
            aggs["URDwell_at_50_10_Combined"] / aggs["URDwell2016_RH2016"] * 100
        )

    return boundary_geom.merge(aggs, left_on=geom_index, right_index=True, how="left")
