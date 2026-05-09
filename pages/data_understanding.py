import os
import pandas as pd
import streamlit as st
from PIL import Image

# =========================================================
# CSS (Lebih Estetis & Modern)
# =========================================================
IMAGE_CARD_CSS = """
<style>
/* Styling Header Aplikasi */
.app-header {
    background: linear-gradient(135deg, #2E8B57, #8FBC8F);
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}
.app-header h1 {
    margin: 0;
    font-size: 2.2em;
    font-weight: 800;
}
.app-header p {
    margin: 5px 0 0 0;
    font-size: 1.1em;
    opacity: 0.9;
}

/* Styling Judul Kartu Gambar */
.card-title {
    font-weight: bold;
    font-size: 1.1em;
    text-align: center;
    margin-bottom: -5px; /* Menarik gambar agar lebih rapat */
    padding: 10px 0;
    border-radius: 10px 10px 0 0;
    color: white;
    background: linear-gradient(135deg, #3CB371, #2E8B57);
    z-index: 1;
    position: relative;
}

/* Styling Deskripsi di bawah Gambar */
.card-desc {
    text-align: justify;
    font-size: 13px;
    line-height: 1.5;
    color: #333;
    background-color: #f8faf8;
    margin-top: -5px; /* Menarik gambar agar lebih rapat */
    padding: 15px;
    border-radius: 0 0 10px 10px;
    border: 1px solid #e0e0e0;
    border-top: none;
    box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
}
</style>
"""

# =========================================================
# TEXT (Lebih Santai & Storytelling)
# =========================================================
DATASET_DESCRIPTION = """
<div style='text-align: justify; font-size: 16px; line-height: 1.7; margin-bottom: 20px;'>
<p>Menghasilkan model AI yang cerdas tentu membutuhkan "bahan bakar" data yang berkualitas! 🌾✨ Dataset yang kami gunakan dalam penelitian ini merangkum dua sumber utama untuk memastikan model dapat mengenali penyakit daun padi secara akurat:</p>
<ul style='line-height: 1.8;'>
    <li>🌍 <b>Data Publik (Kaggle):</b> Kami memanfaatkan dataset populer yang berjudul <i>"Rice Leafs"</i> dari platform Kaggle (tautan: <a href='https://www.kaggle.com/datasets/shayanriyaz/riceleafs' target='_blank'>di sini</a>).</li>
    <li>🇮🇩 <b>Data Lokal (Bangkalan):</b> Selain data padi dari kaggle kami menambah variasinya dengan padi yang ada di Kabupaten Bangkalan.</li>
</ul>
<p>Kombinasi gambar-gambar ini kemudian dianotasi dengan teliti sebelum masuk ke pelatihan model. Untuk rincian komposisi datanya ada pada tabel di bawah ini! 👇</p>
</div>
"""

# =========================================================
# DATAFRAME
# =========================================================
def create_dataset_dataframe():
    df = pd.DataFrame({
        "No": [1, 2, 3],
        "Jenis Penyakit": ["Brown Spot", "Leaf Blast", "Hispa"],
        "Kaggle (Publik)": [300, 300, 300],
        "Bangkalan (Lokal)": [48, 48, 48],
        "Total Gambar": [348, 348, 348]
    })

    # Mengubah warna header tabel menjadi hijau agar senada
    styled_df = (
        df.style
        .set_properties(**{
            "text-align": "center",
            "font-weight": "500",
            "border": "1px solid #e0e0e0",
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#2E8B57"), 
                    ("color", "white"),
                    ("font-weight", "bold"),
                    ("text-align", "center"),
                    ("font-size", "15px")
                ]
            }
        ])
    )
    return styled_df

# =========================================================
# IMAGE DATA (Deskripsi Lebih Menarik)
# =========================================================
def get_sample_images():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_dir = os.path.join(base_dir, "sample_images")

    image_data = [
        {
            "label": "🍂 Brown Spot",
            "path": os.path.join(image_dir, "IMG_20190420_190305.jpg"),
            "description": "Bercak oval mirip biji wijen yang menjadi 'alarm' bahwa tanaman sedang kekurangan nutrisi. Sering muncul di tanah yang kurang subur."
        },
        {
            "label": "🦠 Leaf Blast",
            "path": os.path.join(image_dir, "IMG_5506.jpg"),
            "description": "Musuh utama petani! Bercak misterius berbentuk belah ketupat dengan pusat abu-abu ini disebabkan oleh infeksi jamur ganas."
        },
        {
            "label": "🐛 Hispa",
            "path": os.path.join(image_dir, "Screenshot 2025-12-01 132635.png"),
            "description": "Jejak nakal serangga Hispa yang menggerogoti zat hijau daun, menyisakan goresan putih memanjang yang merusak estetika dan kesehatan daun."
        },
        {
            "label": "🤖 Mask (Anotasi)",
            "path": os.path.join(image_dir, "Screenshot 2025-12-01 132720.png"),
            "description": "<i>Di balik layar:</i> Ini adalah 'kacamata' AI (citra biner) yang memandu model agar bisa fokus tepat sasaran pada lokasi penyakit di daun."
        },
    ]
    return image_data

# =========================================================
# RENDER IMAGE GRID
# =========================================================
def render_image_grid():
    image_data = get_sample_images()
    cols = st.columns(4)

    for col, item in zip(cols, image_data):
        with col:
            # Title
            st.markdown(f"<div class='card-title'>{item['label']}</div>", unsafe_allow_html=True)
            
            # Image
            try:
                image = Image.open(item["path"])
                st.image(image, use_container_width=True)
            except FileNotFoundError:
                st.warning(f"Gambar {item['label']} tidak ditemukan.")

            # Description
            st.markdown(f"<div class='card-desc'>{item['description']}</div>", unsafe_allow_html=True)

# =========================================================
# MAIN PAGE
# =========================================================
def show_data_understanding():
    # Load CSS
    st.markdown(IMAGE_CARD_CSS, unsafe_allow_html=True)

    # Header
    st.markdown(
        """
        <div class="app-header">
            <h1>🌾 Data Understanding</h1>
            <p>Mengenal lebih dekat data di balik kecerdasan model AI kita</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Dataset Description
    st.markdown(DATASET_DESCRIPTION, unsafe_allow_html=True)

    # Dataframe
    dataset_df = create_dataset_dataframe()
    st.dataframe(dataset_df, use_container_width=True, hide_index=True)

    # Divider
    st.markdown("---")

    # Sample Images Section
    st.markdown("### 📸 Galeri Gejala Penyakit")
    st.caption("Berikut adalah cuplikan gambar dari dataset beserta mask anotasi yang digunakan:")
    st.markdown("<br>", unsafe_allow_html=True) # Extra space

    render_image_grid()

# Panggil fungsi ini di file utama (misal: app.py)
# show_data_understanding()