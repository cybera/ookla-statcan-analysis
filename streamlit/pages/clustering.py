import streamlit as st
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

import numpy as np
import pandas as pd
import geopandas as gp
import src.config 
from src.datasets.loading import statcan
from notebooks.cluster import preparedata,AddCluster,best_k
from notebooks.clusterTable import import_table
from sklearn.cluster import KMeans
from OSMPythonTools.api import Api
from OSMPythonTools.nominatim import Nominatim

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from os.path import exists

def subset_province(prname,t):
    subset = t.loc[lambda s: s.PRNAME == prname]
    return subset
if exists("notebooks/cluster_table"):
    features_table=pd.read_pickle("notebooks/cluster_table")
else:
    features_table=import_table(download=True)

pr_names = list(features_table.loc[:, "PRNAME"].unique())
pr_names.append("All")

colors=['#2FA49F','#E6A49F','#9C379F','#9C372D','#FF672D','#FF67FF',
        '#0067FF','#00FAFF','#0046FF','#FF46BD','#F7005A','#96ACFF',
        '#004E00','#00AD00','#FFD800','#FFB497','#FFFF97','#FF1D97',
        '#301D02','#93FF02','#91E7FF']

pkey = 'quadkey'
target_vars = ['avg_d_kbps', 'avg_u_kbps']
calc_vars=['lat','lon','POP_DENSITY','das_area']
cat_vars=['CSDTYPE','PRNAME','SACTYPE']
col_subset = [pkey] + calc_vars+target_vars+cat_vars


# k=best_k(20,X,'k-means++',500,10,42)
# X=AddCluster(k=k,df=X)
#features_table[["cluster","centroids"]] = X[["cluster","centroids"]]

st.markdown("# :blue[🌏Clustering Areas with Similar Features] 🌏")

option = st.selectbox("Province", pr_names, index=pr_names.index("Alberta"))
if option=='All':
    pr_table=features_table
else:
    pr_table=subset_province(option,features_table)
X=preparedata(calc_vars,cat_vars,target_vars,df=pr_table)
k=best_k(20,X,'k-means++',100,10,42)
centers=AddCluster(k=k,df=X)
pr_table['cluster']=X['cluster']

colorsmap=zip(range(0,20),colors[:20])
colorsmap=dict(colorsmap)
pr_table['colors']=pr_table['cluster'].map(colorsmap)


fig = px.scatter_mapbox(pr_table, lat='lon', lon='lat',color='colors',hover_name='cluster',width=950, color_discrete_sequence=px.colors.qualitative.Light24)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

# M = folium.Map(location=[-79.12078857421875, 43.8206565436291], zoom_start=3, control_scale=True)
# #pr_table.head(20).explore("cluster",k=12,categorical=True,m=M)


# #Loop through each row in the dataframe
# for i,c in pr_table.sample(200).iterrows():
#     iframe = folium.IFrame('Province' )
#     popup = folium.Popup(iframe, min_width=300, max_width=300)
#     icon_color = colors[c['cluster']]
#     ICON=folium.Icon(color=icon_color, icon='')
#     folium.CircleMarker(location=[c['lat'],c['lon']],
#                   popup = popup,icon=ICON).add_to(M)

# st_data = st_folium(M, width=700) 

st.markdown(
    """
    From the above graph, we can see that eachj province has dramatically different color distribution. Due to the lack of data points in some areas, 
    we can only get a partial ituition of which of the areas can be grouped together. For those with sufficient data points, for example, Alberta, 
    is obviously grouped in to eastern and western parts, which indicates that we might want to consider to apply different strategies to these two 
    areas. 
    Similarly, we can conduct analysis on other area's maps, such as Ontario or countrywise.

    """
)
