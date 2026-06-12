import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import os

# =========================================================
# CSS (Tema Agrikultur & Modern UI)
# =========================================================
CUSTOM_CSS = """
<style>
/* Styling Header Aplikasi */
.app-header {
    background: linear-gradient(135deg, #2E8B57, #8FBC8F);
    padding: 25px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
.app-header h1 {
    margin: 0;
    font-size: 2.5em;
    font-weight: 800;
    letter-spacing: 1px;
}
.app-header p {
    margin: 8px 0 0 0;
    font-size: 1.1em;
    font-style: italic;
    opacity: 0.95;
}

/* Styling Grid untuk Grafik */
.responsive-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
}
.grid-item {
    flex: 1 1 calc(50% - 20px);
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    border: 1px solid #f0f0f0;
    transition: transform 0.2s ease-in-out;
}
.grid-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 15px rgba(46, 139, 87, 0.15);
}

/* Styling Kartu Penyakit */
.disease-card {
    background-color: #f8faf8;
    border: 1px solid #e2e8e0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.disease-title {
    color: #2E8B57;
    font-size: 1.3em;
    font-weight: bold;
    margin-bottom: 10px;
    border-bottom: 2px solid #8FBC8F;
    padding-bottom: 5px;
    display: inline-block;
}

@media (max-width: 900px) {
    .grid-item {
        flex: 1 1 100%;
    }
}
</style>
"""

# =========================================================
# TEXT (Storytelling & Kreatif)
# =========================================================
ABSTRACT_TEXT = """
<div style='text-align: justify; font-size: 16px; line-height: 1.7;'>
<p>🌾 <b>Tantangan di Sawah:</b> Produksi padi sering kali dihantui oleh penyakit daun seperti hawar daun (<i>blast</i>), bercak cokelat (<i>brown spot</i>), dan serangan hama <i>Hispa</i>. Memeriksa kerusakan daun satu per satu secara manual tentu sangat melelahkan, lambat, dan butuh ketelitian ahli. Di sinilah teknologi kecerdasan buatan (AI) hadir untuk mempermudah proses identifikasi area penyakit pada daun padi.</p>

<p>🧠 <b>Otak di Balik Aplikasi:</b> SMART Oryza ditenagai oleh model AI mutakhir bernama <b>MFBP-UNet</b>. Ini bukan sembarang arsitektur standar; kami telah meningkatkan kemampuannya dengan mengintegrasikan <i>Multi-Scale Feature Extraction</i>, <i>BATok-Multi Layer Perceptron</i>, dan <i>Dynamic Sparse Attention</i>. Teknologi ini memungkinkan AI membedakan area daun yang sehat dan sakit hingga ke tingkat piksel dengan sangat tajam.</p>

<p>📈 <b>Prestasi Model:</b> Dilatih menggunakan 1.044 citra daun padi dari dataset publik (Kaggle) dan temuan langsung di sawah Bangkalan, MFBP-UNet terbukti unggul! Pada pengujian hingga 60 epoch, model andalan kami sukses mencetak akurasi segmentasi <b>IoU sebesar 80%</b> dan <b>skor Dice 87%</b>, melampaui kemampuan UNet standar (IoU 79%, Dice 86%). Peningkatan ini membuktikan bahwa MFBP-UNet sangat siap diandalkan untuk mendeteksi penyakit daun padi secara otomatis dan presisi.</p>
</div>
"""

import base64

# 1. Fungsi Pembantu untuk Mengubah Gambar Lokal ke Base64
def get_image_base64(path_gambar):
    try:
        if os.path.exists(path_gambar):
            with open(path_gambar, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded_string}"
        else:
            # Jika file tidak ketemu, pakai placeholder agar web tidak crash
            return "https://via.placeholder.com/300x200?text=Gambar+Tidak+Ditemukan"
    except Exception:
        return "https://via.placeholder.com/300x200?text=Error"

# 2. Path Gambar Lokal Anda (Pastikan file-file ini satu folder dengan app.py Anda)
PATH_LEAF_BLAST = "blast-leaf.jpg"
PATH_BROWN_SPOT = "brown-spot-3.jpg"
PATH_HISPA = "hispa.jpg"
PATH_SERANGGA_HISPA = "rice-hispa.jpg"

