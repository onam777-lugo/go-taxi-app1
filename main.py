import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="GO TAXI PÍRITU", page_icon="logo.jpg", layout="centered")

# Conexión
url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Carga de datos
try:
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
    precio = str(df_config.iloc[0, 1])
except:
    precio = "---"

# Estilo Naranja y Negro
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FF8C00; }}
    .banner {{ background-color: black; color: #FF8C00; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
    .card {{ background-color: #FEE0C0; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 10px solid #28a745; color: black; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }}
    </style>
    <div class="banner">
        <span style="color:white; font-weight:bold; letter-spacing: 2px;">GO TAXI PÍRITU</span><br>
        <span style="color:white; font-size:12px;">TARIFA MÍNIMA HOY</span><br>
        <b style="font-size:35px;">Bs. {precio}</b>
    </div><br>
    """, unsafe_allow_html=True)

# Lista de Choferes Disponibles
if not df.empty:
    df.columns = df.columns.str.strip().str.upper()
    # Solo mostramos los que dicen "Disponible"
    disponibles = df[df['ESTATUS'].str.contains('Disponible', case=False, na=False)]
    
    st.markdown("<h4 style='color:white; text-align:center;'>🚖 Unidades en Línea</h4>", unsafe_allow_html=True)
    
    for _, fila in disponibles.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="card">
                    <b style="font-size:18px;">{fila['NOMBRE']}</b><br>
                    <small>Código: #{fila['CODIGO']}</small><br>
                    <span>📱 {fila['TELEFONO']}</span>
                </div>
            """, unsafe_allow_html=True)
            with st.expander("SOLICITAR TAXI"):
                st.write(f"**Datos de Pago:** {fila.get('DATOSPAGO', 'Consultar al chofer')}")
                st.link_button(f"Llamar a {fila['NOMBRE']}", f"tel:{fila['TELEFONO']}", use_container_width=True)
else:
    st.info("Buscando unidades disponibles...")

st.markdown('<p style="text-align:center; color:white; font-size:10px; margin-top:50px;">Desarrollado por Workflow Designer Onam</p>', unsafe_allow_html=True)
