# Import required libraries
from random import sample
from statistics import mean
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(
     page_title="S&P 500 Company",
     page_icon=":dollar",
     layout="wide",
     initial_sidebar_state="expanded"
 )

st.title('S&P 500 Company')

# Read S&P 500 Companies 
@st.cache
def getsp500():
    return pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0] 

sp_500 = getsp500()
comp_list = sp_500['Symbol'].unique()
comp_list.sort()

st.sidebar.header('User Input')
comp_ticker = st.sidebar.selectbox('Symbol of a Company', comp_list)
time_length = st.sidebar.selectbox('Timeframe', ['2 days', '1 month', '6 months', '1 year', '5 years'], index=3)
time_dict = {'2 days': '2d', '1 month': '1mo', '6 months': '6mo', '1 year': '1y', '5 years': '5y'}

def companyinfo(symbol, df=sp_500):
    df = df.copy()
    df = df[df['Symbol']==symbol] 
    df.rename(columns={'Security': 'Company', 'GICS Sector': 'Sector', 'Headquarters Location': 'Headquarter'}, 
              inplace=True)
    df = df[['Company', 'Sector', 'Headquarter', 'Founded']].reset_index(drop=True)
    df = df.T
    df.columns = [symbol]
    return df

company = companyinfo(comp_ticker)

st.header('Information for ' + comp_ticker)
st.write(company)

yf_data = yf.Ticker(comp_ticker).history(period=time_dict[time_length])

st.subheader(time_length + ' Summary')
range_df = pd.DataFrame({'High': max(yf_data['High']), 
                         'Low': min(yf_data['Low']), 
                         'Max Volume': max(yf_data['Volume']), 
                         'Min Volume': min(yf_data['Volume']),
                         'Max Dividends': max(yf_data['Dividends']), 
                         'Stock Splits Occured': 'Yes' if max(yf_data['Stock Splits'])>0 else 'No'
                        }, index=[time_length + ' Range'])
st.write(range_df)

st.download_button(label='Download Raw Data as CSV', 
                    data=yf_data.to_csv(), 
                    file_name=comp_ticker + ' ' + time_length + '.csv', 
                    help='Download last ' + time_length + ' data')

st.subheader(time_length + ' Trend')
fig = px.area(yf_data, x=yf_data.index, y='Close')
fig.update_layout(plot_bgcolor='white', xaxis={'showgrid': False}, 
                yaxis={'showgrid': False}, 
                yaxis_range=[min(yf_data['High'])*0.5, max(yf_data['High'])*1.25], 
                title_text='Stock Closing Value by Day', title_x=0.5, 
                title_font_color="gray",
                title_font_size=24)
st.plotly_chart(fig, use_container_width=True)
