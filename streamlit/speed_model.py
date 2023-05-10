import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from src.datasets.loading import statcan, ookla


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
    for_visualization = for_visualization.rename({'Proviences': 'PRNAME'}, axis=1)
    for_visualization = statcan.boundary('provinces').merge(for_visualization[['PRNAME','Percentage_gap']],on="PRNAME",how='left')
    t = statcan.boundary('provinces').merge(for_visualization).plot(column='Percentage_gap', legend=True, missing_kwds={'color':'gray'})
    plt.gcf().suptitle("Gap in each provience for Download/Up speed of 50/10 Mbps")
    plt.gca().set(xlabel="% Percentage of Gap", ylabel="% Percentage of Gap")
    #plt.savefig('my_plot.png')
    return st.pyplot(plt)

#GAP analysis functions
bar_graph_for_GAP_analysis(for_visualization)
generating_map(for_visualization)

#### Population-wise Analysis

#### Clustering Section

#### Other Activity Of Interest 