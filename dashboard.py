import streamlit as st
import pandas as pd
import plotly.express as px

# DATASET PENJUALAN
data = {
    'Bulan':['Januari','Februari','Maret','April','Mei','Juni'],
    'Penjualan': [100, 120, 90, 150, 180, 200],
    'Keuntungan': [20, 25, 15, 35, 40, 45],
    'Wilayah': ['Antasari','Teluk','Sukarame','Barat','Pesawaran','Barat',]

}

df = pd.DataFrame(data)
# Reset index mulai dari 1
df.index = range(1, len(df) + 1)

# Judul Dashboard
st.title("Dashboard Kelas 5A")

# Dropdown pilihan
wilayah_options = ["Semua"] + sorted(df['Wilayah'].unique())
wilayah = st.selectbox("Pilih Wilayah:", wilayah_options)

# filter dataset
if wilayah == "Semua":
    filtered = df.copy()
else:
    filtered = df[df['Wilayah'] == wilayah].copy()

# Tabel DATA
st.subheader("Data Penjualan")
st.dataframe(
    filtered.style.format({
        "Penjualan": "{:,.0f}",
        "Keuntungan": "{:,.0f}"

    })
)

#membuat pie chart

#pie chart -proporsi penjualan per wilayah
st.subheader("Proporsi Penjualan Per Wilayah")
fig_pie = px.pie(
    df,
    names='Wilayah',
    values='Penjualan',
    title="Proporsi Penjualan Per Wilayah"
)
st.plotly_chart(fig_pie, use_container_width=True)

#line chart - tren keuntungan
st.subheader("Tren Keuntungan")
fig_line = px.line(
    filtered,
    x='Bulan', 
    y='Keuntungan',
    markers=True,
    title=f"Tren Keuntungan - {wilayah}"   
)
st.plotly_chart(fig_line, use_container_width=True)

#membuat bar chart

#bar chart - tren keunutngan
st.subheader("Penjualan Per Bulan")
fig_bar = px.bar(
    filtered,
    x='Bulan',
    y='Penjualan',
    text='Penjualan',
    title=f"Penjualan - {wilayah}"
)
st.plotly_chart(fig_bar, use_container_width=True)