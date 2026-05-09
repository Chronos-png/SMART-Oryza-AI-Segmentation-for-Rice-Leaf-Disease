import io
import os
import cv2
import torch
import numpy as np
import streamlit as st
import albumentations as album

from PIL import Image
from albumentations.pytorch import ToTensorV2

# Pastikan file MFBP_UNet.py berada di direktori yang sama
from MFBP_UNet import MFBP_UNet

import gdown


# =========================================================
# CONFIG
# =========================================================
MODEL_PATH = "./model/model_mfbp-unet.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMAGE_SIZE = 512


# =========================================================
# CSS (Tema Agrikultur & UI Modern)
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
    font-size: 2.2em;
    font-weight: 800;
    letter-spacing: 1px;
}
.app-header p {
    margin: 8px 0 0 0;
    font-size: 1.1em;
    font-style: italic;
    opacity: 0.95;
}
/* Mempercantik kotak metrik bawaan Streamlit */
div[data-testid="metric-container"] {
    background-color: #f8faf8;
    border: 1px solid #e2e8e0;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
</style>
"""


# =========================================================
# MODEL LOADER
# =========================================================
@st.cache_resource(show_spinner="Memuat model deep learning...")
def load_model():
    # 1. Inisialisasi arsitektur model
    model = MFBP_UNet(
        in_ch=3,
        num_classes=2,
        base_ch=32
    )
    
    # 2. CEK FILE FISIK (PERBAIKAN UTAMA)
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        file_id = "1X9n2s8m7l5k3j2h1g0f9a8b7c6d5e4"
        url = f"https://drive.google.com/uc?id={file_id}"
        
        with st.spinner("Mengunduh model (130MB)... Mohon tunggu."):
            gdown.download(url, MODEL_PATH, quiet=False)
            
    state = torch.load(MODEL_PATH, map_location=torch.device('cpu'))

    if "model_state_dict" in state:
        model.load_state_dict(state["model_state_dict"])
    else:
        model.load_state_dict(state)

    model.to(DEVICE)
    model.eval()

    return model

# =========================================================
# TRANSFORM
# =========================================================
inference_transform = album.Compose([
    album.Resize(IMAGE_SIZE, IMAGE_SIZE),
    ToTensorV2()
])


# =========================================================
# PREDICTION
# =========================================================
def predict_mask(image_pil: Image.Image, model) -> np.ndarray:
    image_np = np.array(image_pil)
    h, w = image_np.shape[:2]

    augmented = inference_transform(image=image_np)
    tensor = augmented["image"].float().unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)

    # =============================================
    # BINARY SEGMENTATION
    # =============================================
    if logits.shape[1] == 1:
        probs = torch.sigmoid(logits)
        mask = (probs > 0.5).squeeze().cpu().numpy().astype(np.uint8)

    # =============================================
    # MULTI-CLASS SEGMENTATION
    # =============================================
    else:
        mask = torch.argmax(logits, dim=1).squeeze().cpu().numpy().astype(np.uint8)

    # Kembalikan mask ke ukuran gambar asli
    mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
    return mask


# =========================================================
# OVERLAY
# =========================================================
def create_overlay(image_pil: Image.Image, mask: np.ndarray, color=(255, 40, 80), alpha=120):
    image_np = np.array(image_pil)
    color_layer = np.zeros_like(image_np)
    color_layer[mask == 1] = color

    overlay = cv2.addWeighted(
        image_np, 1.0,
        color_layer, alpha / 255.0,
        0
    )
    return overlay


# =========================================================
# CONVERT MASK
# =========================================================
def mask_to_bytes(mask: np.ndarray):
    image_pil = Image.fromarray(mask)
    buffer = io.BytesIO()
    image_pil.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# =========================================================
# MAIN PAGE
# =========================================================
def show_segmentation():
    # Load CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # HEADER
    st.markdown(
        """
        <div class="app-header">
            <h1>🧪 Uji Segmentasi AI</h1>
            <p>Unggah foto daun padi Anda, dan biarkan AI memetakan area penyakit secara presisi!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # LOAD MODEL
    model = load_model()

    # =====================================================
    # UPLOAD SECTION
    # =====================================================
    st.info("""
    💡 **Tips:**
    1. Untuk hasil terbaik, gunakan gambar daun padi yang fokus dan memiliki pencahayaan yang cukup.
    2. Penyakit yang terdeteksi akan ditandai dengan warna merah pada gambar hasil overlay.
    3. Fokus penyakit pada model saat ini hanya leaf blast, brown spot, dan hispa. Pastikan gambar yang diunggah memiliki salah satu dari ketiga penyakit tersebut untuk melihat hasil segmentasi yang optimal.
    """)
    
    uploaded_file = st.file_uploader(
        "📂 Pilih gambar daun tanaman (JPG/PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is None:
        # Hentikan eksekusi di sini jika belum ada file
        return

    # Jika file sudah diunggah, tampilkan antarmuka pratinjau
    image = Image.open(uploaded_file).convert("RGB")

    st.markdown("---")
    
    # Membagi layout menjadi 2 kolom untuk pratinjau dan tombol aksi
    input_col, action_col = st.columns([1, 1])

    with input_col:
        st.markdown("### 📸 Gambar Input")
        st.image(image, use_container_width=True, caption="Siap untuk dianalisis")

    with action_col:
        st.markdown("### ⚙️ Panel Kontrol")
        st.write("Model **MFBP-UNet** telah dimuat dan siap digunakan. Klik tombol di bawah ini untuk memulai proses ekstraksi fitur dan masking.")
        
        # Tombol utama (primary) agar lebih mencolok
        run = st.button("🔍 Analisis Gambar Sekarang", type="primary", use_container_width=True)

    if not run:
        return

    # =====================================================
    # PREDICTION SECTION
    # =====================================================
    st.markdown("---")
    
    with st.spinner("⏳ Memproses citra dengan MFBP-UNet... Mohon tunggu sebentar."):
        mask = predict_mask(image, model)
        grayscale_mask = (mask * 255).astype(np.uint8)
        overlay = create_overlay(image, mask)

    st.success("✅ Analisis berhasil diselesaikan!")

    # =====================================================
    # RESULT SECTION
    # =====================================================
    st.header("🎯 Hasil Segmentasi", divider="green")

    col1, col2 = st.columns(2)

    with col1:
        st.image(overlay, caption="🔴 Overlay Mask (Visualisasi Area Penyakit)", use_container_width=True)
        st.caption("*Menampilkan area yang terdeteksi sakit (warna merah) di atas gambar asli.*")

    with col2:
        st.image(grayscale_mask, caption="🤖 Grayscale Mask (Output Model Murni)", use_container_width=True)
        st.caption("*Citra biner murni; putih adalah penyakit, hitam adalah daun sehat/background.*")

    # =====================================================
    # METRICS & DOWNLOAD SECTION
    # =====================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Rangkuman Analisis")
    
    metric1, metric2 = st.columns(2)

    with metric1:
        # Menghitung rasio area penyakit terhadap keseluruhan gambar
        st.metric(
            label="Tingkat Kerusakan (Area Tersegmentasi)",
            value=f"{mask.mean() * 100:.2f}%"
        )

    with metric2:
        st.metric(
            label="Model yang digunakan:",
            value="MFBP-UNet"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menggunakan kolom untuk memusatkan tombol download
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.download_button(
            label="⬇️ Unduh Hasil Masking (PNG)",
            data=mask_to_bytes(grayscale_mask),
            file_name="hasil_masking_ai.png",
            mime="image/png",
            use_container_width=True
        )

# Jika ingin dijalankan secara independen untuk testing, hapus komentar di bawah:
# show_segmentation()