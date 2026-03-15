import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Go Taxi", page_icon="🏍️ ")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    h1, h2, h3, p, b { color: black !important; text-align: center; }
    .driver-card {
        background-color: rgba(255, 255, 255, 0.3);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 2px solid black;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo y Título
st.title("🚕 GO TAXI")
st.write("### ¡Tu transporte seguro en Portuguesa!")

# Conexión al Sheets
sheet_id = "1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(url)
    # Limpiamos nombres de columnas por si tienen espacios locos
    df.columns = df.columns.str.strip()
    
    # Buscamos las columnas correctas sin importar mayúsculas
    col_nombre = [c for c in df.columns if 'nombre' in c.lower()][0]
    col_estatus = [c for c in df.columns if 'estatus' in c.lower()][0]
    col_telefono = [c for c in df.columns if 'telefono' in c.lower() or 'teléfono' in c.lower()][0]

    for index, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="driver-card">
                <b>👤 Chófer:</b> {row[col_nombre]}<br>
                <b>📍 Estatus:</b> {row[col_estatus]}
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de llamada negro
            tel = str(row[col_telefono]).replace(".0", "").replace(" ", "")
            st.markdown(f'<a href="tel:{tel}"><button style="width:100%; background-color:black; color:white; padding:12px; border-radius:15px; border:none; font-weight:bold; font-size:18px; cursor:pointer;">📞 LLAMAR AHORA</button></a>', unsafe_allow_html=True)
            st.write("") 

except Exception as e:
    st.error(f"Error de conexión: Verifica los nombres de las columnas en tu Excel. {e}")
