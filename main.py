import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

# Conexión
url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. CARGA DE DATOS SEGURA
try:
    # Intentamos leer Sheet1, si falla usamos la primera hoja disponible
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    df.columns = df.columns.str.strip().str.upper()
    
    # Intentamos leer CONFIG
    df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
    df_config.columns = df_config.columns.str.strip().str.upper()
    
    # Buscamos el precio sin importar si está en mayúsculas o minúsculas
    precio_actual = df_config.loc[df_config['PARAMETRO'].str.contains('PRECIO', case=False, na=False), 'VALOR'].values[0]
except Exception as e:
    st.warning("⚠️ Ajustando conexión con las hojas de cálculo...")
    df = pd.DataFrame()
    precio_actual = "Consultar"

# --- EL RESTO DEL DISEÑO SE MANTIENE IGUAL ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FF8C00; }}
    .precio-banner {{
        background-color: black; color: #FF8C00; padding: 15px; border-radius: 15px; 
        text-align: center; margin-bottom: 20px; border: 2px solid white;
    }}
    .driver-card {{ 
        background-color: #FEE0C0; padding: 15px; border-radius: 12px; 
        border-left: 10px solid var(--status-color); margin-bottom: 10px; color: black;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:white;">GO TAXI</h1>', unsafe_allow_html=True)

st.markdown(f'<div class="precio-banner"><span style="color:white;">TARIFA MÍNIMA HOY</span><br><b style="font-size:28px;">Bs. {precio_actual}</b></div>', unsafe_allow_html=True)

if not df.empty:
    # Lógica de mostrar choferes (igual que antes)
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]
    for sec in secciones:
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == sec['key']]
            for _, fila in grupo.iterrows():
                st.markdown(f'<div class="driver-card" style="--status-color: {sec["color"]};"><b>{fila["NOMBRE"]}</b><br>{fila["TELEFONO"]}</div>', unsafe_allow_html=True)
                if sec['key'] != "No Laborando":
                    with st.expander("VER CONTACTO"):
                        st.write(f"Pago: {fila.get('DATOSPAGO', 'No registrado')}")
                        st.link_button("Llamar", f"tel:{fila['TELEFONO']}", use_container_width=True)

# 5. PANEL DE ADMINISTRADOR
st.markdown("---")
with st.expander("🔐 GESTIÓN DE TARIFA"):
    admin_pass = st.text_input("Contraseña", type="password")
    if admin_pass == "Oo27636":
        nuevo_precio = st.number_input("Nuevo precio (Bs.)", min_value=0, value=460)
        if st.button("GUARDAR"):
            try:
                df_upd = pd.DataFrame([["PRECIO_CARRERA", nuevo_precio]], columns=["PARAMETRO", "VALOR"])
                conn.update(spreadsheet=url, worksheet="CONFIG", data=df_upd)
                st.success("¡Guardado! Refresca la app.")
                st.balloons()
            except:
                st.error("Error: Verifica que la pestaña en Excel se llame exactamente CONFIG")
