def get_scholar_publications(author_id):
    try:
        # Mencari profil berdasarkan ID Google Scholar
        author = scholarly.search_author_id(author_id)
        # Mengisi data spesifik publikasi (hanya mengambil info dasar agar cepat)
        author_filled = scholarly.fill(author, sections=['publications'])
        
        pub_list = []
        # Ambil 5-10 publikasi teratas saja agar loading tidak terlalu lama
        for pub in author_filled['publications'][:5]:
            pub_info = scholarly.fill(pub)
            pub_list.append({
                "Judul": pub_info['bib'].get('title', 'N/A'),
                "Tahun": pub_info['bib'].get('pub_year', 'N/A'),
                "Sitasi": pub_info.get('num_citations', 0)
            })
        return pub_list
    except Exception as e:
        return None
