import streamlit as st
import pandas as pd

# 1. Configuración visual (Fondo naranja y estilo)
st.set_page_config(page_title="Go Taxi App", page_icon="🚕")

st.markdown("""
    <style>
    .stApp {
        background-color: #FF8C00; /* Ese naranja llamativo */
    }
    h1, h2, p, b {
        color: black !important;
        text-align: center;
    }
    .driver-card {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid black;
    }
    .stButton>button {
        background-color: black !important;
        color: white !important;
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Tu Logo y Título
st.title("🚕 GO TAXI")
st.write("### ¡Tu transporte seguro en Portuguesa!")

# 3. Conexión a tu Sheets
sheet_id = "1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(url)
    
    # 4. Mostrar conductores de forma bonita
    for index, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="driver-card">
                <b>👤 Chófer:</b> {row['Nombre']}<br>
                <b>📍 Estatus:</b> {'🟢 Disponible' if row['Estatus'] == 'Disponible' else '🔴 Ocupado'}
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de llamada (funciona en celulares)
            telefono = str(row['Telefono']).replace(" ", "")
            st.markdown(f'<a href="tel:{telefono}"><button style="width:100%; background-color:black; color:white; padding:10px; border-radius:15px; border:none; font-weight:bold; cursor:pointer;">📞 LLAMAR AHORA</button></a>', unsafe_allow_html=True)
            st.write("") # Espacio

except Exception as e:
    st.error("Estamos actualizando la lista de conductores...")
