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

output_name = "LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes"
output_dir = src.config.DATA_DIRECTORY / "processed" / "statistical_geometries"
output_dir.mkdir(exist_ok=True)

CRS = 'EPSG:4326'

nominatim = Nominatim()


popctrs = statcan.boundary('population_centres')

def convert_kbps_to_mbps(table, copy=False):
    if copy:
        table = table.copy()
    for col in table.columns:
        if 'kbps' not in col:
            continue
        table.loc[:,col] /= 1000
        table.rename(columns={col:col.replace('kbps','Mbps')}, inplace=True)
    return table

@st.experimental_singleton
def load_speed_data():
    print("Loading speed data...")

    speed_data = gp.read_file(output_dir / output_name, driver="MapInfo File")
    speed_data.crs = popctrs.crs

    speed_data['Ookla_Pop_at_50_10'] = speed_data['Pop2016'] *  speed_data['ookla_50_10_percentile']/100

    speed_data = convert_kbps_to_mbps(speed_data)

    speed_data['is_rural'] = ~speed_data.PCCLASS.isin(['2','3','4'])
    return speed_data

speed_data = load_speed_data()

#memoize boundary loading function
statcan.boundary = st.experimental_singleton(statcan.boundary)
# statcan.boundary("census_divisions")

pr_names = list(statcan.boundary('provinces').loc[:,'PRNAME'].unique())
# cd_names = statcan.boundary("census_divisions").loc[:, 'CDNAME'].unique()

@st.experimental_memo
def subset_region(prname, cdname="All", ername="All"):
    if cdname == "All" and ername == "All":
        area = statcan.boundary('provinces').loc[lambda s:s.PRNAME == prname]
        if len(area) > 1:
            print(f"Was expecting exactly one area to match on {prname}")
        return speed_data.sjoin(area,how='inner', predicate="intersects")
    elif ername != "All":
        area = statcan.boundary('economic_regions').loc[lambda s:(s.PRNAME==prname) & (s.ERNAME == ername)]
        if len(area) != 1 :
            print(f"Was expecting exactly one area to match on {prname}, {ername}")
        return speed_data.sjoin(area, how='inner', predicate='intersects')
    elif cdname != "All":
        area = statcan.boundary('census_divisions').loc[lambda s:(s.PRNAME==prname) & (s.CDNAME == cdname)]
        if len(area) != 1:
            print(f"Was expecting exactly one area to match on {prname}, {cdname}")
        return speed_data.sjoin(area, how='inner', predicate='intersects')
    
    raise RuntimeError("Oops this should have had 100% case coverage....")

#'covers', 'touches', 'within', 'overlaps', 'intersects', 'contains_properly', 'contains', None, 'crosses'
# print("Filtering to AB...")
# speed_data_subset = speed_data.sjoin(statcan.boundary('provinces').loc[lambda s:s.PRENAME == "Alberta"],how='inner', predicate="intersects") #intersects is default
#speed_data needs to be first to preserve geometry in join result.

# @st.cache
# def generate_map(gdf):
# @st.experimental_memo
def generate_map(prname, cdname="All", ername="All"):
    gdf = subset_region(prname, cdname, ername)
    print("Generating map")
    map = gdf.loc[lambda s:s.Pop2016 >0.0].explore(
    'ookla_50_10_percentile',#scheme='equalinterval', k = 4, 
    cmap=cm.StepColormap(['gray','red','orange','yellow','blue'], vmin=0, vmax=100, index=[0,1,25,50,75,100]),
    tooltip=['HEXUID_PCPUID','PCNAME','Pop2016','Pop_Avail_50_10','ookla_50_10_percentile'],
    popup=[
        'HEXUID_PCPUID','PCNAME',
        'min_d_Mbps','avg_d_Mbps','max_d_Mbps',
        'min_u_Mbps','avg_u_Mbps','max_u_Mbps',
        'Pop2016','tests','num_tiles','unique_devices', 'min_year','max_year','connections',
        'Pop_Avail_50_10','ookla_50_10_percentile','Down_50_percentile','Up_10_percentile']
    )
    return map

def lookup_address(address):
    results = nominatim.query(address).toJSON()
    return results


