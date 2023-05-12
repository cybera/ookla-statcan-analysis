import streamlit as st
import src.config
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
import pickle
import plotly.express as px
import os
import subprocess


# Load data placed in "notebooks/" as generated by Clustering.ipynb and Population-wise_Analysis.ipynb. 
features_table = pd.read_pickle(r'notebooks/data.pickle')
ab_data = pd.read_pickle(r'notebooks/data_AB.pickle')


pkey = 'quadkey'
geometry = 'geometry'
id_and_names = ['DAUID', 'CDUID', 'CDNAME', 'CCSUID', 'CSDNAME', 'CMAUID', 'CMAPUID', 'CMANAME', 
'CCSNAME', 'CSDUID', 'ERUID', 'ERNAME', 'CTUID', 'CTNAME', 'ADAUID', 
'PCUID', 'PCNAME', 'PCPUID', 'SACCODE',] ##SACCODE is half a category half ID values

categorical_labels = [
    #'PRUID', #PRUID is redundant with PRNAME
    'PRNAME', 'CDTYPE', 
    'CSDTYPE',  
    'SACTYPE', 
    'CMATYPE', 'PCTYPE', 'PCCLASS',
]
numerical_vars = [
    'tests', 'devices',
    'das_area', 'tile_area', 'tile_frac',  'das_frac', 
    'DAPOP','POP_DENSITY'
]
target_vars = ['avg_d_kbps', 'avg_u_kbps']


def scatter_3d(df, x:str='CDTYPE', y:str='CSDTYPE', z:str='avg_d_kbps', color:str=''):
    if color=='':
        fig = px.scatter_3d(df, x=x, y=y, z=z)
    else:
        fig = px.scatter_3d(df, x=x, y=y, z=z, color=color, color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(
        autosize=False,
        width=1000,
        height=700
    )
    st.plotly_chart(fig)


st.markdown("""
# Population-wise Analysis

It is obvious that population has a big impact on internet availability and connection speeds. Population influences the demand, and in turn, the supply of internet services. Population density can also impact internet connectivity by causing interferences or by just division of bandwidth. Hence, it is important to analyze how exactly population affects our target variables. 
We expect that larger populations would lead to an increased demand and supply; but this will be true only up till a certain extent after which the internet services are not able to keep up with the demand. Similarly, we expect increased overcrowdedness to negatively impact internet connection speeds. 

### Now let us see what the data reveals for Alberta:
""")

st.markdown("Analyzing connection speeds vs. dissemination area population ")
fig = px.scatter(ab_data, x='DAPOP', y='avg_d_kbps', color='avg_u_kbps', color_continuous_scale=px.colors.sequential.Viridis)
st.plotly_chart(fig)


st.markdown("Analyzing connection speeds vs. population density")

fig = px.scatter(ab_data, x='POP_DENSITY', y='avg_d_kbps', color='avg_u_kbps', color_continuous_scale=px.colors.sequential.Viridis)
st.plotly_chart(fig)


st.markdown("Combined visualization")

scatter_3d(features_table.sample(50000), 'DAPOP', 'POP_DENSITY','avg_d_kbps', 'avg_u_kbps')

st.markdown("Analyzing with population center class")

features_table['PCCLASS'] = features_table['PCCLASS'].replace({"2": "Small", "3": "Medium", "4": "Large", "": "Rural"})
ab_data['PCCLASS'] = ab_data['PCCLASS'].replace({"2": "Small", "3": "Medium", "4": "Large", "": "Rural"})


np.random.seed(9)
scatter_3d(features_table.sample(50000), 'DAPOP', 'POP_DENSITY','avg_d_kbps', color='PCCLASS')

st.markdown("""
### Interpretations

- Areas with very high population or population density do not get very high speeds. This may indicate that high population density causes increased interference or division of bandwidth. 

- Download speeds converge to a point around 200000 kbps as population density increases. 


- Data is scattered homogeneously around the origin 
""")