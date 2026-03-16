import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(
    page_title="GO TAXI", 
    page_icon="logo.jpg", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Conexión a Google Sheets
url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. CARGA DE DATOS (Choferes y Precio)
try:
    # Leemos la lista de choferes
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    df.columns = df.columns.str.strip().str.upper()
    
    # Leemos la configuración del precio
    df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
    precio_actual = df_config.loc[df_config['PARAMETRO'] == 'PRECIO_CARRERA', 'VALOR'].values[0]
except Exception:
    precio_actual = "Consultar"

# 3. DISEÑO PREMIUM
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FF8C00; }}
    .precio-banner {{
        background-color: black;
        color: #FF8C00 !important;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .precio-monto {{ font-size: 28px; font-weight: 900; display: block; }}
    .driver-card {{ background: linear-gradient(145deg, #FEE0C0, #f7d4b0); padding: 15px; border-radius: 15px; border-left: 12px solid var(--status-color); margin-bottom: 15px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">GO TAXI</h1>', unsafe_allow_html=True)

# Banner de Tarifa
st.markdown(f"""
    <div class="precio-banner">
        <span style="font-size:14px; font-weight:bold; color:white;">TARIFA MÍNIMA HOY</span>
        <span class="precio-monto">Bs. {precio_actual}</span>
    </div>
    """, unsafe_allow_html=True)

# 4. LÓGICA DE HORARIO Y LISTADO (Lo que ya funcionaba)
tz = pytz.timezone('America/Caracas')
hora_actual = datetime.now(tz).hour
es_horario_nocturno = hora_actual >= 21 or hora_actual < 6

if es_horario_nocturno:
    st.error("🌙 HORARIO NOCTURNO - Servicio activo desde las 6:00 AM")
    df['ESTATUS'] = 'No Laborando'

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
            with st.container():
                st.markdown(f'<div class="driver-card" style="--status-color: {sec["color"]};"><b>{fila["NOMBRE"]}</b><br><small>📱 {fila["TELEFONO"]}</small></div>', unsafe_allow_html=True)
                if sec['key'] != "No Laborando":
                    with st.expander("VER OPCIONES"):
                        st.code(fila['DATOSPAGO'], language=None)
                        st.link_button("Llamar", f"tel:{fila['TELEFONO']}", use_container_width=True)

# 5. PANEL DE ADMINISTRADOR (OCULTO)
st.markdown("---")
with st.expander("🔐 GESTIÓN DE TARIFA"):
    admin_pass = st.text_input("Contraseña de acceso", type="password")
    if admin_pass == "Oo27636":
        nuevo_precio = st.number_input("Establecer nuevo precio (Bs.)", min_value=0, value=int(precio_actual) if str(precio_actual).isdigit() else 0)
        if st.button("GUARDAR NUEVO PRECIO"):
            try:
                # Actualizamos la hoja CONFIG
                df_upd = pd.DataFrame([["PRECIO_CARRERA", nuevo_precio]], columns=["PARAMETRO", "VALOR"])
                conn.update(spreadsheet=url, worksheet="CONFIG", data=df_upd)
                st.success("Precio actualizado correctamente.")
                st.balloons()
            except Exception as e:
                st.error("Error al actualizar. Verifica los permisos del Excel.")

st.markdown('<p style="text-align:center; color:white; font-size:10px;">Instala esta app tocando los 3 puntos y "Agregar a inicio"</p>', unsafe_allow_html=True)