# 3. Konversi Otomatis ke format yang dimengerti oleh Tag HTML <img>
URL_GAMBAR_LEAF_BLAST = get_image_base64(PATH_LEAF_BLAST)
URL_GAMBAR_BROWN_SPOT = get_image_base64(PATH_BROWN_SPOT)
URL_GAMBAR_HISPA = get_image_base64(PATH_HISPA)
URL_GAMBAR_SERANGGA_HISPA = get_image_base64(PATH_SERANGGA_HISPA)

# 4. String HTML Anda (Tetap sama, tidak perlu diubah)
PENYAKIT_TEXT = f"""
<div style='text-align: justify; font-size: 16px; line-height: 1.7;'>
    <p>Model kami dilatih secara khusus untuk mendeteksi dan melokalisasi tiga anomali utama pada daun padi berikut:</p>
    <div class='disease-card'>
        <div class='disease-title'>🦠 Leaf Blast (Blas Daun)</div>
        <p>Disebabkan oleh infeksi jamur ganas <i>Pyricularia oryzae</i>. Bintik awalnya terlihat seperti titik putih kecil, lalu membesar menjadi bercak khas berbentuk belah ketupat (berlian) dengan pusat abu-abu dan pinggiran cokelat gelap.</p>
        <div style='text-align: center; margin: 15px 0;'>
            <img src='{URL_GAMBAR_LEAF_BLAST}' alt='Contoh Leaf Blast' style='max-width: 100%; height: 200px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); object-fit: cover;'>
        </div>
        <p><b>💡 Penanganan:</b> Gunakan varietas tahan blas, hindari pemupukan Nitrogen berlebihan, atur jarak tanam agar sawah tidak terlalu lembap, dan aplikasikan fungisida (misal: <i>trisiklazol</i>) bila perlu.</p>
    </div>
    <div class='disease-card'>
        <div class='disease-title'>🍂 Brown Spot (Bercak Cokelat)</div>
        <p>Penyakit ini bagaikan "alarm" bahwa tanaman sedang kekurangan nutrisi! Disebabkan oleh jamur <i>Bipolaris oryzae</i>, gejalanya berupa bercak cokelat hingga hitam berbentuk oval menyerupai biji wijen.</p>
        <div style='text-align: center; margin: 15px 0;'>
            <img src='{URL_GAMBAR_BROWN_SPOT}' alt='Contoh Brown Spot' style='max-width: 100%; height: 200px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); object-fit: cover;'>
        </div>
        <p><b>💡 Penanganan:</b> Perbaiki kesuburan tanah dengan pemupukan berimbang (N, P, K, plus Silika), perbaiki sistem drainase sawah, dan lakukan perlakuan benih (<i>seed treatment</i>) sebelum tanam.</p>
    </div>
    <div class='disease-card'>
        <div class='disease-title'>🐛 Serangan Hama Hispa</div>
        <p>Kerusakan ini bukan karena jamur, melainkan ulah serangga nakal <i>Dicladispa armata</i>. Serangga dewasa memakan jaringan hijau daun (klorofil) dan meninggalkan jejak berupa goresan putih memanjang yang membuat daun mengering.</p>
        <div style='text-align: center; margin: 15px 0; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;'>
            <img src='{URL_GAMBAR_SERANGGA_HISPA}' alt='Wujud Serangga Hispa' style='height: 180px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);'>
            <img src='{URL_GAMBAR_HISPA}' alt='Kerusakan Daun Hispa' style='height: 180px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);'>
        </div>
        <p><b>💡 Penanganan:</b> Potong ujung daun bibit sebelum pindah tanam (untuk membuang telur hama), gunakan jaring ayun untuk menangkap hama secara mekanis, atau gunakan insektisida sistemik jika populasi sudah di luar kendali.</p>
    </div>
    <div style='background-color: #e8f5e9; padding: 15px; border-left: 5px solid #4CAF50; border-radius: 4px; font-size: 14px;'>
        <b>📚 Sumber Referensi:</b><br>
        1. <i>Rice Knowledge Bank</i> - International Rice Research Institute (IRRI).<br>
        2. Pedoman PHT BB Padi - Kementerian Pertanian Republik Indonesia.
    </div>
</div>
"""

