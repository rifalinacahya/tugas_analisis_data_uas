import streamlit as st
import pandas as pd
import altair as alt

# Tentukan path (jalur) ke file CSV Anda
FILE_PATH = "dataset_ujian.csv"

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide")

st.title("📊 Dashboard Data Nilai Mahasiswa dari File CSV")
st.markdown("---")

# ==============================================================================
# 1. MEMUAT DATA
# ==============================================================================
@st.cache_data
def load_data(path):
    """Memuat data dari CSV dan melakukan konversi tipe data."""
    try:
        df = pd.read_csv(path)
        
        # Konversi kolom 'Tanggal'
        try:
            # Asumsi format tanggal adalah Hari/Bulan/Tahun (contoh: 9/8/2023)
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y', errors='coerce')
        except KeyError:
            st.warning("Kolom 'Tanggal' tidak ditemukan atau formatnya berbeda. Melewati konversi tanggal.")
            
        return df
        
    except FileNotFoundError:
        st.error(f"Error: File **{path}** tidak ditemukan. Pastikan nama dan jalurnya benar.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
        st.stop()

df = load_data(FILE_PATH)
st.success(f"Data berhasil dimuat dari **{FILE_PATH}**!")


# ==============================================================================
# 2. PROSES DATA CLEANING
# ==============================================================================
st.header("1. Proses Data Cleaning dan Preprocessing 🧹")

# Inisialisasi DataFrame untuk cleaning
df_cleaned = df.copy()

# --- 2.1 Pengecekan Data Null Awal ---
st.subheader("1.1 Pengecekan Data Null Awal")
total_rows_before = len(df_cleaned)
null_counts = df_cleaned.isnull().sum()
st.info(f"Total baris awal: **{total_rows_before}**")
st.dataframe(null_counts.rename('Jumlah Nilai Null'))

# Hapus baris di mana SEMUA kolom bernilai NULL/NaN
st.markdown("##### Menghapus baris yang kosong seluruhnya (dropna(how='all'))")
df_cleaned.dropna(how='all', inplace=True)
total_rows_after_null = len(df_cleaned)
st.success(f"Cleaning Null Selesai! Baris terhapus: **{total_rows_before - total_rows_after_null}**.")
st.write(f"Total baris setelah cleaning Null: **{total_rows_after_null}**")


# --- 2.2 Pengecekan Duplikasi ---
st.subheader("1.2 Pengecekan dan Penghapusan Data Duplikasi 🔍")

duplicate_rows = df_cleaned.duplicated().sum()
st.info(f"Total baris yang terdeteksi duplikat: **{duplicate_rows}**")

if duplicate_rows > 0:
    st.warning("Baris Duplikat Ditemukan! Menampilkan baris yang duplikat:")
    # Tampilkan baris duplikat (keep=False menampilkan semua, termasuk yang pertama)
    st.dataframe(df_cleaned[df_cleaned.duplicated(keep=False)])
    
    # Menghapus baris duplikat
    df_cleaned.drop_duplicates(inplace=True)
    st.success(f"**{duplicate_rows}** baris duplikat telah dihapus. Sisa baris: **{len(df_cleaned)}**.")
else:
    st.success("Tidak ada baris duplikat yang ditemukan dalam dataset.")

# Gunakan DataFrame yang sudah bersih untuk analisis selanjutnya
df = df_cleaned
st.info(f"Total data akhir yang akan digunakan untuk analisis: **{len(df)}** baris.")
st.markdown("---")

# ==============================================================================
# 3. FILTER INTERAKTIF
# ==============================================================================
st.header("2. Filter Data dan Ringkasan Statistik ⚙️")

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
    # Menggunakan nilai min/max dari data ASLI untuk range slider
    min_val_range = float(df['Nilai'].min())
    max_val_range = float(df['Nilai'].max())
    min_nilai = st.slider("Nilai Minimum (Nilai Akhir)", min_val_range, max_val_range, min_val_range)

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

st.subheader("Ringkasan Statistik Nilai (Dari Data yang Difilter)")
# Menampilkan ringkasan statistik dari kolom numerik
st.dataframe(
    df_filtered[['Nilai', 'UTS', 'UAS', 'Umur']].describe().T.style.format(precision=2),
    use_container_width=True
)

st.subheader("Modus Data yang Dipilih (Nilai Paling Sering Muncul) 🎯")

# Kolom yang ingin dicari modusnya
mode_cols = ['Nilai', 'UTS', 'UAS', 'Gender', 'Matkul']

if not df_filtered.empty:
    mode_results = {}
    
    # Hitung modus untuk setiap kolom
    for col in mode_cols:
        mode_values = df_filtered[col].mode().tolist()
        
        # Format output
        if len(mode_values) == 1:
            result = str(mode_values[0])
        elif len(mode_values) > 1:
            result = f"{', '.join(map(str, mode_values))} (Multimodal)"
        else:
            result = "Tidak ditemukan"
            
        mode_results[col] = result

    # Konversi ke DataFrame untuk tampilan yang rapi
    df_mode = pd.DataFrame(mode_results.items(), columns=['Kolom', 'Modus/Nilai Terbanyak'])
    df_mode = df_mode.set_index('Kolom')
    
    st.table(df_mode)
    st.caption("Catatan: Jika terdapat lebih dari satu modus (Multimodal), semua nilai akan ditampilkan.")
    
else:
    st.warning("Tidak ada data setelah difilter, Modus tidak dapat dihitung.")

st.markdown("---")

# ==============================================================================
# 4. KORELASI ANTAR VARIABEL (BARU)
# ==============================================================================

st.header("3. Korelasi Antar Variabel Numerik 🔗")
st.info("Korelasi menunjukkan hubungan linier antara dua variabel. Nilai mendekati +1.0 berarti korelasi positif kuat, -1.0 berarti korelasi negatif kuat, dan 0.0 berarti tidak ada korelasi.")

numeric_cols = ['Nilai', 'UTS', 'UAS', 'Umur']

if not df_filtered.empty and len(df_filtered) > 1:
    
    # 4.1 Hitung Matriks Korelasi
    correlation_matrix = df_filtered[numeric_cols].corr().reset_index()
    correlation_matrix = correlation_matrix.rename(columns={'index': 'Variable1'})

    # Melt DataFrame untuk format yang kompatibel dengan Altair (Variable1, Variable2, Correlation)
    corr_long = pd.melt(correlation_matrix, 
                        id_vars='Variable1', 
                        value_vars=numeric_cols,
                        var_name='Variable2', 
                        value_name='Korelasi')

    # 4.2 Tampilkan Tabel Korelasi
    st.subheader("Tabel Matriks Korelasi Pearson")
    st.dataframe(
        correlation_matrix.set_index('Variable1').style.format(precision=3),
        use_container_width=True
    )
    
    # 4.3 Visualisasi Heatmap
    st.subheader("Visualisasi Heatmap Korelasi")
    
    # Buat Heatmap Altair
    heatmap = alt.Chart(corr_long).mark_rect().encode(
        x=alt.X('Variable1:N', title='Variabel 1'),
        y=alt.Y('Variable2:N', title='Variabel 2'),
        color=alt.Color('Korelasi:Q', 
                        scale=alt.Scale(domain=[-1, 0, 1], range='diverging', scheme='redblue'),
                        title='Koefisien Korelasi'),
        tooltip=['Variable1', 'Variable2', alt.Tooltip('Korelasi', format='.3f')]
    ).properties(
        title='Heatmap Korelasi Antar Variabel Numerik'
    ).interactive()

    # Tambahkan teks nilai korelasi ke setiap kotak
    text = heatmap.mark_text().encode(
        text=alt.Text('Korelasi', format='.2f'),
        color=alt.value('black') # Warna teks agar kontras
    )

    # Gabungkan Heatmap dan Teks
    st.altair_chart(heatmap + text, use_container_width=True)
    
else:
    st.warning("Tidak ada cukup data setelah difilter (minimal 2 baris) untuk menghitung korelasi antar variabel numerik.")


st.markdown("---")

# ==============================================================================
# 5. DISTRIBUSI DATA NILAI (HISTOGRAM)
# ==============================================================================
st.header("4. Visualisasi Distribusi Nilai (Data Filtered) 📈")

st.info("Visualisasi ini menunjukkan sebaran frekuensi Nilai Akhir, UTS, dan UAS dari data yang telah Anda filter.")

# Daftar kolom nilai yang akan divisualisasikan
nilai_cols = ['Nilai', 'UTS', 'UAS']
color_scheme = ['#4c78a8', '#f58518', '#e4575c'] # Skema warna untuk setiap kolom

# Membuat 3 kolom untuk 3 histogram
chart_cols = st.columns(3)

for i, col in enumerate(nilai_cols):
    with chart_cols[i]:
        st.subheader(f"Distribusi {col}")
        
        # Membuat Histogram menggunakan Altair
        if not df_filtered.empty:
            chart = alt.Chart(df_filtered).mark_bar().encode(
                # Bins untuk membuat histogram
                x=alt.X(f'{col}', bin=True, title=f'{col} (Rentang Nilai)'),
                # y sebagai count/frekuensi
                y=alt.Y('count()', title='Frekuensi'),
                tooltip=[
                    alt.Tooltip(f'{col}', bin=True, title=f'Rentang {col}'),
                    alt.Tooltip('count()', title='Jumlah Mahasiswa')
                ],
                color=alt.value(color_scheme[i]) # Atur warna
            ).properties(
                title=f'Histogram Nilai {col}'
            ).interactive() # Tambahkan interaktivitas (zoom/pan)
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning(f"Tidak ada data untuk menampilkan Distribusi {col}!")