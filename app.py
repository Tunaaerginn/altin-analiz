import streamlit as st
import yfinance as yf
import pandas as pd
import requests 

st.title("ALTIN PANEL") 

@st.cache_data(ttl=60)
def veri_al():
url = "https://www.izko.org.tr/guncel-kur"
h = {"User-Agent": "Mozilla/5.0"}
res = requests.get(url, headers=h, timeout=10)
tables = pd.read_html(res.text)
return tables 

try:
data = veri_al()
st.dataframe(data)
except Exception as e:
st.error(str(e)) 

ticker = yf.Ticker("GC=F")
df = ticker.history(period="1d")
if not df.empty:
st.metric("Ons Gold", f"{df['Close'].iloc[-1]:.2f}")