# # URLs Gambar
# URL_GAMBAR_LEAF_BLAST = "blast-leaf.jpg"
# URL_GAMBAR_BROWN_SPOT = "brown-spot-3.jpg"
# URL_GAMBAR_HISPA = "hispa.jpg"
# URL_GAMBAR_SERANGGA_HISPA = "rice-hispa.jpg"

# PENYAKIT_TEXT = f"""
# <div style='text-align: justify; font-size: 16px; line-height: 1.7;'>
#     <p>Model kami dilatih secara khusus untuk mendeteksi dan melokalisasi tiga anomali utama pada daun padi berikut:</p>
#     <div class='disease-card'>
#         <div class='disease-title'>🦠 Leaf Blast (Blas Daun)</div>
#         <p>Disebabkan oleh infeksi jamur ganas <i>Pyricularia oryzae</i>. Bintik awalnya terlihat seperti titik putih kecil, lalu membesar menjadi bercak khas berbentuk belah ketupat (berlian) dengan pusat abu-abu dan pinggiran cokelat gelap.</p>
#         <div style='text-align: center; margin: 15px 0;'>
#             <img src='{URL_GAMBAR_LEAF_BLAST}' alt='Contoh Leaf Blast' style='max-width: 100%; height: 200px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); object-fit: cover;'>
#         </div>
#         <p><b>💡 Penanganan:</b> Gunakan varietas tahan blas, hindari pemupukan Nitrogen berlebihan, atur jarak tanam agar sawah tidak terlalu lembap, dan aplikasikan fungisida (misal: <i>trisiklazol</i>) bila perlu.</p>
#     </div>
#     <div class='disease-card'>
#         <div class='disease-title'>🍂 Brown Spot (Bercak Cokelat)</div>
#         <p>Penyakit ini bagaikan "alarm" bahwa tanaman sedang kekurangan nutrisi! Disebabkan oleh jamur <i>Bipolaris oryzae</i>, gejalanya berupa bercak cokelat hingga hitam berbentuk oval menyerupai biji wijen.</p>
#         <div style='text-align: center; margin: 15px 0;'>
#             <img src='{URL_GAMBAR_BROWN_SPOT}' alt='Contoh Brown Spot' style='max-width: 100%; height: 200px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); object-fit: cover;'>
#         </div>
#         <p><b>💡 Penanganan:</b> Perbaiki kesuburan tanah dengan pemupukan berimbang (N, P, K, plus Silika), perbaiki sistem drainase sawah, dan lakukan perlakuan benih (<i>seed treatment</i>) sebelum tanam.</p>
#     </div>
#     <div class='disease-card'>
#         <div class='disease-title'>🐛 Serangan Hama Hispa</div>
#         <p>Kerusakan ini bukan karena jamur, melainkan ulah serangga nakal <i>Dicladispa armata</i>. Serangga dewasa memakan jaringan hijau daun (klorofil) dan meninggalkan jejak berupa goresan putih memanjang yang membuat daun mengering.</p>
#         <div style='text-align: center; margin: 15px 0; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;'>
#             <img src='{URL_GAMBAR_SERANGGA_HISPA}' alt='Wujud Serangga Hispa' style='height: 180px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);'>
#             <img src='{URL_GAMBAR_HISPA}' alt='Kerusakan Daun Hispa' style='height: 180px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);'>
#         </div>
#         <p><b>💡 Penanganan:</b> Potong ujung daun bibit sebelum pindah tanam (untuk membuang telur hama), gunakan jaring ayun untuk menangkap hama secara mekanis, atau gunakan insektisida sistemik jika populasi sudah di luar kendali.</p>
#     </div>
#     <div style='background-color: #e8f5e9; padding: 15px; border-left: 5px solid #4CAF50; border-radius: 4px; font-size: 14px;'>
#         <b>📚 Sumber Referensi:</b><br>
#         1. <i>Rice Knowledge Bank</i> - International Rice Research Institute (IRRI).<br>
#         2. Pedoman PHT BB Padi - Kementerian Pertanian Republik Indonesia.
#     </div>
# </div>
# """

