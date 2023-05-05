import streamlit as st
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

import pandas as pd
import geopandas as gp
import src.config
from src.datasets.loading import statcan

from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim

import plotly.express as px
import plotly.graph_objects as go

# memoize boundary loading function
statcan.boundary = st.experimental_singleton(statcan.boundary)

output_name = "LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg"
output_dir = src.config.DATA_DIRECTORY / "processed" / "statistical_geometries"
output_dir.mkdir(exist_ok=True)

CRS = "EPSG:4326"

nominatim = Nominatim()

PRCODE_MAP = {
    "NL": 10,
    "PE": 11,
    "NS": 12,
    "NB": 13,
    "QC": 24,
    "ON": 35,
    "MB": 46,
    "SK": 47,
    "AB": 48,
    "BC": 59,
    "YT": 60,
    "NT": 61,
    "NU": 62,
}

popctrs = statcan.boundary("population_centres")


def convert_kbps_to_mbps(table, copy=False):
    if copy:
        table = table.copy()
    for col in table.columns:
        if "kbps" not in col:
            continue
        table.loc[:, col] /= 1000
        table.rename(columns={col: col.replace("kbps", "Mbps")}, inplace=True)
    return table


@st.experimental_singleton
def load_speed_data():
    print("Loading speed data...")

    speed_data = gp.read_file(output_dir / output_name, driver="GPKG")

    speed_data["Ookla_Pop_at_50_10"] = (
        speed_data["Pop2016"] * speed_data["ookla_50_10_percentile"] / 100
    )

    speed_data = convert_kbps_to_mbps(speed_data)

    speed_data["is_rural"] = ~speed_data.PCCLASS.isin(["2", "3", "4"])

    speed_data["PRUID"] = speed_data["PRCODE"].replace(PRCODE_MAP)
    speed_data["PCCLASS"] = speed_data["PCCLASS"].fillna("")
    return speed_data


speed_data = load_speed_data()


pr_names = list(statcan.boundary("provinces").loc[:, "PRNAME"].unique())


@st.experimental_memo
def subset_region(prname, cdname="All", ername="All"):
    pruid = (
        statcan.boundary("provinces").loc[lambda s: s.PRNAME == prname, "PRUID"].iloc[0]
    )
    subset = speed_data.loc[lambda s: s.PRUID == int(pruid)]

    if ername != "All":
        area = (
            statcan.boundary("economic_regions")
            .to_crs(subset.crs)
            .loc[lambda s: (s.PRNAME == prname) & (s.ERNAME == ername)]
        )
        if len(area) != 1:
            print(f"Was expecting exactly one area to match on {prname}, {ername}")
        return subset.sjoin(area, how="inner", predicate="intersects")
    elif cdname != "All":
        area = (
            statcan.boundary("census_divisions")
            .to_crs(subset.crs)
            .loc[lambda s: (s.PRNAME == prname) & (s.CDNAME == cdname)]
        )
        if len(area) != 1:
            print(f"Was expecting exactly one area to match on {prname}, {cdname}")
        return subset.sjoin(area, how="inner", predicate="intersects")

    return subset


#'covers', 'touches', 'within', 'overlaps', 'intersects', 'contains_properly', 'contains', None, 'crosses'
# print("Filtering to AB...")
# speed_data_subset = speed_data.sjoin(statcan.boundary('provinces').loc[lambda s:s.PRENAME == "Alberta"],how='inner', predicate="intersects") #intersects is default
# speed_data needs to be first to preserve geometry in join result.


from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib as mpl

## there's some kind of weird bug interraction with the colormaps
## when there's nans that is only handled properly in geopandas
## when the cmap is a registered matplotlib colormap T_T :(
cmap = ListedColormap(["red", "orange", "yellow", "blue"], name="progress")
mpl.colormaps.register(cmap, force=True)

# @st.cache
# def generate_map(gdf):
# @st.experimental_memo
def generate_map(prname, cdname="All", ername="All"):
    gdf = subset_region(prname, cdname, ername)
    print("Generating map")
    map = gdf.loc[lambda s: s.Pop2016 > 0.0].explore(
        "ookla_50_10_percentile",
        scheme="equalinterval",
        k=4,
        # cmap=cm.StepColormap(
        #     ["gray", "red", "orange", "yellow", "blue"],
        #     vmin=0,
        #     vmax=100,
        #     index=[0, 1, 25, 50, 75, 100],
        # ),
        cmap="progress",
        legend=True,
        tooltip=[
            "HEXUID_PCPUID",
            "PCNAME",
            "Pop2016",
            "Pop_Avail_50_10",
            "ookla_50_10_percentile",
        ],
        popup=[
            "HEXUID_PCPUID",
            "PCNAME",
            "min_d_Mbps",
            "avg_d_Mbps",
            "max_d_Mbps",
            "min_u_Mbps",
            "avg_u_Mbps",
            "max_u_Mbps",
            "Pop2016",
            "tests",
            "num_tiles",
            "unique_devices",
            "min_year",
            "max_year",
            "connections",
            "Pop_Avail_50_10",
            "ookla_50_10_percentile",
            "Down_50_percentile",
            "Up_10_percentile",
        ],
    )
    return map


