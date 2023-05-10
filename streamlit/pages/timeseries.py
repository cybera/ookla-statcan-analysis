import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import matplotlib.pyplot as plt

st.set_page_config(page_title='Time Series', page_icon='📈')

st.markdown('# Internet Speed Though Time')
st.sidebar.header("Time Series")
st.markdown('## 1. Time Series Plots and Insights')
st.markdown('### 1.1. Internet Speed Development since 2019-Q1')
st.markdown('Following time series line chart display the development of internet speed at provinces.')

@st.cache_data
def data_reading(path):
    my_df = pd.read_csv(path)
    return my_df
    
data_path = 'data/model_data/speed_data_grouped.csv'
df = data_reading(data_path)
df['year-quarter'] = df['year'].astype(str) + 'Q' + df['quarter'].astype(str)
df['DU_Ratio'] = df['avg_d_kbps'].astype(float) / df['avg_u_kbps'].astype(float)
    
p1 = st.selectbox('Select Province 1', df['PR'].unique(), index=df['PR'].unique().tolist().index('AB'))    
o1 = st.multiselect('Select Options', ['Upload', 'Download'], default = 'Download')

def generate_graph1(province, options):
    filtered_df = df[df['PR'] == province]
    
    fig = go.Figure()
    
    if "Upload" in options:
        fig.add_trace(go.Scatter(x=filtered_df['year-quarter'], 
                                 y=filtered_df['avg_u_kbps'], 
                                 name='Upload Speed'))

    if "Download" in options:
        fig.add_trace(go.Scatter(x=filtered_df['year-quarter'], 
                                 y=filtered_df['avg_d_kbps'], 
                                 name='Download Speed'))

    fig.update_layout(title=f'Internet Speed Development in {province}<br><sub>Local data was aggregated on province level<sub>', 
                          xaxis_title='Time', 
                          template = 'simple_white',
                          yaxis_title='Internet Speed (kbps)')
    return fig
fig = generate_graph1(p1, o1)
st.plotly_chart(fig)

st.markdown('**Insights**')
st.markdown('will add one paragraph here')

st.markdown('### 1.2. Download & Upload Speed Comparison')
st.markdown('Following time series line chart display the relative development of download and upload speeds at provinces.')

p2 = st.selectbox('Select Province 2', df['PR'].unique(), index=df['PR'].unique().tolist().index('AB'))    
def generate_graph2(province):
    filtered_df = df[df['PR'] == province]
    
    fig_2 = go.Figure()
    fig_2.add_trace(go.Scatter(x=filtered_df['year-quarter'], 
                             y=filtered_df['DU_Ratio'], 
                                 name='Download / Upload Speed'))

    fig_2.update_layout(title=f'Comparing Download and Upload Speeds in {province}<br><sub>Local data was aggregated on province level<sub>', 
                      xaxis_title='Time', 
                      template = 'simple_white',
                      yaxis_title='Speed Ratio')
    return fig_2
fig_2 = generate_graph2(p2)
st.plotly_chart(fig_2)

st.markdown('**Insights**')
st.markdown('will add one paragraph here')

st.markdown('### 1.3. Comparing Provinces')
st.markdown('Following running bar plot display the ranking of provinces in terms of download or upload speeds.')

o3 = st.selectbox('Select Any Option', ['Upload', 'Download'], index = 1)

def generate_graph3(option):
    colors = ['crimson']
    if o3 == 'Upload':
        df_sorted = df.sort_values(['year-quarter', 'avg_u_kbps'], ascending=[True, False])
        fig_3 = px.bar(df_sorted,
                       x = 'PR',
                       y = 'avg_u_kbps',
                       animation_frame = 'year-quarter',
                       color_discrete_sequence = colors)
    elif o3 == 'Download':
        df_sorted = df.sort_values(['year-quarter', 'avg_d_kbps'], ascending=[True, False])
        fig_3 = px.bar(df_sorted,
                       x = 'PR',
                       y = 'avg_d_kbps',
                       animation_frame = 'year-quarter',
                       color_discrete_sequence = colors)
        
    fig_3.update_layout(title='Comparing Provinces Through Time<br><sub>Local data was aggregated on province level<sub>', 
                        xaxis_title='Provinces', 
                        template = 'simple_white',
                        yaxis_title='Internet Speed (kbps)')
    return fig_3
