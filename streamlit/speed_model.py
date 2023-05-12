import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import geopandas as gp
import src.config


# Function to load the dataset
@st.cache_data
def load_data(url):
    data = gp.read_file(url, driver="GPKG")
    return data


# Page 1: About the dataset
def about_data_page(data):
    st.header("Analysis of Download and Upload Internet Speed in Canadian Provinces")

    st.subheader("Dataset Description")
    st.write("This dataset provides a comprehensive view of the upload speed, download speed, and latency for different provinces across Canada.\
             The data was collected using the Speedtest by Ookla applications for Android and IOS and averaged for each tile. \
             More details about the dataset can be obtained from https://registry.opendata.aws/speedtest-global-performance")
    st.dataframe(data.drop(['geometry'], axis=1), width=900, height=300)

    st.subheader("Summary Statistics of the Dataset")
    st.write("To understand the distribution of the dataset, we looked at the summary statistics of the numerical columns of the dataset as follows:")
    st.write(data.describe())


# Page 2: Create and display the plot
def plot_page(data):
    fig = px.scatter(
    data,
    x="avg_d_kbps",
    y="connections",
    color="PRCODE",
    hover_name="PCCLASS",
    log_x=True,
    size_max=60,
)
    
    st.plotly_chart(fig, theme=None, use_container_width=True)

# Page 3: Layout Examples
def layout_examples_page():
    st.header("Streamlit Layout Examples \n Document: https://docs.streamlit.io/library/api-reference/layout")

    st.subheader("Columns")
    st.write("You can create columns in Streamlit using `st.columns()`. This allows you to arrange widgets or content side by side.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Column 1")
        st.button("Button 1")
    with col2:
        st.write("Column 2")
        st.button("Button 2")
    with col3:
        st.write("Column 3")
        st.button("Button 3")

    st.subheader("Expander")
    st.write("You can create expanders in Streamlit using `st.xpander()`. This allows you to show or hide content in a collapsible section.")
    
    with st.expander("Expandable Section"):
        st.write("This is an expandable section.")
        st.button("Button inside Expander")

    st.subheader("Container")
    st.write("You can create containers in Streamlit using `st.container()`. This allows you to group and organize content or widgets.")
    
    
    with st.container():
        st.write("This is a container.")
        st.button("Button inside Container")
    st.write('This is outside a container')
    # Page 4: Styling Examples
def styling_examples_page():
    # Add custom CSS styles
    st.markdown("""
    <style>
        .custom-header {
            color: #4a148c;
            font-weight: bold;
        }
        .custom-text {
            color: #388e3c;
            font-style: italic;
        }
        .custom-button button {
            background-color: #ff9800;
            border: 2px solid #f57c00;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        .custom-button:hover button {
            background-color: #f57c00;
            border-color: #ff9800;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='custom-header'>Custom Styled Header</h1>", unsafe_allow_html=True)
    st.markdown("<p class='custom-text'>This is custom styled text.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='custom-button'>", unsafe_allow_html=True)
    st.button("Custom Styled Button")
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    # Read in the dataset
    output_name = "LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg"
    output_dir = src.config.DATA_DIRECTORY / "processed" / "statistical_geometries"
    output_dir.mkdir(exist_ok=True)
   
    data = load_data(output_dir / output_name)

    # Define pages and their corresponding functions
    pages = {
        "About the Data": about_data_page,
        "Data Visualization": plot_page,
        "Layout Examples": layout_examples_page,
        "Styling Examples": styling_examples_page,
    }

    # Show a selection box in the sidebar to choose a page
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to", list(pages.keys()))

    # Call the corresponding function for the selected page
    if selected_page in ["About the Data", "Data Visualization"]:
        pages[selected_page](data)
    else:
        pages[selected_page]()

if __name__ == "__main__":
    main()




# def plot_indicator(data, selected_province, selected_connection, upload_speed):
#         filtered_data = data[(data['PRCODE'].isin(selected_province)) &
#                             (data['connections'] == selected_connection) &
#                             (data['avg_u_kbps'] == upload_speed)]
#         speed_type = ["Download Speed", "Upload Speed"]
#         selection = ""
#         if speed_type == "Download Speed":
#             selection == data['avg_d_kbps']
#         else:
#             selection == data['avg_u_kbps']
#         fig = sns.scatterplot(filtered_data,  x=selection, color='PRCODE',
#                     title=f"{selected_connection} for {', '.join(selected_province)} over time")
#         # fig = px.line(filtered_data, x=selection, color='PRCODE',
#         #             title=f"{selected_connection} for {', '.join(selected_province)} over time")

#         return fig

#     st.header("Interactive Visualization \n Ducoments:https://docs.streamlit.io/library/api-reference/charts")
#     st.subheader("Select countries, indicator, and year range to plot over time")
#     all_provinces = data['PRCODE'].unique()
#     all_connections = data['connections'].unique()
#     download_speed = data['avg_d_kbps']
#     upload_speed = data['avg_u_kbps']
#     filtered_data = data['PRCODE', 'connections', 'avg_u_kbps']
#     # speed_type = ["Download Speed", "Upload Speed"]

#     selected_province = st.multiselect("Choose province", options=all_provinces, default=['AB'])
#     selected_connection = st.multiselect("Choose connection type", options=all_connections, default=['fixed'])
#     # selected_speed = st.selectbox("Indicate internet speed", options= speed_type, index=0)

#     # min_year, max_year = int(data['Year'].min()), int(data['Year'].max())
#     # upload_speed = st.slider("Choose year range")

#     if selected_province:
#         fig = plot_indicator(filtered_data, selected_province, selected_connection, upload_speed)
#         st.plotly_chart(fig)
#     else:
#         st.write("No countries selected. Please select at least one country to plot th= selected indicator over time.")