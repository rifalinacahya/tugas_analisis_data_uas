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
st.header("1. Proses Data Cleaning dan Preprocessing")

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
    
    # --- Penambahan Pie Chart untuk Modus ---
    st.markdown("##### Visualisasi Frekuensi Modus (Nilai Terbanyak) ")
    
    pie_col1, pie_col2, pie_col3 = st.columns(3)
    
    # 1. Pie Chart untuk Gender (Modus Gender)
    with pie_col1:
        st.caption("Distribusi Gender")
        gender_counts = df_filtered['Gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        
        pie_gender = alt.Chart(gender_counts).mark_arc(outerRadius=120).encode(
            theta=alt.Theta("Count", stack=True),
            color=alt.Color("Gender"),
            tooltip=['Gender', 'Count']
        ).properties(title="Distribusi Gender")
        
        st.altair_chart(pie_gender, use_container_width=True)
        
    # 2. Pie Chart untuk Matkul (Modus Mata Kuliah)
    with pie_col2:
        st.caption("Distribusi Mata Kuliah")
        matkul_counts = df_filtered['Matkul'].value_counts().reset_index()
        matkul_counts.columns = ['Matkul', 'Count']
        
        pie_matkul = alt.Chart(matkul_counts).mark_arc(outerRadius=120).encode(
            theta=alt.Theta("Count", stack=True),
            color=alt.Color("Matkul"),
            tooltip=['Matkul', 'Count']
        ).properties(title="Distribusi Matkul")
        
        st.altair_chart(pie_matkul, use_container_width=True)

    # 3. Pie Chart untuk Nilai (Modus Nilai Akhir) - Hanya jika tunggal
    with pie_col3:
        st.caption("Frekuensi Nilai Modus (Nilai Akhir)")
        modus_nilai = df_filtered['Nilai'].mode()
        
        if len(modus_nilai) == 1:
            mode_val = modus_nilai.iloc[0]
            mode_count = (df_filtered['Nilai'] == mode_val).sum()
            other_count = len(df_filtered) - mode_count
            
            pie_data = pd.DataFrame({
                'Category': [f'Modus ({mode_val})', 'Lainnya'],
                'Count': [mode_count, other_count]
            })
            
            pie_nilai = alt.Chart(pie_data).mark_arc(outerRadius=120).encode(
                theta=alt.Theta("Count", stack=True),
                color=alt.Color("Category", scale=alt.Scale(domain=[f'Modus ({mode_val})', 'Lainnya'], range=['#1f77b4', '#aec7e8'])),
                tooltip=['Category', 'Count']
            ).properties(title="Frekuensi Modus Nilai Akhir")
            
            st.altair_chart(pie_nilai, use_container_width=True)
        else:
            st.info("Modus Nilai Akhir tidak tunggal (Multimodal) atau tidak ditemukan. Pie Chart dilewati.")
    
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
# 5. DISTRIBUSI DATA NILAI (HISTOGRAM & LINE CHART)
# ==============================================================================
st.header("4. Visualisasi Distribusi Nilai (Data Filtered) 📈")

st.info("Visualisasi ini menunjukkan sebaran frekuensi Nilai Akhir, UTS, dan UAS dari data yang telah Anda filter.")

# Daftar kolom nilai yang akan divisualisasikan
nilai_cols = ['Nilai', 'UTS', 'UAS']
# Tentukan warna untuk setiap kolom
color_scheme = {
    'Nilai': '#4c78a8', # Biru
    'UTS': '#f58518',  # Oranye
    'UAS': '#e4575c'   # Merah
}

# Membuat 3 kolom untuk Histrogram dan 3 kolom untuk Line Chart
st.subheader("Visualisasi Histogram (Bar Chart)")
hist_cols = st.columns(3)

for i, col in enumerate(nilai_cols):
    with hist_cols[i]:
        st.caption(f"Histogram {col}")
        
        if not df_filtered.empty:
            # Membuat Histogram menggunakan Altair
            chart = alt.Chart(df_filtered).mark_bar().encode(
                # Bins untuk membuat histogram
                x=alt.X(f'{col}', bin=alt.Bin(maxbins=15), title=f'{col} (Rentang Nilai)'),
                # y sebagai count/frekuensi
                y=alt.Y('count()', title='Frekuensi'),
                tooltip=[
                    alt.Tooltip(f'{col}', bin=True, title=f'Rentang {col}'),
                    alt.Tooltip('count()', title='Jumlah Mahasiswa')
                ],
                color=alt.value(color_scheme[col]) # Atur warna
            ).properties(
                title=f'Histogram Nilai {col}'
            ).interactive() 
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning(f"Tidak ada data untuk menampilkan Distribusi {col}!")

st.markdown("---")
st.subheader("Visualisasi Line Chart (Frequency Polygon)")
line_cols = st.columns(3)

for i, col in enumerate(nilai_cols):
    with line_cols[i]:
        st.caption(f"Line Chart (Frequency Polygon) {col}")
        
        if not df_filtered.empty:
            # Membuat Line Chart (Frequency Polygon) menggunakan Altair
            # Menggunakan transform_bin untuk mendapatkan nilai tengah bin
            
            chart_base = alt.Chart(df_filtered).transform_bin(
                # Bins sama dengan histogram, simpan di kolom '_bin_start' dan '_bin_end'
                # Kolom baru 'bin_start' akan berisi batas bawah bin
                'bin_start', field=col, bin=alt.Bin(maxbins=15)
            ).transform_aggregate(
                # Hitung frekuensi untuk setiap bin
                count='count()',
                # Hitung nilai tengah bin
                center_point='mean(bin_start)', # Menggunakan batas bawah bin sebagai proxy untuk center
                groupby=['bin_start']
            ).encode(
                x=alt.X('bin_start:Q', title=f'Nilai Tengah Bin {col}'),
                y=alt.Y('count:Q', title='Frekuensi'),
                tooltip=[
                    alt.Tooltip('bin_start:Q', title=f'Nilai Awal Bin'),
                    alt.Tooltip('count:Q', title='Jumlah Mahasiswa')
                ]
            )

            # Mark Line
            line = chart_base.mark_line(point=True, color=color_scheme[col]).properties(
                title=f'Line Chart (Frequency Polygon) Nilai {col}'
            ).interactive() 

            st.altair_chart(line, use_container_width=True)
        else:
            st.warning(f"Tidak ada data untuk menampilkan Line Chart Distribusi {col}!")