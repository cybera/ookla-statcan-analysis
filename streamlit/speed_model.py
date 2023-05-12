import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import geopandas as gp
import src.config
import matplotlib.pyplot as plt


# Function to load the dataset
@st.cache_data
def load_data(url):
    data = gp.read_file(url, driver="GPKG")
    return data

@st.cache_data
def load_data_csv(file):
    data = pd.read_csv(file)
    return data


# Page 1: About the dataset
def about_data_page(data):
    # Add custom CSS styles
    st.markdown("""
    <style>
        .custom-header {
            color: #4d4d99;
            font-weight: bold;
            text-align: left;
        }

        .custom-header2 {
            color: #000080;
            # font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='custom-header'>Analysis of Download and Upload Internet Speed in Canadian Provinces</h1>", unsafe_allow_html=True)
    # st.header("Analysis of Download and Upload Internet Speed in Canadian Provinces")

    st.markdown("<h3 class='custom-header2'>Dataset Description</h3>", unsafe_allow_html=True)
    # st.subheader("Dataset Description")
    st.write("This dataset provides a comprehensive view of the upload speed, download speed, and latency for different provinces across Canada.\
             The data was collected using the Speedtest by Ookla applications for Android and IOS and averaged for each tile. \
             More details about the dataset can be obtained from https://registry.opendata.aws/speedtest-global-performance")
    st.dataframe(data.drop(['geometry'], axis=1), width=900, height=300)

    st.markdown("<h3 class='custom-header2'>Summary Statistics of the Dataset</h3>", unsafe_allow_html=True)
    # st.subheader("Summary Statistics of the Dataset")
    st.write("To understand the distribution of the dataset, we looked at the summary statistics of the numerical columns of the dataset as follows:")
    st.write(data.describe())


# Page 2: Create and display the plot
def plot_page(data):
    # Add custom CSS styles
    st.markdown("""
    <style>
        .custom-header2 {
            color: #000080;
            # font-weight: bold;
        }
        .custom-text {
            color: #388e3c;
            font-style: italic;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='custom-header2'>Data Visualization</h2>", unsafe_allow_html=True)
    # st.header("Data Visualization")
    st.markdown("<h4 class='custom-text'>Please select the data research topic you would like to visualize:</h4>", unsafe_allow_html=True)
    # st.subheader("Please select the data research topic you would like to visualize")

    def figure_one(data):
        sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
        sns.set(rc={'figure.figsize':(11.7,8.27)})

        g = sns.boxplot(data=data, x="avg_d_kbps", 
                                    y="PCCLASS",  
                                    orient = 'h')
                                    #showfliers = False)

        plt.xlabel('Avg. Download in Kilobytes')
        plt.ylabel('Population Centre Type')
        plt.yticks([0, 1, 2], ['Small P. Centre', 'Medium P. Centre', 'Large P. Centre'])
        plt.title('Behavior of the Average Download Speed in 2019 for the defined Population Centres')
        plt.axvline(50000, linestyle='--')
        st.pyplot(g.figure)

    def figure_two(data):
        sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
        sns.set(rc={'figure.figsize':(11.7,8.27)})

        g = sns.scatterplot(data=data, x="POP_DENSITY", 
                                            y="avg_d_kbps", 
                                            hue="PCCLASS", 
                                            palette="deep")

        plt.xlabel('Population Density in 2019')
        plt.ylabel('Avg. Download in Kilobytes')
        plt.legend(title='Population Centre Type', loc='upper right')
        plt.title('Average Download Speed in contrast to the population density of 2019 for the defined Population Centres')
        plt.axhline(50000, linestyle='--')
        st.pyplot(g.figure)
    
    def figure_three(data):
        # Let's convert the NULL values into "Outside"
        data['PCCLASS'].fillna("Outside", inplace = True)
        sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
        sns.set(rc={'figure.figsize':(11.7,8.27)})

        g = sns.boxplot(data=data, x="avg_d_kbps", 
                                            y="PCCLASS",  
                                            orient = 'h')
                                            #showfliers = False)

        plt.xlabel('Avg. Download in Kilobytes')
        plt.ylabel('Population Centre Type')
        plt.title('Behavior of the Average Download Speed in 2019 for all areas - Population Centres vs. Rural/Outside areas')
        plt.axvline(50000, linestyle='--')
        st.pyplot(g.figure)

    def figure_four(data):
        sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
        sns.set(rc={'figure.figsize':(11.7,8.27)})

        g = sns.boxplot(data=data, x="avg_u_kbps", 
                                    y="PCCLASS",  
                                    orient = 'h')
                                    #showfliers = False)

        plt.xlabel('Avg. Upload in Kilobytes')
        plt.ylabel('Population Centre Type')
        plt.yticks([0, 1, 2], ['Small P. Centre', 'Medium P. Centre', 'Large P. Centre'])
        plt.title('Behavior of the Average Upload Speed in 2019 for the defined Population Centres')
        plt.axvline(50000, linestyle='--')
        st.pyplot(g.figure)

    def figure_five(data):
        sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
        sns.set(rc={'figure.figsize':(11.7,8.27)})

        g = sns.scatterplot(data=data, x="POP_DENSITY", 
                                            y="avg_u_kbps", 
                                            hue="PCCLASS", 
                                            palette="deep")

        plt.xlabel('Population Density in 2019')
        plt.ylabel('Avg. Upload in Kilobytes')
        plt.legend(title='Population Centre Type', loc='upper right')
        plt.title('Average Upload Speed in contrast to the population density of 2019 for the defined Population Centres')
        plt.axhline(50000, linestyle='--')
        st.pyplot(g.figure)
    
    def figure_six(data):
        # Let's convert the NULL values into "Outside"
        data['PCCLASS'].fillna("Outside", inplace = True)
        sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
        sns.set(rc={'figure.figsize':(11.7,8.27)})

        g = sns.boxplot(data=data, x="avg_u_kbps", 
                                            y="PCCLASS",  
                                            orient = 'h')
                                            #showfliers = False)

        plt.xlabel('Avg. Upload in Kilobytes')
        plt.ylabel('Population Centre Type')
        plt.title('Behavior of the Average Upload Speed in 2019 for all areas - Population Centres vs. Rural/Outside areas')
        plt.axvline(50000, linestyle='--')
        st.pyplot(g.figure)    
    
    figure_titles = ['Average Download Speed in contrast to the population density of 2019 for the defined Population Centres'\
                     , 'Average Upload Speed in contrast to the population density of 2019 for the defined Population Centres'\
                     , 'Behavior of the Average Download Speed in 2019 for the defined Population Centres'\
                     , 'Behavior of the Average Upload Speed in 2019 for the defined Population Centres'\
                     , 'Behavior of the Average Download Speed in 2019 for all areas - Population Centres vs. Rural/Outside areas'\
                     , 'Behavior of the Average Upload Speed in 2019 for all areas - Population Centres vs. Rural/Outside areas']
    selected_indicator = st.selectbox("Choose indicator", options=figure_titles, index=0)

    if selected_indicator == 'Behavior of the Average Download Speed in 2019 for the defined Population Centres':
        figure_one(data)
    elif selected_indicator == 'Average Download Speed in contrast to the population density of 2019 for the defined Population Centres':
        figure_two(data)
    elif selected_indicator == 'Behavior of the Average Download Speed in 2019 for all areas - Population Centres vs. Rural/Outside areas':
        figure_three(data)
    if selected_indicator == 'Behavior of the Average Upload Speed in 2019 for the defined Population Centres':
        figure_four(data)
    elif selected_indicator == 'Average Upload Speed in contrast to the population density of 2019 for the defined Population Centres':
        figure_five(data)
    elif selected_indicator == 'Behavior of the Average Upload Speed in 2019 for all areas - Population Centres vs. Rural/Outside areas':
        figure_six(data)

# Page 3: Layout Examples
def machine_learning_page():
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


def main():
    # Read in the dataset
    output_name = "LastFourQuartersOrBestEstimate_On_DissolvedSmallerCitiesHexes.gpkg"
    output_dir = src.config.DATA_DIRECTORY / "processed" / "statistical_geometries"
    output_dir.mkdir(exist_ok=True)

    output_2019_data = "Final.csv"
    output_2019_dir = src.config.DATA_DIRECTORY 
    output_2019_dir.mkdir(exist_ok=True)
   
    data = load_data(output_dir / output_name)

    data_2019 = load_data_csv(output_2019_dir / output_2019_data)

    # Define pages and their corresponding functions
    pages = {
        "About the Data": about_data_page,
        "Data Visualization": plot_page,
        "Machine Learning Output": machine_learning_page,
    }

    # Show a selection box in the sidebar to choose a page
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to", list(pages.keys()))

    # Call the corresponding function for the selected page
    if selected_page in ["About the Data"]:
        pages[selected_page](data)
    elif selected_page in ["Data Visualization"]:
        pages[selected_page](data_2019)
    else:
        pages[selected_page]()

if __name__ == "__main__":
    main()