# =========================================================
# HELPERS
# =========================================================
@st.cache_data
def load_logs():
    try:
        df_unet = pd.read_csv("./train_logs/combined_training_log.csv")
        df_mfbp = pd.read_csv("./train_logs/mfbp_unet_log_full.csv")
        return df_unet, df_mfbp
    except Exception:
        st.error("⚠️ Log tidak ditemukan! Pastikan file CSV ada di folder aplikasi (./train_logs/).")
        return None, None

def create_training_figure(log_df):
    fig = sp.make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("<b>Loss Curve</b>", "<b>Dice & mIoU Curve</b>")
    )

    # Menyesuaikan warna agar lebih segar/modern
    colors = {
        "train": "#2E8B57", # SeaGreen
        "val": "#FF8C00",   # DarkOrange
        "dice": "#1E90FF",  # DodgerBlue
        "miou": "#9370DB"   # MediumPurple
    }

    # =====================================================
    # LOSS
    # =====================================================
    fig.add_trace(
        go.Scatter(
            x=log_df["epoch"], y=log_df["train_loss"],
            mode="lines", name="Train Loss",
            line=dict(width=3, color=colors["train"]),
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=log_df["epoch"], y=log_df["val_loss"],
            mode="lines", name="Validation Loss",
            line=dict(width=3, color=colors["val"]),
        ),
        row=1, col=1
    )

    # =====================================================
    # METRICS
    # =====================================================
    fig.add_trace(
        go.Scatter(
            x=log_df["epoch"], y=log_df["val_dice"],
            mode="lines", name="Dice Score",
            line=dict(width=3, color=colors["dice"]),
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=log_df["epoch"], y=log_df["val_miou"],
            mode="lines", name="mIoU",
            line=dict(width=3, color=colors["miou"]),
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=450,
        plot_bgcolor="#fdfdfd",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=60),
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0.5,
            xanchor="center",
        ),
    )

    # Membuat grid grafik terlihat transparan dan rapi
    fig.update_xaxes(showgrid=True, gridcolor="rgba(200,200,200,0.2)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.2)")

    return fig

def render_plot_card(fig, title):
    st.markdown(
        f"""
        <div class="grid-item">
            <h4 style="text-align:center; color: #333; margin-top: 0;">
                {title}
            </h4>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# MAIN PAGE
# =========================================================
import base64
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(base_dir, "icon.png")
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return None

def show_home():
    # Load CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    logo_base64 = get_image_base64(logo_path)
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 1.2em; vertical-align: middle;">'
    else:
        logo_html = "🌾"

    # HEADER
    st.markdown(
        f"""
        <div class="app-header">
            <!-- Sisipkan logo_html di samping teks -->
            <h1 style="display: flex; align-items: center; justify-content: center; gap: 10px;">
               {logo_html} SMART Oryza
            </h1>
            <p>Semantic Segmentation Masking AI for Rice Traits Oryza</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # BACKGROUND
    st.header("🔍 Latar Belakang", divider="green")
    st.markdown(ABSTRACT_TEXT, unsafe_allow_html=True)

    # CHARTS
    st.header("📊 Grafik Evaluasi Model", divider="green")
    df_unet, df_mfbp = load_logs()

    st.markdown("<div class='responsive-grid'>", unsafe_allow_html=True)

    if df_unet is not None:
        fig_unet = create_training_figure(df_unet)
        render_plot_card(fig_unet, "🔵 Baseline: UNet Standard")

    if df_mfbp is not None:
        fig_mfbp = create_training_figure(df_mfbp)
        render_plot_card(fig_mfbp, "🚀 Modified Baseline: MFBP-UNet")

    st.markdown("</div><br>", unsafe_allow_html=True)

    # DISEASES INFO
    st.header("🦠 Fokus Penyakit & Hama Padi", divider="green")
    st.markdown(PENYAKIT_TEXT, unsafe_allow_html=True)

# Jika ingin dijalankan secara independen untuk testing, hapus komentar di bawah:
# show_home()