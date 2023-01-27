import streamlit as st
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

import geopandas as gp
import src.config
from src.datasets.loading import statcan

from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim

output_name = "LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes"
output_dir = src.config.DATA_DIRECTORY / "processed" / "statistical_geometries"
output_dir.mkdir(exist_ok=True)

CRS = 'EPSG:4326'

nominatim = Nominatim()


popctrs = statcan.boundary('population_centres')

@st.experimental_singleton
def load_speed_data():
    print("Loading speed data...")

    speed_data = gp.read_file(output_dir / output_name, driver="MapInfo File")
    speed_data.crs = popctrs.crs

    speed_data['Ookla_Pop_at_50_10'] = speed_data['Pop2016'] *  speed_data['ookla_50_10_percentile']/100
    return speed_data

speed_data = load_speed_data()

statcan.boundary("census_divisions")

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
        'min_d_kbps','avg_d_kbps','max_d_kbps',
        'min_u_kbps','avg_u_kbps','max_u_kbps',
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

#####

pr_option = st.selectbox("Province", pr_names, index=pr_names.index("Alberta"))

er_options = ["All"]
er_options.extend(statcan.boundary("economic_regions").loc[lambda s:s.PRNAME == pr_option, 'ERNAME'])
er_option = st.selectbox("Economic Regions", er_options)

pin_location = None

f"Province selected: {pr_option}"
f"Economic region selected: {er_option}"

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
stats_table = speed_data_subset.groupby('PCCLASS')[["Pop2016",'Pop2016_at_50_10_Combined','Ookla_Pop_at_50_10']].sum()
stats_table["Percentage_StatCan"] = stats_table['Pop2016_at_50_10_Combined']/stats_table['Pop2016']*100
stats_table["Percentage_Ookla"] = stats_table['Ookla_Pop_at_50_10']/stats_table['Pop2016']*100
stats_table.rename(columns={"Pop2016_at_50_10_Combined":"StatCan_Pop_at_50_10"},inplace=True)
st.table(stats_table)

map = generate_map(pr_option, "All", er_option)
if pin_location:
    pin = folium.Marker(pin_location, popup="Search Location")
    pin.add_to(map)


st_folium(map, key='main-map', returned_objects=[], height=800, width=700)

st.write("Population Centres (excluding class 4 largest cities):")
st.table(
    speed_data_subset.loc[lambda s:s.PCCLASS.isin(['2','3']), ['HEXUID_PCPUID','PCNAME','P50_d_kbps','P50_u_kbps','Pop2016','Pop_Avail_50_10','ookla_50_10_percentile']].sort_values(by='PCNAME')
    )

