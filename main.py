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

# 2. ESTILOS BASE (ESTÁTICOS)
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; padding-bottom: 5rem !important; }
    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; font-size: 42px; font-weight: 900; padding-top: 80px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }
    
    /* Contenedor de Tarjeta */
    .driver-card {
        padding: 0px !important; 
        border-radius: 15px 15px 0 0 !important; 
        margin-bottom: 0px !important; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        display: flex;
        overflow: hidden;
        position: relative;
    }
    .status-bar { width: 14px; min-height: 100%; }
    .card-info { padding: 15px; flex-grow: 1; }
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }
    .code-tag { background-color: black; color: white !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }

    /* Expander como base redondeada */
    .stExpander { 
        border: none !important; 
        border-radius: 0 0 15px 15px !important; 
        margin-top: 0px !important;
        margin-bottom: 20px !important;
        overflow: hidden !important;
    }
    .stExpander details { border: none !important; }
    .stExpander summary { padding-top: 10px !important; }
    .stButton>button { border-radius: 12px !important; height: 50px !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">¡Go! TAXI</h1><p class="brand-subtitle">TU RUTA SEGURA EN PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    df.columns = df.columns.str.strip().str.upper()
    
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 22 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px;">🌙 SERVICIO CERRADO (10PM - 6AM)</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    # --- CONFIGURACIÓN DE COLORES DINÁMICOS POR ESTATUS ---
    # bg: fondo tarjeta | bar: barra lateral | shadow: fondo del botón (tu "sombra")
    config_estatus = {
        "Disponible": {"bg": "#E8F5E9", "bar": "#28a745", "shadow": "#C8E6C9", "text": "#1B5E20"},
        "Ocupado": {"bg": "#FFFDE7", "bar": "#f1c40f", "shadow": "#FFF9C4", "text": "#F57F17"},
        "No Laborando": {"bg": "#FFEBEE", "bar": "#dc3545", "shadow": "#FFCDD2", "text": "#B71C1C"}
    }

    for key, colores in config_estatus.items():
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == key]
            if not grupo.empty:
                st.markdown(f"<p style='color: white; font-weight: 800; margin-bottom: 8px;'>{key.upper()}</p>", unsafe_allow_html=True)
                
                for _, fila in grupo.iterrows():
                    telf_raw = str(fila['TELEFONO']).split('.')[0].replace(" ", "").replace("-", "")
                    codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"
                    
                    # APLICAMOS EL COLOR DINÁMICO AQUÍ
                    st.markdown(f"""
                        <style>
                        /* Generamos un ID único o usamos clases combinadas para el color */
                        div[data-testid="stExpander"]:has(summary:contains("VER DATOS")) {{
                            background-color: {colores['shadow']} !important;
                        }}
                        </style>
                        <div class="driver-card" style="background-color: {colores['bg']};">
                            <div class="status-bar" style="background-color: {colores['bar']};"></div>
                            <div class="card-info">
                                <span class="name-text" style="color: {colores['text']} !important;">{fila['NOMBRE']} <span class="code-tag">#{codigo}</span></span>
                                <span style="color:#444; font-weight:600;">📱 +58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if key != "No Laborando":
                        with st.expander("VER DATOS"):
                            st.markdown(f"<b style='color:{colores['text']}'>💳 PAGO MÓVIL / DATOS:</b>", unsafe_allow_html=True)
                            st.code(fila['DATOSPAGO'], language=None) 
                            c1, c2 = st.columns(2)
                            with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                            with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                    else:
                        st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    
