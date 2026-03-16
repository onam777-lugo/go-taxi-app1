import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(
    page_title="GO TAXI", 
    page_icon="logo.jpeg", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. DISEÑO DE INTERFAZ PREMIUM Y ELIMINACIÓN DE BARRA BLANCA
st.markdown("""
    <style>
    /* Ocultar barra blanca superior y elementos de Streamlit */
    header, [data-testid="stHeader"], .stAppHeader {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Eliminar espacio en blanco superior */
    .stApp {
        background-color: #FF8C00;
        margin-top: -60px !important;
    }

    /* Ocultar menú y footer */
    #MainMenu, footer { visibility: hidden; }
    
    .block-container { 
        padding-top: 0rem !important; 
        max-width: 450px !important; 
    }

    /* Estilo de Títulos */
    .brand-title { 
        text-align: center; 
        color: white !important; 
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4); 
        margin-bottom: -10px; 
        font-size: 42px; 
        font-weight: 900; 
        padding-top: 40px;
    }
    .brand-subtitle { 
        text-align: center; 
        color: black !important; 
        font-weight: 800; 
        font-size: 14px; 
        letter-spacing: 2px; 
        margin-bottom: 25px; 
    }

    /* Banner de Tarifa */
    .tarifa-container {
        background-color: black; color: white; padding: 12px; border-radius: 15px;
        text-align: center; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.2);
    }

    /* Tarjetas de Choferes */
    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 15px; border-radius: 15px; border-left: 12px solid var(--status-color);
        margin-bottom: 15px; box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
    }
    
    .has-expander { border-radius: 15px 15px 0 0 !important; margin-bottom: -5px !important; }
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }
    .code-tag { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }
    
    .stExpander { background-color: #FEE0C0 !important; border: none !important; border-radius: 0 0 15px 15px !important; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Títulos Principales
st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU</p>', unsafe_allow_html=True)

try:
    # Conexión silenciosa
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    
    # Lectura de datos
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0) 
    
    # Tarifa desde el encabezado J (Columna 10)
    try:
        precio_hoy = df.columns[9] if len(df.columns) > 9 else "Consultar"
    except:
        precio_hoy = "Consultar"

    st.markdown(f"""
        <div class="tarifa-container">
            <p style="margin:0; font-size:11px; font-weight:700; color:#FF8C00; letter-spacing:1px;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:26px; font-weight:900;">Bs. {precio_hoy}</p>
        </div>
    """, unsafe_allow_html=True)

    # Lógica de Choferes
    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.error("🌙 SERVICIO CERRADO (9PM - 6AM)")
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == sec['key']]
            if not grupo.empty:
                st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 5px;'>{sec['label']}</p>", unsafe_allow_html=True)
                for _, fila in grupo.iterrows():
                    telf = str(fila['TELEFONO']).split('.')[0]
                    cod = str(fila['CODIGO']).split('.')[0]
                    
                    st.markdown(f"""
                        <div class="driver-card {'has-expander' if sec['key'] != 'No Laborando' else ''}" style="--status-color: {sec['color']};">
                            <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></span>
                            <span style="color:#444; font-weight:600;">📱 +58 {telf}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    if sec['key'] != "No Laborando":
                        with st.expander("VER OPCIONES"):
                            st.code(fila.get('DATOSPAGO', 'Consultar'), language=None)
                            c1, c2 = st.columns(2)
                            c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                            c2.link_button("WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)

except Exception as e:
    # Mensaje de carga discreto si algo falla temporalmente
    st.markdown("<p style='text-align:center; color:white; font-size:12px;'>Actualizando conexión con la flota...</p>", unsafe_allow_html=True)