def lookup_address(address):
    results = nominatim.query(address).toJSON()
    return results


def address_speeds(results):
    result = results[0]
    print(result)
    coord = result["lat"], result["lon"]
    geom = gp.points_from_xy(y=[coord[0]], x=[coord[1]])
    print(geom)
    result_data = gp.GeoDataFrame(results[0:1], geometry=geom, crs="EPSG:4326")

    result_data = result_data.to_crs(speed_data.crs)

    speed = result_data.sjoin(speed_data)
    return speed


def pcclass_percentage_breakdown(sample_data):
    stats_table = sample_data.groupby("PCCLASS")[
        ["Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"]
    ].sum()
    stats_table.index = pd.Index(
        pd.Series(stats_table.index)
        .replace({"2": "Small", "3": "Medium", "4": "Large", "": "Rural"})
        .values
    ).rename("Population Center Type")
    # stats_table = stats_table.append(
    #     sample_data[["Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"]]
    #     .sum()
    #     .rename("Total")
    # )
    other = sample_data[["Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"]].sum().rename("Total")
    other = pd.DataFrame(other).T
    stats_table = pd.concat([stats_table, other],axis=0)

    stats_table["Percentage_StatCan"] = (
        stats_table["Pop2016_at_50_10_Combined"] / stats_table["Pop2016"] * 100
    )
    stats_table["Percentage_Ookla"] = (
        stats_table["Ookla_Pop_at_50_10"] / stats_table["Pop2016"] * 100
    )
    stats_table.rename(
        columns={"Pop2016_at_50_10_Combined": "StatCan_Pop_at_50_10"}, inplace=True
    )

    return stats_table


def rural_urban_percentage_breakdown(sample_data):
    stats_table = sample_data.groupby("is_rural")[
        ["Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"]
    ].sum()
    stats_table.index = pd.Index(
        pd.Series(stats_table.index).replace({True: "Rural", False: "Urban"}).values
    )
    # st.write(stats_table)
    # stats_table = stats_table.append(
    #     sample_data[["Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"]]
    #     .sum()
    #     .rename("Total")
    # )
    other = (sample_data[["Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"]]
        .sum()
        .rename("Total")
    )
    other = pd.DataFrame(other).T
    stats_table = pd.concat([stats_table, other],axis=0)

    stats_table["Percentage_StatCan"] = (
        stats_table["Pop2016_at_50_10_Combined"] / stats_table["Pop2016"] * 100
    )
    stats_table["Percentage_Ookla"] = (
        stats_table["Ookla_Pop_at_50_10"] / stats_table["Pop2016"] * 100
    )
    stats_table.rename(
        columns={"Pop2016_at_50_10_Combined": "StatCan_Pop_at_50_10"}, inplace=True
    )

    return stats_table


#####


st.header("Canada Wide 50/10 Internet")
st.markdown(
    """
The progress towards access to internet at download and upload speeds of 50/10 Mbps 
is evaluated to determine progress towards this federal access target. 
The National Broadband Map appears to over-estimate access to internet at 
this speed target when considering real speed test data from the open 
speed test data from Ookla. 
"""
)

st.markdown(
    """
The table below summarizes the populations what percentage have access 
to internet at the 50/10 level. At both urban and rural geographies the speed test 
data indicates fewer Canadians are accessing internet speeds 
at the 50/10 level than indicated by the National Broadband Map. 
"""
)
canada_stats = rural_urban_percentage_breakdown(speed_data)
canada_stats.replace({True: "Rural", False: "Urban"}, inplace=True)
canada_stats = canada_stats.loc[
    ["Urban", "Rural", "Total"], ["Pop2016", "Percentage_StatCan", "Percentage_Ookla"]
]
st.table(canada_stats.style.format(precision=0, thousands=","))

for_pies = rural_urban_percentage_breakdown(speed_data)
for_pies["StatCan_Pop_below_50_10"] = for_pies.apply(
    lambda s: s.Pop2016 - s.StatCan_Pop_at_50_10, axis="columns"
)
for_pies["Ookla_Pop_below_50_10"] = for_pies.apply(
    lambda s: s.Pop2016 - s.Ookla_Pop_at_50_10, axis="columns"
)
# st.table(for_pies.T)

