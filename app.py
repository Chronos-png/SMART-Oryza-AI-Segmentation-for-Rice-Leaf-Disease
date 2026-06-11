import streamlit as st
from PIL import Image
import os
from pages.home import show_home
from pages.data_understanding import show_data_understanding
from pages.segmentation import show_segmentation

# --------------------------------------------
# Config
# --------------------------------------------
LOGO_PATH = "iconbg.png"
TR_LOGO_PATH = "icon.png"
try:
    img_logo = Image.open(LOGO_PATH)
    img_tr_logo = Image.open(TR_LOGO_PATH)
    st.set_page_config(
        page_title="SMART Oryza | AI Segmentation",
        page_icon=img_tr_logo,
        layout="wide",
        initial_sidebar_state="expanded"
    )
except FileNotFoundError:
    st.set_page_config(
        page_title="SMART Oryza | AI Segmentation", 
        page_icon="🌾", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =========================================================
# IMPORTS
# =========================================================

import io
import cv2
import torch
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp

from albumentations.pytorch import ToTensorV2
import albumentations as album

from MFBP_UNet import MFBP_UNet

from components.styles import CUSTOM_CSS

import torch.nn as nn
from huggingface_hub import hf_hub_download

# CSS kustom
HIDE_ST_STYLE = """
<style>
    /* Menyembunyikan menu auto-navigasi folder 'pages/' bawaan Streamlit */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS + HIDE_ST_STYLE, unsafe_allow_html=True)


# Sidebar Navigation ------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        # Menampilkan Logo
        try:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<br>", unsafe_allow_html=True) 
                st.image(Image.open(LOGO_PATH), use_container_width=True)
            
            st.markdown(
                "<div style='text-align:center; color:#2E8B57; font-weight:bold; margin-top:-5px; margin-bottom:20px; font-size:1.1em;'>SMART ORYZA v1.0</div>", 
                unsafe_allow_html=True
            )
        except NameError:
            st.title("🌾 SMART Oryza")
            
        # Judul Navigasi
        st.markdown("### 🧭 Navigasi Utama")

        # Membuat kamus halaman
        pages_dict = {
            "Home": show_home,
            "Data Understanding": show_data_understanding,
            "Segmentasi": show_segmentation
        }

        # Menu Radio Kustom
        choice = st.radio(
            label="Menu Navigasi",
            options=list(pages_dict.keys()),
            label_visibility="collapsed"
        )

        # -----------------------------------------------------------
        # Footer Sidebar
        # -----------------------------------------------------------
        st.markdown("---")
        st.header("Tentang Aplikasi")
        st.info(
            "Aplikasi ini dibuat untuk demonstrasi segmentasi penyakit daun padi menggunakan arsitektur **MFBP-UNet**. "
            "Aplikasi ini dikembangkan sebagai bagian dari penelitian untuk MBKM Riset yang dilaksanakan di Universitas Trunojoyo Madura."
        )
        st.write("Last Updated — June 2026")
        
        # svg_github = """
        # <svg height="18" viewBox="0 0 16 16" version="1.1" width="18" aria-hidden="true" style="vertical-align: middle; margin-right: 5px;">
        #   <path fill="#2E8B57" fill-rule="evenodd"
        #     d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
        #     0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52
        #     -.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64
        #     -.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 012.01-.27c.68.003
        #     1.36.092 2.01.27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75
        #     -3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.19 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
        # </svg>
        # """
        st.markdown(
            f"""
            <div style="font-size: 0.9em;">
                <b> Tim Penelitian: </b> 
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><span style="color: #2E8B57;">1. Prof. Dr. Rima Tri Wahyuningrum, ST., MT.</span> <br> <a href="mailto:rimatriwahyuningrum@trunojoyo.ac.id" style="color: #2E8B57; text-decoration: none;"><b>Email:</b> rimatriwahyuningrum@trunojoyo.ac.id</a></li>
                    <li><span style="color: #2E8B57;">2. Ahmad Ar-rosyid Hidayatullah</span> <br> <a href="mailto:rosyi.drey@gmail.com" style="color: #2E8B57; text-decoration: none;"><b>Email:</b> rosyi.drey@gmail.com</a></li>
                <ul>
            </div>

            <div style="font-size: 0.9em;">
                <b> Prodi: </b> S1 Teknik Informatika dan S2 PSDA
                <b> Universitas: </b> <a href="https://www2.trunojoyo.ac.id/" target="_blank" style="color: #2E8B57; text-decoration: none; display: inline-flex; align-items: center;"> Universitas Trunojoyo Madura</a>
            </div>
            """, unsafe_allow_html=True)
        # <b>Kontak:</b> <a href="mailto:rosyi.drey@gmail.com" style="color: #2E8B57; text-decoration: none;">rosyi.drey@gmail.com</a><br>
        # <b>Github:</b> <a href="https://github.com/Chronos-png" target="_blank" style="color: #2E8B57; text-decoration: none; display: inline-flex; align-items: center;">{svg_github} Chronos-png</a>
        return pages_dict, choice

pages_dict, user_choice = render_sidebar()
pages_dict[user_choice]()