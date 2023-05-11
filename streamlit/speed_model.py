import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from src.datasets.loading import statcan, ookla
import seaborn as sns


st.write("# Canada Internet")
st.write("## JT Take Us To The Promised Land (of 50/10)")
=======


st.markdown("<h1 class='custom-header'>1) Exploring the data</h1>", unsafe_allow_html=True)

#### EDA SECTION

for_visualization = pd.read_csv("./data/Gap_Analysis.csv")
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

    st.markdown(
        """
    We are comparing the gap between expected 100% Canadians having >50Mbps Download & >10Mbps uplod speed but the graph show how much % of localities lag the speed expected.
    """
    )

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

#GAP analysis functions
bar_graph_for_GAP_analysis(for_visualization)
generating_map(for_visualization)
for_visualization_devices = pd.read_csv("./notebooks/Features.csv")
devices_speed_check_all_provience(for_visualization_devices)
devices_speed_check_alberta(for_visualization_devices)


#### Population-wise Analysis

#### Clustering Section

#### Other Activity Of Interest 