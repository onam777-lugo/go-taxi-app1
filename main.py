import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

# Variables de respaldo para evitar NameError
df = pd.DataFrame()
precio_actual = "Consultar"

# Conexión
url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. CARGA DE DATOS INTELIGENTE
try:
    # Intentamos cargar la lista de choferes (Sheet1)
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    df.columns = df.columns.str.strip().str.upper()
    
    # Intentamos cargar el precio (CONFIG)
    df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
    df_config.columns = df_config.columns.str.strip().str.upper()
    precio_actual = df_config.iloc[0, 1] # Toma el valor de la segunda columna
except Exception as e:
    st.warning("⚠️ Sincronizando datos con la central...")

# 3. ESTILOS VISUALES
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

st.markdown('<h1 style="text-align:center; color:white; font-weight:900;">GO TAXI</h1>', unsafe_allow_html=True)

# Banner de Tarifa
st.markdown(f'<div class="precio-banner"><span style="color:white;">TARIFA MÍNIMA HOY</span><br><b style="font-size:28px;">Bs. {precio_actual}</b></div>', unsafe_allow_html=True)

# 4. LISTADO DE CHOFERES
if not df.empty and 'ESTATUS' in df.columns:
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]
    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<b style='color: white;'>{sec['label']}</b>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                st.markdown(f'<div class="driver-card" style="--status-color: {sec["color"]};"><b>{fila["NOMBRE"]}</b><br>📱 {fila["TELEFONO"]}</div>', unsafe_allow_html=True)
                if sec['key'] != "No Laborando":
                    with st.expander("VER OPCIONES"):
                        st.write(f"Pago: {fila.get('DATOSPAGO', 'Consultar')}")
                        st.link_button("Llamar", f"tel:{fila['TELEFONO']}", use_container_width=True)
else:
    st.info("Cargando flota de vehículos...")

# 5. PANEL DE ADMINISTRADOR
st.markdown("---")
with st.expander("🔐 GESTIÓN DE TARIFA"):
    admin_pass = st.text_input("Contraseña", type="password")
    if admin_pass == "Oo27636":
        nuevo_precio = st.number_input("Establecer nuevo precio (Bs.)", min_value=0, value=460)
        if st.button("GUARDAR NUEVO PRECIO"):
            try:
                # Actualización forzada a la hoja CONFIG
                df_upd = pd.DataFrame([["PRECIO_CARRERA", nuevo_precio]], columns=["PARAMETRO", "VALOR"])
                conn.update(spreadsheet=url, worksheet="CONFIG", data=df_upd)
                st.success("¡Precio actualizado! Reinicia la app para ver los cambios.")
                st.balloons()
            except Exception as e:
                st.error("Error al guardar. Revisa que el Excel tenga permiso de 'Editor'.")
                
