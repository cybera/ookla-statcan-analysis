import streamlit as st
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

st.write("# Hello!")

st.write("""
This is a space to work and make a new app!
""")



#### EDA SECTION
st.write("A")

for_visualization = pd.read_csv("./data/Gap_Analysis.csv")
for_visualization["Percentage_gap"] = (for_visualization["Crt_Size_Total"]/for_visualization["Size_Total"])*100
for_visualization.sort_values(by="Percentage_gap", ascending=False,inplace=True)

st.write(for_visualization)

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



#### Clustering Section
st.write("A")




#### Other Activity Of Interest 
st.write("A")