def address_speeds(results):
    result = results[0]
    print(result)
    coord = result['lat'], result['lon']
    geom = gp.points_from_xy(y=[coord[0]], x=[coord[1]])
    print(geom)
    result_data = gp.GeoDataFrame(results[0:1], geometry=geom, crs="EPSG:4326")
    
    result_data = result_data.to_crs(speed_data.crs)
    
    speed = result_data.sjoin(speed_data)
    return speed

def pcclass_percentage_breakdown(sample_data):
    stats_table = sample_data.groupby('PCCLASS')[["Pop2016",'Pop2016_at_50_10_Combined','Ookla_Pop_at_50_10']].sum()
    stats_table.index = pd.Index(pd.Series(stats_table.index).replace({'2':'Small','3':'Medium','4':'Large','':'Rural'}).values).rename("Population Center Type")
    stats_table = stats_table.append(sample_data[["Pop2016",'Pop2016_at_50_10_Combined','Ookla_Pop_at_50_10']].sum().rename("Total"))

    stats_table["Percentage_StatCan"] = stats_table['Pop2016_at_50_10_Combined']/stats_table['Pop2016']*100
    stats_table["Percentage_Ookla"] = stats_table['Ookla_Pop_at_50_10']/stats_table['Pop2016']*100
    stats_table.rename(columns={"Pop2016_at_50_10_Combined":"StatCan_Pop_at_50_10"},inplace=True)

    return stats_table

def rural_urban_percentage_breakdown(sample_data):
    stats_table = sample_data.groupby('is_rural')[["Pop2016",'Pop2016_at_50_10_Combined','Ookla_Pop_at_50_10']].sum()
    stats_table.index = pd.Index(pd.Series(stats_table.index).replace({True:'Rural',False:'Urban'}).values)
    stats_table = stats_table.append(sample_data[["Pop2016",'Pop2016_at_50_10_Combined','Ookla_Pop_at_50_10']].sum().rename("Total"))

    stats_table["Percentage_StatCan"] = stats_table['Pop2016_at_50_10_Combined']/stats_table['Pop2016']*100
    stats_table["Percentage_Ookla"] = stats_table['Ookla_Pop_at_50_10']/stats_table['Pop2016']*100
    stats_table.rename(columns={"Pop2016_at_50_10_Combined":"StatCan_Pop_at_50_10"},inplace=True)

    return stats_table
#####



st.header("Canada Wide 50/10 Internet")
st.markdown("""
The progress towards access to internet at download and upload speeds of 50/10 Mbps 
is evaluated to determine progress towards this federal access target. 
The National Broadband Map appears to over-estimate access to internet at 
this speed target when considering real speed test data from the open 
speed test data from Ookla. 
""")

st.markdown("""
The table below summarizes the populations what percentage have access 
to internet at the 50/10 level. At both urban and rural geographies the speed test 
data indicates fewer Canadians are accessing internet speeds 
at the 50/10 level than indicated by the National Broadband Map. 
""")
canada_stats = rural_urban_percentage_breakdown(speed_data)
canada_stats.replace({True:"Rural", False:"Urban"}, inplace=True)
canada_stats = canada_stats.loc[['Urban','Rural','Total'],['Pop2016','Percentage_StatCan','Percentage_Ookla']]
st.table(canada_stats.style.format(precision=0, thousands=",") )

for_pies = rural_urban_percentage_breakdown(speed_data)
for_pies["StatCan_Pop_below_50_10"] = for_pies.apply(lambda s:s.Pop2016 - s.StatCan_Pop_at_50_10, axis='columns')
for_pies["Ookla_Pop_below_50_10"] = for_pies.apply(lambda s:s.Pop2016 - s.Ookla_Pop_at_50_10, axis='columns')
# st.table(for_pies.T)

st.subheader("Canada 50/10 Access")
st.markdown("""
The below pie charts provide a visual comparison between 
the StatCan and Ookla derived 50/10 access levels at evaluated 
country-wide and for rural communities.
""")
col1, col2 = st.columns(2)


with col1:
    fig = px.pie(for_pies.loc[:,["StatCan_Pop_at_50_10","StatCan_Pop_below_50_10"]].T.reset_index(), values='Total', names='index', hole=0.6, height=180, title="StatCan 50/10")
    fig.update(layout_showlegend=False)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0))
    st.plotly_chart(fig , use_container_width=True)
