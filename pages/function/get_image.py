import base64


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
    
    import base64

def get_image_base64_2(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()