fig_3 = generate_graph3(o3)
st.plotly_chart(fig_3)

st.markdown('**Insights**')
st.markdown('will add one paragraph here. Remember: Nunavut has 3 missing data points: 2019Q1, 2019Q2 ans 2020Q3 therefore cannot be plotted inside the running bar plot for some periods.')

st.markdown('## 2. Attempting an ARIMA Model (Alberta)')

data_path = 'data/model_data/Alberta_Speed_Data_Grouped.csv'
AB_df = data_reading(data_path)
time_index = pd.date_range(start='2019-Q1', end='2023-Q2', freq='Q')
AB_df.set_index(time_index, inplace=True)
AB_df = AB_df.to_period('Q')

st.markdown('### 2.1. Time Series Decomposition')
st.markdown('''
Additive time series decomposition is a method used to break down a time series into its constituent components: trend, seasonality, and randomness. By separating these elements, additive decomposition allows for a deeper understanding of the underlying patterns and variations in the data. The trend component represents the long-term direction, the seasonality component captures recurring patterns, and the residual component accounts for the unexplained fluctuations. This decomposition technique is valuable as it enables evaluation of each component individually, gain insights into the data's behavior, and make more accurate predictions. It also aids in selecting appropriate modeling approaches that can account for specific characteristics of the time series.

Alberta's Download Speed data was decomposed in below chart.
''')

from pylab import rcParams
AB_dec_df = AB_df.copy()
AB_dec_df.index = pd.to_datetime(AB_df.index.to_timestamp(), format='%Y-%m-%d').to_period('Q').to_timestamp()
rcParams['figure.figsize'] = 15, 8
rcParams['axes.labelsize'] = 14
rcParams['ytick.labelsize'] = 14
rcParams['xtick.labelsize'] = 14
decomposition = sm.tsa.seasonal_decompose(AB_dec_df, model='additive')
decomp = decomposition.plot()
decomp.suptitle('Alberta Download Speed Decomposition', fontsize=18)
st.pyplot(decomp)
st.markdown('''
Above plot obviously shows and increasing trend and a seasonality for Alberta's Download Speed Data. Existence of a trend in the dataset is likely to result in non-stationarity of time series data which will be adressed in later parts. 
''')

st.markdown('### 2.2. Auto Correlation Checks')
st.markdown('''
**ACF (Autocorrelation Function)** and **PACF (Partial Autocorrelation Function)** are important tools in time series analysis, particularly for fitting **ARIMA (Autoregressive Integrated Moving Average)** models. They provide insights into the underlying autocorrelation structure of the time series data, which is essential for determining the appropriate order of the ARIMA model.

**ACF** measures the autocorrelation between a time series and its lagged (previous) values. It helps identify the presence of correlation in the time series at different lag levels. By examining the ACF plot, it is easy to identify the decay pattern of autocorrelation, which indicates the appropriate order of the Moving Average (MA) component in the ARIMA model. The significant spikes in the ACF plot at specific lags suggest the need for including MA terms in the model.

**PACF** measures the correlation between a time series and its lagged values while controlling for the influence of intervening lags. It provides information about the direct relationship between the observations at different lags, after accounting for the intermediate lags. Examining the PACF plot helps to identify the order of the Autoregressive (AR) component in the ARIMA model. The significant spikes in the PACF plot at specific lags suggest the need for including AR terms in the model.

In short, analyzing the ACF and PACF plots is essential to identify the presence of autocorrelation and determine the appropriate orders for the AR and MA components of the ARIMA model.''')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
plot_acf(AB_df['avg_d_kbps'],
         title='ACF of Alberta Download Speed',
         ax = ax1)
plot_pacf(AB_df['avg_d_kbps'],
          title='PACF of Alberta Download Speed',
          lags = 5,
          ax = ax2)
plt.tight_layout()
st.pyplot(fig)

st.markdown('''
ACF displayed a clear decay of autocorrelation for different lags and PACF showed an obvious cut-off after lag 1. These plots indicate a possible AR(1) model. However, we need to ensure stationarity of the dataset before fitting an AR(1) model.
''')

