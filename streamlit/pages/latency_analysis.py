import streamlit as st

# Import pakcages
import src.config
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
import pickle
import plotly.express as px
import plotly.graph_objs as go
from statsmodels.tsa.api import ExponentialSmoothing


# Import data
output_dir = src.config.DATA_DIRECTORY / 'processed' 
output_dir.mkdir(exist_ok = True)
feature_pickle = output_dir / 'all_years_latency.pickle'

with open(feature_pickle, 'rb') as f:
    features_table = pickle.load(f)

features_table["CMANAME"] = features_table["CMANAME"].fillna("Rural")

for col in features_table:
    if "kbps" in col:
        features_table[col] /= 1000
        features_table.rename(columns={col:col.replace('kbps','Mbps')}, inplace=True)

# Create latency table (Latency over all Canada per year/quarter)
latency = features_table.groupby(['year', 'quarter']).apply(lambda x: (x.loc[:, 'avg_lat_ms'].mean()))
latency = latency.reset_index()
latency["y/q"] = "y"+ latency["year"].astype("str") + "q" + latency["quarter"].astype("str")
latency = latency.rename(columns={0:'Average Latency (ms)'})

latency_display_df = latency.drop(columns="y/q")

st.header("Internet Latency Over Time")

st.markdown(
    """
The Canadian government has commited to giving all Canadians access to at least 50/10 Mbps internet through their 
connectivity strategy. It has a committment to give 100 percent of Canadians thr ability of accessing 50/10 internet by 2030.
However, in the Connectivity Strategy, there is no mention of the latency of the internet made available. Although bandwidth is undoubtably very
important for high quality internet as this allows it to be fast, so is having a low latency. Throughout this page, the latency of internet
across Canada will be analyzed. 
"""
)
st.markdown(
    """
Below are a few scenarios of how having high latency can affect day-to-day internet usage:  
- **Browsing**: Can cause long page load times and unresponsiveness 
- **Video calling**: Can cause sync issues with the people you are calling with along with freezing  
- **Video gaming**: Manifests itself as lag when playing online multiplayer games. Your actions in the game will behind others with a lower latency, casuing the game to difficult to play 
"""
)


st.markdown("Data of Average Latency Over Time for Each Census Metropolitan Area in Canada")
st.dataframe(latency_display_df, width=800, height=200)

def plot_all_latency(latency, year_range):
        filtered_data = latency[(latency['year'].between(year_range[0], year_range[1]))]
        fig = px.line(filtered_data, x='y/q', y='Average Latency (ms)',
                    title=f"Average Latency Over Time", labels={"y/q":"Year / Quarter"})
        return fig


min_year_all, max_year_all = int(latency['year'].min()), int(latency['year'].max())
year_range_all = st.slider("Choose year range", min_value=min_year_all, max_value=max_year_all, value=(min_year_all, max_year_all), key=1)

fig = plot_all_latency(latency, year_range_all)
st.plotly_chart(fig)
st.write("From the above visualization, we can see that the average latency of internet has been steadily decreasing throughout Canada as a whole over the years 2019-2023.")

# Create cma_lat table (Latency over time divided by census metro area)

cma_lat = features_table.groupby(['CMANAME', 'year', 'quarter']).apply(lambda x: (x.loc[:, 'avg_lat_ms'].mean()))
cma_lat = cma_lat.reset_index()
cma_lat["y/q"] = "y"+ cma_lat["year"].astype("str") + "q" + cma_lat["quarter"].astype("str")
cma_lat = cma_lat.rename(columns={0:'Average Latency (ms)', 'CMANAME':'Metropolitan Area'})

def plot_latency(cma_lat, selected_areas, year_range):
        filtered_data = cma_lat[(cma_lat['Metropolitan Area'].isin(selected_areas)) &
                            (cma_lat['year'].between(year_range[0], year_range[1]))]

        fig = px.line(filtered_data, x='y/q', y='Average Latency (ms)', color='Metropolitan Area',
                    title=f" Average Latency (ms) for {', '.join(selected_areas)} Over Time", labels={"y/q":"Year / Quarter"})

        return fig

all_census_areas = cma_lat['Metropolitan Area'].unique()

