import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

# CONEXIÓN
url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# VARIABLES POR DEFECTO
df = pd.DataFrame()
precio_actual = "465" # Valor por si falla la conexión inicial

# CARGA DE DATOS
try:
    # Carga Choferes
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    df.columns = df.columns.str.strip().str.upper()
    
    # Carga Precio (Hoja CONFIG)
    df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
    precio_actual = str(df_config.iloc[0, 1])
except Exception:
    st.warning("⚠️ Sincronizando con la central de Píritu...")

# DISEÑO
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

# BANNER DE TARIFA
st.markdown(f'<div class="precio-banner"><span style="color:white;">TARIFA MÍNIMA HOY</span><br><b style="font-size:28px;">Bs. {precio_actual}</b></div>', unsafe_allow_html=True)

# MOSTRAR CHOFERES
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
                        st.code(fila.get('DATOSPAGO', 'Consultar pago al chofer'), language=None)
                        st.link_button("Llamar", f"tel:{fila['TELEFONO']}", use_container_width=True)
else:
    st.info("Cargando flota de vehículos... Si no carga, verifica el nombre 'Sheet1' en tu Excel.")

# ADMINISTRACIÓN
st.markdown("---")
with st.expander("🔐 GESTIÓN DE TARIFA"):
    admin_pass = st.text_input("Contraseña", type="password")
    if admin_pass == "Oo27636":
        nuevo_precio = st.number_input("Nuevo precio (Bs.)", min_value=0, value=465)
        if st.button("GUARDAR NUEVO PRECIO"):
            try:
                # Creamos el dato para actualizar
                upd_df = pd.DataFrame([["PRECIO_CARRERA", nuevo_precio]], columns=["PARAMETRO", "VALOR"])
                conn.update(spreadsheet=url, worksheet="CONFIG", data=upd_df)
                st.success("¡Precio actualizado! Refresca la app.")
                st.balloons()
            except Exception:
                st.error("Error al guardar. RECUERDA: En el botón azul 'Compartir' del Excel, debes poner 'Cualquier persona con el enlace' como EDITOR.")
                
