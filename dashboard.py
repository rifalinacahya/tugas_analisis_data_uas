import streamlit as st
import pandas as pd

# Tentukan path (jalur) ke file CSV Anda
# Pastikan file ini ada di lokasi yang sama atau sesuaikan jalurnya
FILE_PATH = "dataset_ujian.csv"

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide")

st.title("📊 Dashboard Data Nilai Mahasiswa dari File CSV")
st.markdown("---")

# 1. Memuat Data dari File CSV
try:
    # Menggunakan Pandas untuk membaca file CSV
    df = pd.read_csv(FILE_PATH)

    st.success(f"Data berhasil dimuat dari **{FILE_PATH}**!")

    # Opsional: Konversi kolom 'Tanggal' ke tipe datetime
    # Asumsi format tanggal adalah Hari/Bulan/Tahun (contoh: 9/8/2023)
    try:
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y', errors='coerce')
    except KeyError:
        st.warning("Kolom 'Tanggal' tidak ditemukan atau formatnya berbeda. Melewati konversi tanggal.")
    
except FileNotFoundError:
    st.error(f"Error: File **{FILE_PATH}** tidak ditemukan. Pastikan nama dan jalurnya benar.")
    st.stop() # Hentikan eksekusi jika file tidak ditemukan
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca file: {e}")
    st.stop() # Hentikan eksekusi jika ada error lain


# 2. Menampilkan Data Lengkap (Tabel Interaktif)
st.subheader("Tabel Data Lengkap")
st.info(f"Total **{len(df)}** data mahasiswa ditampilkan.")

# Menampilkan DataFrame
st.dataframe(
    df,
    use_container_width=True, # Menggunakan lebar penuh kontainer
    hide_index=True          # Menyembunyikan indeks default Pandas
)

# 3. Filter Interaktif
st.markdown("---")
st.subheader("Filter dan Analisis Data")

col1, col2, col3 = st.columns(3)

# Filter Berdasarkan Gender
with col1:
    gender_list = ['Semua'] + df['Gender'].unique().tolist()
    selected_gender = st.selectbox("Pilih Gender", gender_list)

# Filter Berdasarkan Mata Kuliah
with col2:
    matkul_list = ['Semua'] + df['Matkul'].unique().tolist()
    selected_matkul = st.selectbox("Pilih Mata Kuliah", matkul_list)

# Filter Berdasarkan Nilai Minimum
with col3:
    min_nilai = st.slider("Nilai Minimum (Nilai Akhir)", float(df['Nilai'].min()), float(df['Nilai'].max()), float(df['Nilai'].min()))

# Menerapkan Filter
df_filtered = df.copy()

if selected_gender != 'Semua':
    df_filtered = df_filtered[df_filtered['Gender'] == selected_gender]

if selected_matkul != 'Semua':
    df_filtered = df_filtered[df_filtered['Matkul'] == selected_matkul]

df_filtered = df_filtered[df_filtered['Nilai'] >= min_nilai]


st.subheader(f"Tabel Data Hasil Filter ({len(df_filtered)} Baris)")

# Menampilkan Data yang sudah difilter
st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True
)

# 4. Ringkasan Statistik
st.markdown("---")
st.subheader("Ringkasan Statistik Nilai (Dari Data yang Difilter)")
# Menampilkan ringkasan statistik dari kolom numerik
st.dataframe(
    df_filtered[['Nilai', 'UTS', 'UAS', 'Umur']].describe().T.style.format(precision=2),
    use_container_width=True
)