with col2:
    fig = px.pie(for_pies.loc[:,["Ookla_Pop_at_50_10","Ookla_Pop_below_50_10"]].T.reset_index(), values='Total', names='index', hole=0.6, height=180, title="Ookla 50/10")
    fig.update(layout_showlegend=False)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0))
    st.plotly_chart(fig , use_container_width=True)

# st.subheader("Rural 50/10 Access")
col1, col2 = st.columns(2)
with col1:
    fig = px.pie(for_pies.loc[:,["StatCan_Pop_at_50_10","StatCan_Pop_below_50_10"]].T.reset_index(), values='Rural', names='index', hole=0.6, height=180, title='StatCan Rural 50/10')
    fig.update(layout_showlegend=False)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0))
    st.plotly_chart(fig , use_container_width=True)
with col2:
    fig = px.pie(for_pies.loc[:,["Ookla_Pop_at_50_10","Ookla_Pop_below_50_10"]].T.reset_index(), values='Rural', names='index', hole=0.6, height=180, title="Ookla Rural 50/10")
    fig.update(layout_showlegend=False)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=0))
    st.plotly_chart(fig , use_container_width=True)

#####

st.header("Mapping and Regional Statistics")
st.markdown("""
A map displaying internet speeds based on the Ookla 
speed test data is shown below. Data volume and performance 
require limiting the area to at least the province 
level. 
""")
pr_option = st.selectbox("Province", pr_names, index=pr_names.index("Alberta"))
er_options = ["All"]
er_options.extend(statcan.boundary("economic_regions").loc[lambda s:s.PRNAME == pr_option, 'ERNAME'])
er_option = st.selectbox("Economic Regions", er_options)

pin_location = None

f"Province selected: {pr_option}"
f"Economic region selected: {er_option}"

st.markdown("""
To help find locations on the map, it is possible to search for 
an address or named location using the text bar below, which uses 
OpenStreetMap. A table for the area searched is also displayed
after searching.
""")
addy_lookup = st.text_input("Address Search")
f"Typed Address: {addy_lookup if addy_lookup.strip() != '' else 'No Address Submitted'}"
if addy_lookup.strip() != "":
    search_result = lookup_address(addy_lookup)
    st.write(search_result)
    
    if search_result:
        pin_location = search_result[0]['lat'], search_result[0]['lon']

        searched_speeds = address_speeds(search_result)
        st.write('Stats for Searched Area')
        st.table(searched_speeds.T)


speed_data_subset = subset_region(pr_option, ername=er_option)

if len(speed_data_subset) == 0:
    st.write("Empty subset returned! :( T_T")

st.write("Statistics for province and (optional) economic region")
st.markdown("""
A more detailed breakdown of speeds for rural and urban areas for the selected 
area is shown below. Like above, this compares the percentage of 
people with access to internet at the 50/10 federal target. 
Beyond the urban/rural divide, we also see a more granular 
breakdown of Small/Medium/Large population centers and 
how this differs by province compared to the national average.
""")
st.table(pcclass_percentage_breakdown(speed_data_subset).style.format(precision=0, thousands=","))

map = generate_map(pr_option, "All", er_option)
if pin_location:
    pin = folium.Marker(pin_location, popup="Search Location")
    pin.add_to(map)


st_folium(map, key='main-map', returned_objects=[], height=800, width=700)

st.write("Population Centres (excluding class 4 largest cities):")
popctr_table = speed_data_subset.loc[lambda s:s.PCCLASS.isin(['2','3']), ['PCNAME','PCCLASS','P50_d_Mbps','P50_u_Mbps','Pop2016','Pop_Avail_50_10','ookla_50_10_percentile']].sort_values(by='PCNAME').set_index("PCNAME")
popctr_table["Discrepancy"] = popctr_table["Pop_Avail_50_10"] - popctr_table["ookla_50_10_percentile"]
popctr_table.rename(columns={"P50_d_Mbps":"Down Speed (Mbps)", "P50_u_Mbps":"Up Speed (Mbps)"}, inplace=True)
popctr_table.rename(columns={"Pop_Avail_50_10":"StatCan Pop at 50/10 (%)", "ookla_50_10_percentile":"Ookla Pop at 50/10 (%)"}, inplace=True)

st.dataframe(
    popctr_table.style.format(precision=0, thousands=","),
    height=1000
    )
