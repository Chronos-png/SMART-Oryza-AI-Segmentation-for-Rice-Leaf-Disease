# Custom CSS --------------------------------------------------------------
# st.markdown(
#     """
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
#     html, body, [class*="css"]  {font-family: 'Plus Jakarta Sans', sans-serif;}
#     .app-header{background: linear-gradient(90deg, #2ECC71 0%, #16A085 100%); padding:18px; border-radius:12px; color: white; margin-bottom:20px}
#     .card{background: white; padding:16px; border-radius:10px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); margin-bottom:20px}
#     .small-muted{color:#6b6b6b; font-size:13px}
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background Premium */
    .main {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 40%, #A5D6A7 100%) !important;
        color: white !important;
    }

    /* Sidebar Premium */
    section[data-testid="stSidebar"] {
        background-color: #0F2A17 !important;
        border-right: 2px solid #D4AF37;
    }

    /* Sidebar Text */
    section[data-testid="stSidebar"] * {
        color: #C5E1A5 !important;
    }

    /* Card Premium */
    .card {
        background-color: #C5E1A5;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #D4AF37;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        margin-bottom: 15px;
    }

    /* Header */
    .app-header{
        background: linear-gradient(90deg, #2ECC71 0%, #16A085 100%); 
        padding:18px; border-radius:12px;
        margin-bottom:20px
    }
    .app-header h1 {
        color: white !important;
    }

    .app-header p {
        color: #E8F5E9 !important;
    }

    /* Buttons */
    .stButton button {
        background-color: #D4AF37 !important;
        color: #0F2A17 !important;
        border-radius: 8px !important;
        border: none;
        font-weight: 600;
        padding: 10px 20px;
        transition: 0.2s ease-in-out;
    }

    .stButton button:hover {
        background-color: #C5E1A5 !important;
        color: #0F2A17 !important;
        border: 1px solid #D4AF37 !important;
        transform: translateY(-2px);
    }

    /* File Uploader */
    .stFileUploader {
        background-color: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 10px;
    }

</style>
"""