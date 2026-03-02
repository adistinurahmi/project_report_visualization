import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Literasi Indonesia", layout="wide")

# --- 1. SETTING WARNA GLOBAL (TARUH DI SINI) ---
MAIN_CYAN = "#00fbff"
ACCENT_GOLD = "#ffaa00"
BG_DARK = "#0e1117"
SYNC_COLORS = [MAIN_CYAN, "#00ced1", ACCENT_GOLD, "#ffd700", "#4f4f4f"]

# --- 2. KONFIGURASI CSS (AGAR WARNA TULISAN SINKRON) ---
st.markdown(f"""
    <style>
    .main {{
        background-color: {BG_DARK};
        color: white;
    }}
    h1 {{ color: {MAIN_CYAN} !important; }}
    h2, h3, h4 {{ color: {ACCENT_GOLD} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOAD DAN BERSIHKAN DATA ---
def load_and_clean_data():
    # Load data dengan pemisah ';' dan desimal ','
    df = pd.read_csv('TGM 2020-2023_eng.csv', delimiter=';', decimal=',')
    df.columns = df.columns.str.strip()
    
    # Mapping Nama Bahasa Inggris ke Bahasa Indonesia (Sesuai GeoJSON)
    mapping_geojson = {
    'Aceh': 'DI. ACEH',
    'Jakarta': 'DKI JAKARTA',
    'Yogyakarta': 'DAERAH ISTIMEWA YOGYAKARTA',
    'Banten': 'PROBANTEN',
    'Bangka Belitung Islands': 'BANGKA BELITUNG',
    'West Nusa Tenggara': 'NUSATENGGARA BARAT',
    'West Papua': 'IRIAN JAYA BARAT',
    'Papua': 'IRIAN JAYA TIMUR',
    'North Sumatra': 'SUMATERA UTARA',
    'West Sumatra': 'SUMATERA BARAT',
    'South Sumatra': 'SUMATERA SELATAN',
    'Central Java': 'JAWA TENGAH',
    'East Java': 'JAWA TIMUR',
    'West Java': 'JAWA BARAT',
    'East Nusa Tenggara': 'NUSA TENGGARA TIMUR',
    'West Kalimantan': 'KALIMANTAN BARAT',
    'Central Kalimantan': 'KALIMANTAN TENGAH',
    'South Kalimantan': 'KALIMANTAN SELATAN',
    'East Kalimantan': 'KALIMANTAN TIMUR',
    'North Sulawesi': 'SULAWESI UTARA',
    'Central Sulawesi': 'SULAWESI TENGAH',
    'South Sulawesi': 'SULAWESI SELATAN',
    'South East Sulawesi': 'SULAWESI TENGGARA',
    'Riau Islands': 'KEPULAUAN RIAU'
    # Tambahkan provinsi lain jika masih ada yang berwarna hitam
    }
    df['Provinsi'] = df['Provinsi'].replace(mapping_geojson)
    
    # Hapus baris 'Indonesia' karena itu total nasional, bukan provinsi
    df = df[df['Provinsi'] != 'Indonesia']
    
    # Pastikan skor TKM adalah angka
    tkm_col = 'Tingkat Kegemaran Membaca (Reading Interest)'
    df[tkm_col] = pd.to_numeric(df[tkm_col], errors='coerce')
    
    return df

df = load_and_clean_data()

# --- TAMPILAN DASHBOARD ---
st.markdown("<h1 style='text-align: center; color: #ffaa00;'>📊 インドネシアにおける読解力調査分析</h1>", unsafe_allow_html=True)

# --- TAMPILAN tujuan ---
st.markdown("""
    <div style="background-color: #1e2130; padding: 20px; border-radius: 10px; border-left: 5px solid #ffaa00;">
        <h3 style="color: #ffaa00; margin-top: 0;">📌 分析の背景と目的</h3>
        <p style="text-align: justify; color: #e0e0e0; font-size: 16px;">
            インドネシアは国際的に「読書嫌いの国」として知られることが少なくありません。
            本分析の目的は、その定説が現在も妥当であるのか、あるいは<b>データに基づいた変化</b>が起きているのかを明らかにすることです。
            2020年から2023年にかけての各州の読書意欲指数（TKM）の推移を可視化し、読書習慣の変遷を検証します。
        </p>
    </div>
    """, unsafe_allow_html=True)    
st.write("#")

# --- Sidebar Filter Tahun dan Daftar Isi ----
st.sidebar.header("📊 フィルター設定")
selected_year = st.sidebar.selectbox("選択", df['Year'].unique())
df_filtered = df[df['Year'] == selected_year]
st.sidebar.title("📑 目次")
st.sidebar.markdown("""
- [1.全国概況](#overview)
- [2.カテゴリー構成比](#category-composition)
- [3.時系列推移](#trend-analysis)
- [4.読書時間の分布](#duration-distribution)
- [5.階層構造分析](#hierarchical-analysis)
- [6.インターネット相関分析](#correlation-analysis)
""")

# --- Metrik Utama ---
col1, col2, col3, col4= st.columns(4)
avg_tkm = df_filtered['Tingkat Kegemaran Membaca (Reading Interest)'].mean()
avg_duration = df_filtered['Daily Reading Duration (in minutes)'].mean()
col1.metric("全国平均読書好感度", f"{avg_tkm:.2f}")
col2.metric("分析対象年度", selected_year)
col3.metric("対象都道府県数", len(df_filtered))
col4.metric("平均読書時間", f"{avg_duration:.2f} 分")

# --- PETA (Tahap 1) ----
st.markdown('<a name="overview"></a>', unsafe_allow_html=True)
st.subheader(f"🗺️ 読書好感度マップ ({selected_year})")
geojson_url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province.json"
# geojson_data = requests.get(geojson_url).json()

# --- PENGATURAN PETA INDONESIA SAJA (BERSIH & KONTRAS) ---
fig_map = px.choropleth(
    df_filtered,
    geojson=geojson_url,
    locations='Provinsi',
    featureidkey="properties.Propinsi",
    color='Tingkat Kegemaran Membaca (Reading Interest)',
    # Skala warna dari Hijau Tua ke Kuning Terang (sangat kontras)
    color_continuous_scale=[
        [0.0, "#004d4d"],   # Warna gelap untuk nilai rendah
        [0.5, "#00fbff"],   # Warna Cyan untuk nilai tengah
        [1.0, "#ffff00"]    # Warna Kuning Terang untuk nilai tinggi
    ]
)

# --- MENGHAPUS SEMUA ELEMEN GANGGUAN ---
fig_map.update_geos(
    visible=False,          # Menghapus peta dunia di latar belakang
    fitbounds="locations",  # Zoom otomatis hanya ke wilayah Indonesia
    showcountries=False,    # Menghapus garis negara lain
    showocean=False,        # Menghapus warna laut (supaya ikut warna dashboard)
    showlakes=False,        # Menghapus gambar danau
)

fig_map.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', # Membuat background transparan total
    margin={"r":0,"t":0,"l":0,"b":0},
    height=500,
    coloraxis_showscale=True      # Tetap menampilkan batang warna di samping
)

# Memberikan garis putih tipis antar provinsi agar jelas batasnya
fig_map.update_traces(
    marker_line_color="white",
    marker_line_width=0.5
)

st.plotly_chart(fig_map, use_container_width=True)
st.markdown("""
    <div style="padding: 10px; border-radius: 5px; border: 1px solid #ffaa00;">
        <p style="margin: 0; color: #555555; font-size: 14px;">
            <b>🎨 色の読み方：</b><br>
            黄色のエリアほど<b>「読書への関心が高い」</b>ことを示し、
            濃い緑色のエリアは<b>「これからの伸びしろがある（関心が低め）」</b>ことを示しています。
        </p>
    </div>
    """, unsafe_allow_html=True)


# --- TAHAP 2: PIE CHART KATEGORI ---
st.markdown('<a name="category-composition"></a>', unsafe_allow_html=True)
st.divider() # Garis pembatas agar rapi
st.subheader(f"📊 全国リテラシーカテゴリ構成 ({selected_year})")

# 1. Bersihkan data kategori (menghapus spasi yang tidak terlihat)
df_filtered['Category'] = df_filtered['Category'].str.strip()

# 2. Hitung jumlah provinsi per kategori
category_counts = df_filtered['Category'].value_counts().reset_index()
category_counts.columns = ['Kategori', 'Jumlah Provinsi']

# 3. Buat Pie Chart
fig_pie = px.pie(
    category_counts, 
    values='Jumlah Provinsi', 
    names='Kategori',
    hole=0.4, # Membuatnya menjadi Donut Chart agar lebih modern
    color_discrete_sequence=SYNC_COLORS, # Warna hijau ke biru yang elegan
    template="plotly_dark"
)

# 4. Atur posisi teks agar mudah dibaca
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(
    margin=dict(t=0, b=0, l=0, r=0),
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=True
)

# Tampilkan di Streamlit
st.plotly_chart(fig_pie, use_container_width=True)

# Tambahkan penjelasan singkat (Insight)
st.info(f"{selected_year}年度において、大半の都道府県は「{category_counts.iloc[0]['Kategori']}」カテゴリに属しています。")

st.markdown('<a name="trend-analysis"></a>', unsafe_allow_html=True)
st.divider()
st.subheader("📈 全国リテラシー推移の傾向 (2020年-2023年)")

# 1. Agregasi data rata-rata nasional per tahun
df_trend = df.groupby('Year').agg({
    'Number of Readings per Quarter': 'mean',
    'Tingkat Kegemaran Membaca (Reading Interest)': 'mean'
}).reset_index()

# 2. Membuat grafik Combo
fig_trend = go.Figure()

# Bar Chart: Jumlah Bacaan
fig_trend.add_trace(go.Bar(
    x=df_trend['Year'], 
    y=df_trend['Number of Readings per Quarter'],
    name="平均読書数",
    marker_color='#00fbff',
    opacity=0.7
))

# Line Chart: Skor TKM (Sumbu Y Kedua)
fig_trend.add_trace(go.Scatter(
    x=df_trend['Year'], 
    y=df_trend['Tingkat Kegemaran Membaca (Reading Interest)'],
    name="平均読書好感度",
    yaxis="y2",
    line=dict(color='orange', width=4),
    mode='lines+markers'
))

# 3. Layout Sumbu Y Ganda
fig_trend.update_layout(
    template="plotly_dark",
    yaxis=dict(title="読書冊数"),
    yaxis2=dict(title="TKMスコア", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig_trend, use_container_width=True)
st.markdown('<a name="duration-distribution"></a>', unsafe_allow_html=True)
st.subheader("⏳1日あたりの平均読書時間の推移 ")

# Membuat Violin Plot untuk melihat distribusi
fig_joy = px.violin(
    df, 
    y="Daily Reading Duration (in minutes)", 
    x="Year", 
    color="Year", 
    box=True, 
    points="all",
    template="plotly_dark",
    title="年別読書時間（分）の分布"
)

fig_joy.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False
)

st.plotly_chart(fig_joy, use_container_width=True)

st.info("💡【分析のポイント】グラフの幅が広い部分（ボリュームゾーン）が年々上昇している場合、大半の国民の読書時間が長くなっていることを示しています。 ")
st.markdown('<a name="hierarchical-analysis"></a>', unsafe_allow_html=True)
st.divider()
st.subheader(f"🌳 リテラシー階層図：カテゴリと都道府県 ({selected_year})")

# 1. Membuat Treemap
fig_tree = px.treemap(
    df_filtered, 
    path=[px.Constant("Indonesia"), 'Category', 'Provinsi'], # Hierarki: Nasional -> Kategori -> Provinsi
    values='Tingkat Kegemaran Membaca (Reading Interest)', # Ukuran kotak berdasarkan skor TKM
    color='Tingkat Kegemaran Membaca (Reading Interest)', # Warna berdasarkan skor TKM
    color_continuous_scale='RdYlGn', # Merah (Rendah) ke Hijau (Tinggi)
    template="plotly_dark",
    hover_data=['Daily Reading Duration (in minutes)'] # Munculkan info durasi baca saat di-hover
)

# 2. Atur tampilan agar teks terlihat jelas
fig_tree.update_layout(
    margin=dict(t=30, b=10, l=10, r=10),
    paper_bgcolor='rgba(0,0,0,0)',
    coloraxis_colorbar=dict(title="Skor TKM")
)

st.plotly_chart(fig_tree, use_container_width=True)

# 3. Insight singkat
st.info(f"【**図の見方**】緑色の大きなボックスは、最もパフォーマンスが高い都道府県を示しています。カテゴリのボックスをクリックすると、該当する都道府県の詳細を確認できます。")
st.markdown('<a name="correlation-analysis"></a>', unsafe_allow_html=True)
st.divider()
st.subheader("🔍 相関分析：インターネット利用率 vs 読書時間")

# 1. Membersihkan data dari nilai N/A agar grafik tidak error
# Karena pada tahun 2020 data internet banyak yang 'N/A'
df_corr = df_filtered.dropna(subset=['Daily Internet Duration (in minutes)', 'Daily Reading Duration (in minutes)'])

# 2. Membuat Scatter Plot dengan Marginal Histogram
fig_corr = px.scatter(
    df_corr, 
    x="Daily Internet Duration (in minutes)", 
    y="Daily Reading Duration (in minutes)",
    color="Category", # Membedakan warna berdasarkan kategori literasi
    size="Tingkat Kegemaran Membaca (Reading Interest)", # Besar titik berdasarkan skor TKM
    hover_name="Provinsi",
    marginal_x="histogram", # Menampilkan distribusi internet di atas
    marginal_y="histogram", # Menampilkan distribusi baca di samping
    trendline="ols",        # Menambahkan garis tren (Linear Regression)
    template="plotly_dark",
    color_discrete_sequence=px.colors.qualitative.Safe
)

# 3. Estetika Grafik
fig_corr.update_layout(
    height=600,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_corr, use_container_width=True)

# 4. Insight Otomatis
st.info("""
**💡【相関分析の読み方】 :**
* 右肩上がりの近似線:インターネットの普及が読書時間の増加を後押ししている（デジタルリテラシーの向上）ことを示唆します。
* 右肩下がりの近似線:インターネット利用時間の増加が読書時間の減少につながっている傾向を示します。
* 点が分散している場合:両者の間に強い相関関係は見られません。
""")
st.write("#")
st.subheader("🔍 相関分析：インターネット利用時間 vs 読書時間")

# （ここに以前作成した Scatter Plot のコードが入ります）

# グラフのすぐ下に以下の解説を追加します
st.markdown("""
    <div style="background-color: #262730; padding: 15px; border-radius: 5px; border-left: 5px solid #ffaa00;">
        <h4 style="color: #ffaa00; margin-top: 0;">💡 データから読み解く「インターネットの質」</h4>
        <p style="text-align: justify; color: #e0e0e0;">
            このデータには、情報収集（学習）とSNS閲覧（娯楽）の両方が含まれています。グラフから以下の可能性を考察できます：
        </p>
        <ul style="color: #e0e0e0;">
            <li><b>正の相関（右上がり）の場合：</b> インターネットが「電子書籍」や「ニュース」などの読書を支えるツールとして活用されている可能性があります（デジタルリテラシー）。</li>
            <li><b>負の相関（右下がり）の場合：</b> インターネット（SNSや動画）が読書時間を奪う「娯楽（ディストラクション）」になっている可能性が高いと考えられます。</li>
        </ul>
        <p style="color: #e0e0e0;">
            インドネシア全体では、インターネット利用が増えても読書時間が維持されている州が多いのか、それとも減少しているのか。このグラフの<b>「傾き」</b>がその答えを示しています。
        </p>
    </div>
    """, unsafe_allow_html=True)