selected_areas = st.multiselect("Choose Census Area", options=all_census_areas, default=['Vancouver', 'Calgary', 'Edmonton'])

min_year, max_year = int(cma_lat['year'].min()), int(cma_lat['year'].max())
year_range = st.slider("Choose year range", min_value=min_year, max_value=max_year, value=(min_year, max_year), key=2)

if selected_areas:
    fig = plot_latency(cma_lat, selected_areas, year_range)
    st.plotly_chart(fig)
else:
    st.write("No census areas selected. Please select at least one census area.")


# Show *highest and lowest latency areas via dataframe
st.markdown("Top 5 Census Metopolitan Areas with the Highest Latency")
st.table(cma_lat.drop(columns=["y/q", "year","quarter"]).groupby("Metropolitan Area").mean().reset_index().sort_values(by="Average Latency (ms)", ascending=False).head(5))

st.markdown(    """
A latency of 100ms or lower is ideal for browsing and calling and around 50-75ms for gaming. 
The above analysis shows that there is no issue with latency of internet in large metroploitan areas and even in the lower populated areas,
internet latency is not much of an issue.
One thing that should be noted regarding this analysis is that any areas that are not considered a census metropolitan area by Statistics Canada
is assigned the label "Rural". Further analysis could be done to look within this category to see if there are rural areas that do have significant
latency.
""")

st.markdown(    """
One thing that should be noted regarding this analysis is that any areas that are not considered a census metropolitan area by Statistics Canada
is assigned the label "Rural". Further analysis could be done to look within this category to see if there are rural areas that do have significant
latency.
""")
            
st.markdown("Tests With the Highest Latency")
st.table(features_table.loc[:,["avg_d_Mbps", "avg_u_Mbps","avg_lat_ms", "CMANAME","year", "quarter"]].sort_values(by="avg_lat_ms", ascending=False).head(10))

st.markdown(    """
As expected, most of the areas where the top 10 latency occured were in rural areas. Interestingly, we see Edmonton and Calgary appear as well.
There seems to be a correlation between download/upload speed and latency.
""")

avg_df = features_table.groupby(['CMANAME']).apply(lambda x: (x.loc[:, ['avg_lat_ms','avg_d_Mbps', 'avg_u_Mbps']].mean())).reset_index()
           
def plot_corr(avg_df, selected_areas, year_range):
        fig = px.scatter(avg_df, x="avg_lat_ms", y="avg_d_Mbps", title="Average Download Speed vs. Average Latency (ms)", trendline='ols')

        return fig

fig = plot_corr(avg_df, selected_areas, year_range)
st.plotly_chart(fig)
st.markdown("""We see a slight negative correlation between average download speed and average latency for each census metropolitan area. 
This means that overall, the **lower** the download speed, the **higher** the latency of the internet.
""")

st.subheader("Forecasting")

prophet_df = latency[["y/q","Average Latency (ms)"]]
prophet_df = prophet_df.rename(columns={"y/q":"ds","Average Latency (ms)":"y"})
prophet_df.set_index('ds', inplace=True)

model = ExponentialSmoothing(prophet_df,
                             trend='add', seasonal='add',seasonal_periods=4)
results = model.fit()
forecast = results.forecast(steps=11)

ind =  ["y2023q2", "y2023q3", "y2023q4", "y2024q1", "y2024q2", "y2024q3","y2024q4", "y2025q1", "y2025q2", "y2025q3", "y2025q4"]
forecast.index = pd.Index(ind)

trace1 = go.Scatter(x=prophet_df.index, y=prophet_df['y'], mode='lines', name='Observed')
trace2 = go.Scatter(x=forecast.index, y=forecast, mode='lines', name='Forecast')

data = [trace1, trace2]

layout = go.Layout(title='Exponential Smoothing Forecast of Latency to the end of 2025', xaxis=dict(title='Date'), yaxis=dict(title='Average Latency (ms)'))

fig = go.Figure(data=data, layout=layout)

st.plotly_chart(fig)

st.markdown("""
According to the exponential smoothing forecast, the average latency of internet in Canada will continue to steadily decrease over the next 3 years.
It should be noted that eventually there will be a limit to how low the latency can be. The latency on LAN is approximately 1-5ms. 
""")