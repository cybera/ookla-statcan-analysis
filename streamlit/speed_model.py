import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from src.datasets.loading import statcan, ookla
import seaborn as sns

import pickle
import bz2

st.write("# Canada Internet current status for 50/10 internet speed")
st.write("## Exploratory Data Analysis(EDA):")


#### EDA SECTION

#for_visualization = pd.read_csv("./data/Gap_Analysis.csv")
ifile = bz2.BZ2File("./data/Gap_Analysis.pickle",'rb')
for_visualization = pickle.load(ifile)
for_visualization["Percentage_gap"] = (for_visualization["Crt_Size_Total"]/for_visualization["Size_Total"])*100
for_visualization.sort_values(by="Percentage_gap", ascending=False,inplace=True)

def bar_graph_for_GAP_analysis(for_visualization):
    #st.write(for_visualization)
    fig = px.bar(
        for_visualization,
        y="Percentage_gap",
        x="Proviences",
        title="Ookla 50/10 GAP by Province",
    )
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig)

def generating_map(for_visualization):
    for_visualization_map = for_visualization.rename({'Proviences': 'PRNAME'}, axis=1)
    for_visualization_map = statcan.boundary('provinces').merge(for_visualization_map[['PRNAME','Percentage_gap']],on="PRNAME",how='left')
    t = statcan.boundary('provinces').merge(for_visualization_map).plot(column='Percentage_gap', legend=True, missing_kwds={'color':'gray'})
    plt.gcf().suptitle("Gap in each provience for Download/Up speed of 50/10 Mbps")
    plt.gca().set(xlabel="% Percentage of Gap", ylabel="% Percentage of Gap")
    return st.pyplot(plt)

def devices_speed_check_alberta(for_visualization_devices):
    for_visualization_download = for_visualization_devices[for_visualization_devices['PRNAME'] == 'Alberta' ]
    for_visualization_download = for_visualization_download.pivot_table(values='avg_d_mbps',index='PRNAME',columns='devices')
    fig, ax = plt.subplots()
    sns.heatmap(for_visualization_download,annot=True)
    return st.write(fig)

def devices_speed_check_all_provience(for_visualization_devices):
    ftr_down_all_provience = for_visualization_devices.pivot_table(values='avg_d_mbps',index='PRNAME',columns='devices')
    fig, ax = plt.subplots()
    sns.heatmap(ftr_down_all_provience,annot=True)
    return st.write(fig)
    #return st.pyplot(plt,use_container_width=True) 

def loading_file():
    ifile = bz2.BZ2File("./data/Features.pickle",'rb')
    for_visualization_devices = pickle.load(ifile) 
    for_visualization_devices["avg_d_mbps"]=for_visualization_devices["avg_d_kbps"]//1000.0
    for_visualization_devices["avg_u_mbps"]=for_visualization_devices["avg_u_kbps"]//1000.0
    return for_visualization_devices

#GAP analysis functions
for_visualization_devices = loading_file()

#EDA - NULL value
st.markdown("<h1 class='custom-header'>- Cleaning the data</h1>", unsafe_allow_html=True)
st.write(for_visualization_devices.isna().sum())
st.markdown("<h3 class='custom-header'><u>Insight:</u>As there are 11 columns where Null values are observed, it will be treated using mean/dropping of row based on the analysis of numeraic/categorical data</h3>", unsafe_allow_html=True)

#EDA - 5 step summary
st.markdown("<h1 class='custom-header'>- 5 number summary of the data</h1>", unsafe_allow_html=True)
st.write(for_visualization_devices.describe())
st.markdown("<h3 class='custom-header'><u>Insight:</u> It is quiet surprising that the '75%' of the locallity using on an average 7 devices while the maximum is at ~1500 devices</h3>", unsafe_allow_html=True)

#Q-1
st.markdown("<h1 class='custom-header'>1) Which provinces needs significant improvement in terms of the 50/10 internet speed criteria?</h1>", unsafe_allow_html=True)
#st.markdown(for_visualization_devices.describe())
bar_graph_for_GAP_analysis(for_visualization)
generating_map(for_visualization)
st.markdown("<h3 class='custom-header'><u>Conclusion:</u>  It is clear from the above graphs that Nunavut, Yukong needs at most improvement in their current 50/10 internet speeds.</h1>", unsafe_allow_html=True)

#Q-2
st.markdown("<h1 class='custom-header'>2) Relation between internet speed vs devices</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='custom-header'>We have a pre assumed conception that as the number of devices increases the internet speed in Download/Upload will decrease, thus to investiage we ploted a heatmap,</h4>", unsafe_allow_html=True)
#for_visualization_devices = pd.read_csv("./notebooks/Features.csv")
devices_speed_check_all_provience(for_visualization_devices)
devices_speed_check_alberta(for_visualization_devices)
st.markdown("<h3 class='custom-header'><u>Conclusion:</u>  Visualization clearly does not stand true to the preconcieved assumption. </h1>", unsafe_allow_html=True)

#### Population-wise Analysis

#### Clustering Section

#### Other Activity Of Interest 
