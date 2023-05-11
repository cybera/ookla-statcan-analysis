import streamlit as st
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

import numpy as np
import pandas as pd
import geopandas as gp
import src.config 
from src.datasets.loading import statcan
from notebooks.cluster import preparedata,best_k,AddCluster
from notebooks.clusterTable import import_table

from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim

import plotly.express as px
import plotly.graph_objects as go

from os.path import exists

def subset_province(prname,t):
    pruid = (
        t.loc[lambda s: s.PRNAME == prname, "PRUID"].iloc[0]
    )
    subset = t.loc[lambda s: s.PRNAME == int(pruid)]
    return subset

if exists("notebooks/cluster_table"):
    features_table=pd.read_pickle("notebooks/cluster_table")
else:
    features_table=import_table(download=True)

pr_names = list(features_table.loc[:, "PRNAME"].unique())
pr_names.append("All")

colors=['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black']

pkey = 'quadkey'
target_vars = ['avg_d_kbps', 'avg_u_kbps']
calc_vars=['lat','lon','POP_DENSITY','das_area', 'tile_area', 'tile_frac',  'das_frac']
cat_vars=['CSDTYPE','PRNAME','SACTYPE']
col_subset = [pkey] + calc_vars+target_vars+cat_vars

X=preparedata(calc_vars,cat_vars,target_vars,df=features_table)
k=best_k(20,X,'k-means++',500,10,42)
X=AddCluster(k=k,df=X)
features_table[["cluster","centroids"]] = X[["cluster","centroids"]]

st.markdown("# :blue[🌏Clustering Areas with Similar Features] 🌏")

option = st.selectbox("Province", pr_names, index=pr_names.index("Alberta"))
if option=='All':
    pr_table=features_table
else:
    pr_table=subset_province(option,features_table)

pr_table['lat']=pr_table.apply(lambda x:float(x['lat']),axis=1)
pr_table['lon']=pr_table.apply(lambda x:float(x['lon']),axis=1)
pr_table['cluster']=pr_table.apply(lambda x:int(x['cluster'].astype(int)),axis=1)

m = folium.Map(location=[-79.12078857421875, 43.8206565436291], zoom_start=3, control_scale=True)

#Loop through each row in the dataframe
for i,row in pr_table.iterrows():
    iframe = folium.IFrame('Province' + str(row["PRNAME"]))
    popup = folium.Popup(iframe, min_width=300, max_width=300)
    icon_color = colors[row['cluster']]
    folium.Marker(location=[row['lat'],row['lon']],
                  popup = popup, icon=folium.Icon(color=icon_color, icon='')).add_to(m)

st_data = st_folium(m, width=700) 