st.subheader("Canada 50/10 Access")
st.markdown(
    """
The below pie charts provide a visual comparison between 
the StatCan and Ookla derived 50/10 access levels at evaluated 
country-wide and for rural communities.
"""
)
col1, col2 = st.columns(2)

# ensure consistent legend/color labelling
explicit_pie_colors = {
    "StatCan_Pop_at_50_10": "blue",
    "StatCan_Pop_below_50_10": "gray",
    "Ookla_Pop_at_50_10": "blue",
    "Ookla_Pop_below_50_10": "gray",
}


def prog_pies(labels, total_or_rural, title):
    fig = px.pie(
        for_pies.loc[:, labels].T.reset_index(),
        values=total_or_rural,
        names="index",
        color="index",
        hole=0.6,
        height=180,
        title=title,
        color_discrete_map=explicit_pie_colors,
        category_orders={"index": labels},
    )
    fig.update(layout_showlegend=False)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0))

    return fig


with col1:
    fig = prog_pies(
        ["StatCan_Pop_at_50_10", "StatCan_Pop_below_50_10"], "Total", "StatCan 50/10"
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = prog_pies(
        ["Ookla_Pop_at_50_10", "Ookla_Pop_below_50_10"], "Total", "Ookla 50/10"
    )
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig = prog_pies(
        ["StatCan_Pop_at_50_10", "StatCan_Pop_below_50_10"],
        "Rural",
        "StatCan Rural 50/10",
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = prog_pies(
        ["Ookla_Pop_at_50_10", "Ookla_Pop_below_50_10"], "Rural", "Ookla Rural 50/10"
    )
    st.plotly_chart(fig, use_container_width=True)

#####
# st.write(speed_data)
pr_stats = speed_data.groupby(["PRCODE", "is_rural"])[[
    "Pop2016", "Pop2016_at_50_10_Combined", "Ookla_Pop_at_50_10"
]].sum()
pr_stats = pd.DataFrame(pr_stats).reset_index()
pr_stats["Pop2016_below_50_10_Combined"] = (
    pr_stats["Pop2016"] - pr_stats["Pop2016_at_50_10_Combined"]
)
pr_stats["Ookla_Pop_below_50_10"] = pr_stats["Pop2016"] - pr_stats["Ookla_Pop_at_50_10"]
pr_stats["StatCan_Percentage"] = (
    pr_stats["Pop2016_at_50_10_Combined"] / pr_stats["Pop2016"] * 100
)
pr_stats["Ookla_Percentage"] = (
    pr_stats["Ookla_Pop_at_50_10"] / pr_stats["Pop2016"] * 100
)

# pr_stats
# fig = go.Figure(data=[go.bar(name="Urban", x="")])


largest_rural_pr, largest_rural_pop = (
    pr_stats.loc[lambda s: s.is_rural]
    .sort_values(by=["Ookla_Pop_below_50_10"], ascending=False)
    .iloc[0]
    .loc[["PRCODE", "Ookla_Pop_below_50_10"]]
)
lowest_percent_pr, lowest_percent = (
    pr_stats.loc[lambda s: s.is_rural]
    .sort_values(by=["Ookla_Percentage"], ascending=True)
    .iloc[0]
    .loc[["PRCODE", "Ookla_Percentage"]]
)
st.markdown(
    """
## Progress by Province
By province, the percentage of people living in areas 
with internet speeds above the 50/10 access level 
varies. For example, {} has the largest 
rural population of {:,.0f} lacking access to internet speeds at the 50/10 level.
While, {} has the lowest percentage coverage for rural areas 
with {:.0f}% of the population at the target level.
""".format(
        largest_rural_pr, largest_rural_pop, lowest_percent_pr, lowest_percent
    )
)

fig = px.bar(
    pr_stats,
    y="Ookla_Percentage",
    x="PRCODE",
    color="is_rural",
    barmode="group",
    labels=dict(Ookla_Percentage="Population >50/10 (%)"),
    category_orders={"PRCODE": list(PRCODE_MAP.keys())},
    title="Ookla 50/10 Progress by Province",
)
fig.add_hline(y=canada_stats.loc["Urban", "Percentage_Ookla"])
fig.add_hline(y=canada_stats.loc["Rural", "Percentage_Ookla"])
fig.update_yaxes(range=[0, 100])
st.plotly_chart(fig)

st.markdown(
    """
We can compare the Ookla values, with those data as published by 
in the National Broadband Map, broken down by province. Generally, 
the trend is that the Ookla access is lower than the 
published access levels. A few provinces, like Prince Edward Island 
or Saskatchewan have substantial differences of 30% or more.
"""
)
fig = px.bar(
    pr_stats,
    y="StatCan_Percentage",
    x="PRCODE",
    color="is_rural",
    barmode="group",
    labels=dict(Ookla_Percentage="Population >50/10 (%)"),
    category_orders={"PRCODE": list(PRCODE_MAP.keys())},
    title="StatCan Values",
)
fig.add_hline(y=canada_stats.loc["Urban", "Percentage_StatCan"])
fig.add_hline(y=canada_stats.loc["Rural", "Percentage_StatCan"])
fig.update_yaxes(range=[0, 100])
st.plotly_chart(fig)

st.markdown(
    """
Because the populations of the provinces are so vastly different, 
in addition to the percentage, it is important to 
note the actual population numbers of those affected. This can 
be important as well, since Quebec sports a higher than average 
rural access rate, it does also have a large population 
of rural inhabitants who appear to lack access to suitable internet 
speeds.
"""
)
fig = px.bar(
    pr_stats,
    y="Ookla_Pop_below_50_10",
    x="PRCODE",
    color="is_rural",
    category_orders={"PRCODE": list(PRCODE_MAP.keys())},
    labels={"Ookla_Pop_below_50_10": "Population <50/10 (N)"},
    title="Ookla Populations Lacking Access to 50/10 by Province",
)
st.plotly_chart(fig)
####

st.header("Mapping and Regional Statistics")
st.markdown(
    """
A map displaying internet speeds based on the Ookla 
speed test data is shown below. Data volume and performance 
require limiting the area to at least the province 
level. 
"""
)
pr_option = st.selectbox("Province", pr_names, index=pr_names.index("Alberta"))
er_options = ["All"]
er_options.extend(
    statcan.boundary("economic_regions").loc[lambda s: s.PRNAME == pr_option, "ERNAME"]
)
er_option = st.selectbox("Economic Regions", er_options)

pin_location = None

f"Province selected: {pr_option}"
f"Economic region selected: {er_option}"

st.markdown(
    """
To help find locations on the map, it is possible to search for 
an address or named location using the text bar below, which uses 
OpenStreetMap. A table for the area searched is also displayed
after searching.
"""
)
addy_lookup = st.text_input("Address Search")
f"Typed Address: {addy_lookup if addy_lookup.strip() != '' else 'No Address Submitted'}"
if addy_lookup.strip() != "":
    search_result = lookup_address(addy_lookup)
    st.write(search_result)

    if search_result:
        pin_location = search_result[0]["lat"], search_result[0]["lon"]

        searched_speeds = address_speeds(search_result)
        st.write("Stats for Searched Area")
        st.table(searched_speeds.T)


speed_data_subset = subset_region(pr_option, ername=er_option)

if len(speed_data_subset) == 0:
    st.write("Empty subset returned! :( T_T")

st.write("Statistics for province and (optional) economic region")
st.markdown(
    """
A more detailed breakdown of speeds for rural and urban areas for the selected 
area is shown below. Like above, this compares the percentage of 
people with access to internet at the 50/10 federal target. 
Beyond the urban/rural divide, we also see a more granular 
breakdown of Small/Medium/Large population centers and 
how this differs by province compared to the national average.
"""
)
st.table(
    pcclass_percentage_breakdown(speed_data_subset).style.format(
        precision=0, thousands=","
    )
)

map = generate_map(pr_option, "All", er_option)
if pin_location:
    pin = folium.Marker(pin_location, popup="Search Location")
    pin.add_to(map)


st_folium(map, key="main-map", returned_objects=[], height=800, width=700)

st.write("Population Centres (excluding class 4 largest cities):")
popctr_table = (
    speed_data_subset.loc[
        lambda s: s.PCCLASS.isin(["2", "3"]),
        [
            "PCNAME",
            "PCCLASS",
            "P50_d_Mbps",
            "P50_u_Mbps",
            "Pop2016",
            "Pop_Avail_50_10",
            "ookla_50_10_percentile",
        ],
    ]
    .sort_values(by="PCNAME")
    .set_index("PCNAME")
)
popctr_table["Discrepancy"] = (
    popctr_table["Pop_Avail_50_10"] - popctr_table["ookla_50_10_percentile"]
)
popctr_table.rename(
    columns={"P50_d_Mbps": "Down Speed (Mbps)", "P50_u_Mbps": "Up Speed (Mbps)"},
    inplace=True,
)
popctr_table.rename(
    columns={
        "Pop_Avail_50_10": "StatCan Pop at 50/10 (%)",
        "ookla_50_10_percentile": "Ookla Pop at 50/10 (%)",
    },
    inplace=True,
)

st.dataframe(popctr_table.style.format(precision=0, thousands=","), height=1000)

st.markdown(
    """
# Code and Analysis

This Streamlit App and associated python code 
used for the analysis is available at the 
following public GitHub repository: 
[github.com/cybera/ookla-statcan-analysis](https://github.com/cybera/ookla-statcan-analysis)
"""
)
