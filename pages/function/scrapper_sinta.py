import streamlit as st
import requests
from bs4 import BeautifulSoup

@st.cache_data(ttl=3600)  # Menyimpan cache selama 1 jam agar halaman cepat terbuka
def get_sinta_metrics(author_id):
    """
    Mengambil data Score dan Indeks dari profil SINTA secara real-time.
    Menggunakan selektor CSS yang disesuaikan dengan struktur update SINTA terbaru.
    """
    url = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{author_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Nilai default berdasarkan data riil dari screenshot Anda (sebagai antisipasi jika koneksi gagal)
    metrics = {
        "sinta_score_overall": "0",
        "sinta_score_3yr": "0",
        "scopus_hindex": "0",
        "gscholar_hindex": "0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- Perbaikan Selektor SINTA Score ---
            # Pada update SINTA terbaru, skor besar biasanya diletakkan di dalam class 'pr-num' atau struktur 'stat-item'
            # Kita cari semua elemen teks yang mengandung angka skor di baris profil
            stat_items = soup.find_all('div', class_='stat-item')
            
            temporary_scores = []
            for item in stat_items:
                num_div = item.find('div', class_='stat-num') or item.find('span')
                if num_div:
                    temporary_scores.append(num_div.text.strip())
            
            # Jika selektor div di atas berhasil menarik data dari web SINTA:
            if len(temporary_scores) >= 2:
                metrics["sinta_score_overall"] = temporary_scores[0]
                metrics["sinta_score_3yr"] = temporary_scores[1]
                
            # --- Alternatif Selektor Cadangan 2: Menembak langsung lewat class 'pr-num' ---
            else:
                pr_nums = soup.find_all('div', class_='pr-num')
                if len(pr_nums) >= 2:
                    metrics["sinta_score_overall"] = pr_nums[0].text.strip()
                    metrics["sinta_score_3yr"] = pr_nums[1].text.strip()
            
            # --- Menarik data H-Index dari kolom Summary (Kanan Web SINTA) ---
            # Mencari teks h-index di dalam baris tabel summary
            rows = soup.find_all('tr')
            for row in rows:
                row_text = row.text.lower()
                cells = row.find_all('td')
                if 'h-index' in row_text and len(cells) >= 3:
                    # cells[1] biasanya untuk Scopus, cells[2] untuk Google Scholar
                    metrics["scopus_hindex"] = cells[1].text.strip()
                    metrics["gscholar_hindex"] = cells[2].text.strip()
                    
    except Exception:
        # Jika terjadi galat jaringan, fungsi akan otomatis mengembalikan nilai dictionary default di atas
        pass
        
    return metrics