st.markdown('### 2.3. Stationarity Checks')
st.markdown('''
Stationarity is a fundamental concept in time series analysis refering to the statistical properties of a time series remaining constant over time. A stationary time series exhibits **consistent mean, variance, and autocovariance structures**, irrespective of when the observations are collected. 

This means that the statistical characteristics of the time series, such as the average value and variability, do not change with time. Stationary time series are easier to model and analyze as they allow for the application of various mathematical techniques, such as forecasting and identifying patterns or trends. Ensuring stationarity is often a prerequisite for employing time series models and accurately interpreting their results.

As shown in above parts, Alberta's Download Speed has a clear upward trend which provides clues about non-stationarity of the time series. However, it is better to check stationarity with a statistical test (**Augmented Dickey-Fuller Test**) and following hypotheses:
''')
st.write("$H_0$: Time Series Data is NOT stationary.")
st.write("$H_A$: Time Series Data is stationary.")

st.markdown('**ADF Test Results:**')
result = adfuller(AB_df['avg_d_kbps'])
st.markdown(f'* ADF Statistic: {result[0]:.2f} and the p-value: {result[1]}')
if result[1] < 0.05:
    st.markdown('* Need to Reject Null Hypothesis. Time Series Data is stationary')
else:
    st.markdown('* Failed to Reject Null Hypothesis. Time Series Data is NOT stationary')
    
st.markdown('The Augmented Dickey-Fuller (ADF) test statistic of 2.81 and a p-value of 1.0 suggest that the time series data does not provide sufficient evidence to reject the null hypothesis. Therefore, we fail to reject the hypothesis stating non-stationarity of the time series. These results indicate that the data exhibits a clear trend (as discussed above) over time.')

st.markdown('### 2.4. Differencing')
st.markdown('''
Differencing is a commonly used technique in time series analysis to address non-stationarity. When a time series exhibits trends, seasonality, or other forms of non-stationary behavior, differencing can help remove or reduce these effects, making the data more stationary. By taking the difference between consecutive observations, differencing eliminates the trend component and focuses on the changes or fluctuations in the data. This process helps stabilize the mean and variance of the time series, making it easier to model and analyze.

Using Alberta's Download Speed data first order differencing applied and stationarity test was repeated with differenced data using the same (mentioned) hypotheses. 
''')

diff_df = pd.DataFrame(AB_df['avg_d_kbps'].diff())
diff_df.dropna(inplace=True)

result = adfuller(diff_df['avg_d_kbps'])
st.markdown(f'* ADF Statistic: {result[0]:.2f} and the p-value: {result[1]}')
if result[1] < 0.05:
    st.markdown('* Need to Reject Null Hypothesis. Time Series Data is stationary')
else:
    st.markdown('* Failed to Reject Null Hypothesis. Time Series Data is NOT stationary')

st.markdown('''
The ADF test statistic of -3.16 and a p-value of 0.022 indicate that the differenced data is statistically significant and provides strong evidence to reject the null hypothesis of non-stationarity. Therefore, we can conclude that the differencing operation has effectively transformed the time series into a stationary process, making it suitable for further analysis and modeling.
''')

st.markdown('### 2.5. Auto Correlation Checks After Differencing')
st.markdown('''
Using the differenced data, ACF and PACF plots were regenerated to decide ARIMA model parameters (p and q, d is set to 1 with first order differencing).
''')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
plot_acf(diff_df['avg_d_kbps'],
         title='ACF of Alberta Download Speed',
         ax = ax1)
plot_pacf(diff_df['avg_d_kbps'],
          title='PACF of Alberta Download Speed',
          lags = 5,
          ax = ax2)
plt.tight_layout()
st.pyplot(fig)

st.markdown('''
Based on the absence of significant spikes in the autocorrelation function (ACF) and partial autocorrelation function (PACF) after differencing the dataset, it can be concluded that the differenced data does not exhibit any apparent linear relationship or correlation with its past values. This suggests that the differenced series may not possess any significant autoregressive (AR) or moving average (MA) components.

In cases, when the ACF and PACF plots do not show significant autocorrelation patterns, it indicates that an ARIMA (Autoregressive Integrated Moving Average) model is not appropriate for modeling the data. Instead, alternative approaches such as non-linear models, machine learning algorithms, or other techniques may be considered.
''')