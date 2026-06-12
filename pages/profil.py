import streamlit as st
import pandas as pd

def get_scopus_publications(author_id):
    try:
        from pybliometrics.scopus import AuthorRetrieval
    except ImportError:
        return None

    try:
        # Mengambil data penulis berdasarkan ID Scopus
        au = AuthorRetrieval(author_id)
        
        # Mengambil daftar dokumen/publikasi (maksimal 10 terakhir agar cepat)
        docs = au.get_documents(size=10)
        
        pub_list = []
        for doc in docs:
            # Mengambil informasi penting: Judul, Jurnal, Tahun
            pub_list.append({
                "Judul": doc.title,
                "Jurnal/Konferensi": doc.publicationName,
                "Tahun": doc.coverDate.split("-")[0],
                "Sitasi": doc.citedby_count
            })
        return pd.DataFrame(pub_list)
    except Exception as e:
        # Jika API bermasalah/tidak terhubung ke jaringan kampus
        return None
 
def show_profile_mbkm(logo_html="🏛️"):  
    # --- SECTION 1: PROFIL UNIVERSITAS ---
    st.markdown(f"<h1>{logo_html} Profil Universitas & Peneliti</h1>", unsafe_allow_html=True)
    st.subheader("Universitas Trunojoyo Madura (UTM)", divider="green")

    # ===========================================================================
    col_univ_logo, col_univ_info = st.columns([1, 2])

    with col_univ_logo:
        # Menggunakan placeholder gambar gedung/logo, Anda bisa menggantinya dengan jalur lokal jika ada
        st.image("data:image/jpeg;base64,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", caption="Kampus Universitas Trunojoyo Madura", use_container_width=True)
                
    with col_univ_info:
        st.markdown("""
        **Universitas Trunojoyo Madura (UTM)** adalah universitas yang menyelenggarakan Tri Dharma Perguruan Tinggi yang bermutu dan mampu bersaing dengan perguruan tinggi pada tingkat nasional dan internasional.
            Mampu menghadapi perkembangan teknologi dan inovasi maupun kebijakan-kebijakan pemerintah di bidang pendidikan, kebudayaan, riset dan teknologi. 
                    Mandiri dalam Keilmuan dan Keuangan.


        **Universitas Trunojoyo Madura (UTM)** berkomitmen penuh dalam mendukung program **Merdeka Belajar Kampus Merdeka (MBKM)**, khususnya pada skema **MBKM Riset / Penelitian**. 
        Melalui skema ini, mahasiswa diintegrasikan langsung ke dalam proyek riset dosen yang relevan dengan kebutuhan industri dan pengembangan potensi daerah, khususnya di wilayah Madura dan skala nasional.
        
        """)
        st.markdown("[🌐 Kunjungi Web Resmi UTM](https://www2.trunojoyo.ac.id/)", unsafe_allow_html=True)
    # ===========================================================================
    
    # Statistik Riset/MBKM di UTM
    st.subheader("")
    st.subheader("STATISTIK UNIVERSITAS TRUNOJOYO MADURA", divider="grey")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="MAHASISWA AKTIF", value="20K+", delta="")
    m2.metric(label="DOSEN", value="588", delta="")
    m3.metric(label="PROFESOR", value="32", delta="")
    m4.metric(label="FAKULTAS", value="7", delta="")

    m21, m22, m23, m24 = st.columns(4)
    m21.metric(label="LEKTOR", value="308", delta="")
    m22.metric(label="LEKTOR KEPALA", value="113", delta="")
    m23.metric(label="ASISTEN AHLI", value="177", delta="")
    m24.metric(label="TENDIK", value="269", delta="")

    st.write("---")

    # --- SECTION 2: PROFIL PENELITI / PEMBIMBING UTAMA ---
    st.subheader("🔬 Tim Peneliti MBKM")
    st.write("Berikut adalah tim peneliti yang terlibat dalam proyek penelitian pada program MBKM yang diterapkan pada aplikasi ini:")

    # --- Peneliti 1 (Fokus Agrikultur / AI) ---
    with st.container(border=True):
        col_p1_img, col_p1_txt = st.columns([1, 3])
        
        with col_p1_img:
            # Anda bisa mengganti dengan foto dosen asli UTM nantinya
            st.image("https://via.placeholder.com/150", caption="Pembimbing Utama 1", use_container_width=True)
            
        with col_p1_txt:
                    # Menggunakan gelar yang benar, ditambahkan spasi standar penulisan gelar
                    st.markdown("### Prof. Dr. Rima Tri Wahyuningrum, S.T., M.T.")
                    
                    # PILIHAN CAPTION (Menggunakan Opsi 2 yang sangat cocok untuk profil riset/MBKM)
                    st.caption("Pembimbing Riset | Guru Besar & Dosen Pascasarjana FT-UTM")
                    
                    # Merapikan tampilan riwayat pendidikan menggunakan format list markdown yang elegan
                    st.markdown("""
                    **🎓 Riwayat Pendidikan:**
                    * **Doktor (S3):** Teknik Elektro (Jaringan Cerdas Multimedia) – Institut Teknologi Sepuluh Nopember (ITS)
                    * **Magister (S2):** Teknik Elektro (Jaringan Cerdas Multimedia) – Institut Teknologi Sepuluh Nopember (ITS)
                    * **Sarjana (S1):** Teknik Elektro – Institut Teknologi Sepuluh Nopember (ITS)
                    """)
                    
                    # Publikasi dan Proyek yang disesuaikan dengan bidang Teknik Elektro/Computer Vision beliau
                    with st.expander("📚 Publikasi Scopus Terkini (Live Data)"):
                        st.write("Mengambil data langsung dari Scopus...")
                        
                        # Panggil fungsi dengan ID Scopus Prof. Rima
                        df_pub = get_scopus_publications("55977023600")
                        
                        if df_pub is not None and not df_pub.empty:
                            # Menampilkan dalam bentuk tabel Streamlit yang rapi dan bisa di-scroll
                            st.dataframe(df_pub, use_container_width=True)
                        else:
                            # Fallback jika API gagal (misal di luar jaringan kampus)
                            st.warning("Gagal memuat data otomatis. Silakan periksa koneksi jaringan kampus/API Key.")

    # st.write("") # Spacer

    # # --- Peneliti 2 (Fokus Teknik Informatika / Data Science) ---
    # with st.container(border=True):
    #     col_p2_img, col_p2_txt = st.columns([1, 3])
        
    #     with col_p2_img:
    #         st.image("https://via.placeholder.com/150", caption="Pembimbing Utama 2", use_container_width=True)
            
    #     with col_p2_txt:
    #         st.markdown("### Dr. Bain Khusnul Khotimah, S.T., M.Kom.")
    #         st.caption("Ketua Kelompok Riset Komputasi Cerdas & Dosen Teknik Informatika UTM")
    #         st.write("""
    #         **Bidang Keahlian & Proyek MBKM:** *Data Mining*, *Soft Computing*, dan *Artificial Intelligence* (AI).  
            
    #         Membuka peluang MBKM Riset bagi mahasiswa yang tertarik pada pemrosesan citra digital (*image processing*), pembelajaran mendalam (*deep learning*), dan segmentasi objek untuk mendukung sektor pertanian pintar (*smart agriculture*).
    #         """)
            
    #         with st.expander("📚 Publikasi & Proyek Riset Aktif"):
    #             st.markdown("""
    #             * *Khotimah, B. K., et al.* "Implementation of Computer Vision for Agricultural Product Grading." *Journal of ICT Research*.
    #             * *Proyek Riset Aktif (2026):* "Sistem Pengenalan Gejala Penyakit Daun Menggunakan Metode Klasifikasi Terarah." (Melibatkan Mandat Kerja Sama MBKM).
    #             """)

    # --- FOOTER ---
    st.write("---")
    st.caption("© 2026 MBKM Riset - Universitas Trunojoyo Madura. Dikembangkan menggunakan Streamlit. - Last Updated: 2026-01-15")
