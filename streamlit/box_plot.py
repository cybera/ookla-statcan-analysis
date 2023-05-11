import streamlit as st
import sys
sys.path.append("..")
import src.config
from src.datasets.loading import statcan, ookla

import numpy as np 
import pandas as pd
import geopandas as gp
import os
import plotly.graph_objects as go
import plotly.express as px

import matplotlib.pyplot as plt 


@st.cache_data
def load_csv_file(df_type:str, base_path: str, file_name:str):
    """
    load in the dataframe whether pandas or geopandas
    """
    
    full_path = os.path.join(base_path, file_name)
    if df_type == "pd":
        result = pd.read_csv(full_path)
    elif df_type == "gp":
        result = gp.read_file(full_path)
    return result


st.write("# Box Plotting for Internet Speed Analysis")

path_to_files = "data/dataframes/"
features_table = load_csv_file(df_type="gp", base_path=path_to_files, file_name="features_table.gpkg")


def get_databaset_subset_province_percentile(database: gp.geodataframe.GeoDataFrame,
                                             province_name:str,
                                             top_percentile:int,
                                             low_percentile:int) -> gp.geodataframe.GeoDataFrame:
    """
    part of the database will be retured that exist in the "province_name" and exists in
    the low_percentile to top_percentile of the population density.
    
    returns: the subset of dataframe
    """
    province_dataset = database[database["PRNAME"] == province_name]
    low_bound = province_dataset["POP_DENSITY"].quantile(low_percentile * 0.01)
    top_bound = province_dataset["POP_DENSITY"].quantile(top_percentile * 0.01)
    target_dataset = province_dataset[(province_dataset["POP_DENSITY"] > low_bound)& \
                                      (province_dataset["POP_DENSITY"] < top_bound)]
    return target_dataset
    

def get_filtered_download_and_upload_speeds(filtered_features_table, remove_outliers=False):
    """
    param:
    filtered_features_table -> Part of the whole dataset that is filtered based on province and population density
    
    return:
    The upload and download speeds after removing the outliers.
    """
    filtered_down_speed = filtered_features_table["avg_d_kbps"]
    filtered_up_speed = filtered_features_table["avg_u_kbps"]
    if remove_outliers:
        up_third_quartile = filtered_up_speed.quantile(0.75)
        down_third_quartile = filtered_up_speed.quantile(0.75)
    else:
        up_third_quartile = np.inf
        down_third_quartile = np.inf
    filtered_down_speed = filtered_down_speed[filtered_down_speed < down_third_quartile]
    filtered_up_speed = filtered_up_speed[filtered_up_speed < up_third_quartile]
    return filtered_down_speed, filtered_up_speed

input_col, _ = st.columns(2)

low_percentile = int(input_col.text_input("Lower bound percentile:", value='0'))
top_percentile = int(input_col.text_input("Upper bound percentile:", value='100'))

province_names = features_table["PRNAME"].unique().tolist()
selected_province = st.selectbox("Select a province", province_names)

filtered_features_table = get_databaset_subset_province_percentile(features_table,
                                                                  province_name=selected_province,
                                                                  top_percentile=top_percentile,
                                                                  low_percentile=low_percentile)
 
filtered_down_speed, filtered_up_speed = get_filtered_download_and_upload_speeds(filtered_features_table, remove_outliers=False)


if st.button("Filter and plot"):
    # Create the box plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Box(y=filtered_down_speed, name="Download Speed [Kbps]"))
    fig.add_trace(go.Box(y=filtered_up_speed, name="Upload Speed [Kbps]"))
    fig.update_layout(xaxis_title="Download/Upload", yaxis_title="Speed [Kbps]", 
        title={
            'text': f"{selected_province} Speeds",
            'y': 0.95,
            'x': 0.45,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'family': 'Arial', 'color': 'black'}
        })
    st.plotly_chart(fig)

    # calculate summary statistics
    down_stats = pd.Series(filtered_down_speed).describe()
    up_stats = pd.Series(filtered_up_speed).describe()

    # create a dataframe with the summary statistics
    stats_df = pd.DataFrame({
        "Download Speed [Kbps]": down_stats,
        "Upload Speed [Kbps]": up_stats
    })

    # display the table of summary statistics
    st.write("Summary Statistics:")
    st.table(stats_df)