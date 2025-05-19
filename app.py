
import streamlit as st
from faiz_tablosu import df

st.set_page_config(page_title="Türkiye Bankaları Güncel Faiz Takibi", layout="wide")
st.title("📊 Güncel Mevduat Faiz Oranları")

kategori = st.selectbox("Kategori seçin", ["Hepsi", "32-91 günlük max oran", "92 günlük max oran", "günlük faiz"])
df = get_faiz_tablosu()

if kategori != "Hepsi":
    df = df[["Banka", kategori]].sort_values(by=kategori, ascending=False)

st.dataframe(df, use_container_width=True)
