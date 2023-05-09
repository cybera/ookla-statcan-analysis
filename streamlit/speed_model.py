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

for_visualization = pd.read_csv("./notebooks/Gap_Analysis.csv")
for_visualization["Percentage_gap"] = (for_visualization["Crt_Size_Total"]/for_visualization["Size_Total"])*100
for_visualization.sort_values(by="Percentage_gap", ascending=False,inplace=True)

st.write(for_visualization)

fig = px.bar(
    for_visualization,
    y="Percentage_gap",
    x="Proviences",
    title="Ookla 50/10 GAP by Province",
)
# fig.add_hline(
#     y=canada_stats.loc["Urban", "Percentage_Ookla"],
#     annotation_text="% Percentage of GAP",
# )
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



#### Clustering Section
st.write("A")




#### Other Activity Of Interest 
st.write("A")
