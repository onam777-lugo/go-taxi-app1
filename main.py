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

# --- AJUSTE DE TRANSPARENCIA ---
opacidad = 0.85 

# 2. ESTILOS BASE (DISEÑO CURVO Y BICOLOR)
st.markdown(f"""
    <style>
    header, [data-testid="stHeader"], .stAppHeader {{ display: none !important; }}
    
    /* Fondo General Crema */
    .stApp {{ 
        background-color: #FFFDF5 !important; 
    }}

    /* Cabecera Naranja con Curva */
    .header-curva {{
        background-color: #FF8C00;
        height: 280px;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 0;
        /* Crea la forma curva en la base */
        clip-path: ellipse(120% 60% at 50% 40%);
    }}

    .block-container {{ 
        padding-top: 0rem !important; 
        max-width: 450px !important; 
        padding-bottom: 5rem !important; 
        z-index: 1;
        position: relative;
    }}
    
    /* Logo estilo Imagen de Referencia */
    .logo-container {{ text-align: center; padding-top: 60px; margin-bottom: 0px; }}
    .go-text {{ color: white; font-size: 55px; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); }}
    .taxi-text {{ background-color: black; color: white; padding: 2px 12px; border-radius: 10px; font-size: 42px; font-weight: 900; margin-left: 8px; vertical-align: middle; }}
    .brand-subtitle {{ text-align: center; color: black !important; font-weight: 800; font-size: 13px; letter-spacing: 2px; margin-top: -5px; margin-bottom: 35px; }}
    
    /* Tarjeta de Tarifa Blanca con Sombra */
    .tarifa-container {{
        background-color: white; 
        padding: 15px; border-radius: 20px; text-align: center; 
        margin-bottom: 30px; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
        width: 90%; margin-left: auto; margin-right: auto;
        border: 1px solid rgba(0,0,0,0.05);
    }}

    /* Tarjetas de Choferes */
    .driver-card {{
        padding: 0px !important; 
        border-radius: 15px !important; 
        margin-bottom: 0px !important; 
        box-shadow: 0px 8px 16px rgba(0,0,0,0.08); 
        display: flex;
        overflow: hidden;
        position: relative;
        z-index: 2;
        border: 1px solid rgba(0,0,0,0.03);
    }}
    .status-bar {{ width: 14px; min-height: 100%; }}
    .card-info {{ padding: 15px; flex-grow: 1; }}
    .name-text {{ font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }}
    .code-tag {{ background-color: black; color: white !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }}

    /* Flecha a la derecha */
    .stExpander summary {{
        display: flex !important;
        flex-direction: row-reverse !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding-right: 20px !important;
        color: #555 !important;
        font-weight: 700 !important;
    }}
    
    .stExpander {{ 
        border: none !important; 
        border-radius: 15px !important; 
        margin-top: -12px !important; 
        margin-bottom: 25px !important;
        overflow: hidden !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }}

    /* Títulos de sección en negro para que resalten en el crema */
    .section-title {{
        color: #333 !important;
        font-weight: 800;
        margin-bottom: 10px;
        margin-top: 10px;
        font-size: 14px;
        letter-spacing: 1px;
    }}
    
    .install-box {{
        background-color: white; border: 1px dashed #FF8C00;
        padding: 15px; border-radius: 15px; text-align: center; color: #555; margin-top: 30px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

# Div para la curva naranja de fondo
st.markdown('<div class="header-curva"></div>', unsafe_allow_html=True)

# Encabezado con Logo
st.markdown('<div class="logo-container"><span class="go-text">¡Go!</span><span class="taxi-text">TAXI</span></div>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">TU RUTA SEGURA EN PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "---"
    
    # Tarjeta de Tarifa (Actúa como puente)
    st.markdown(f"""
        <div class="tarifa-container">
            <p style="margin:0; font-size:11px; font-weight:800; color:#888; letter-spacing:1px;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:36px; font-weight: 900; color:#1a1a1a;">Bs. {precio_vuelo}</p>
        </div>
    """, unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 22 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px;">🌙 SERVICIO CERRADO (10PM - 6AM)</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    config_estatus = {
        "Disponible": {"bg": "white", "bar": "#28a745", "shadow": "#F0FFF0", "text": "#1B5E20", "emoji": "🟢"},
        "Ocupado": {"bg": "white", "bar": "#f1c40f", "shadow": "#FFFFF0", "text": "#F57F17", "emoji": "🟡"},
        "No Laborando": {"bg": "white", "bar": "#dc3545", "shadow": "#FFF5F5", "text": "#B71C1C", "emoji": "🔴"}
    }

    for key, colores in config_estatus.items():
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == key]
            if not grupo.empty:
                st.markdown(f"<p class='section-title'>{colores['emoji']} {key.upper()}</p>", unsafe_allow_html=True)
                
                for _, fila in grupo.iterrows():
                    telf_raw = str(fila['TELEFONO']).split('.')[0].replace(" ", "").replace("-", "")
                    codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"
                    
                    st.markdown(f"""
                        <style>
                        div[data-testid="stExpander"]:has(summary:contains("VER DATOS")) {{
                            background-color: {colores['shadow']} !important;
                        }}
                        </style>
                        <div class="driver-card" style="background-color: {colores['bg']};">
                            <div class="status-bar" style="background-color: {colores['bar']};"></div>
                            <div class="card-info">
                                <span class="name-text" style="color: #1a1a1a !important;">{fila['NOMBRE']} <span class="code-tag">#{codigo}</span></span>
                                <span style="color:#666; font-weight:600; font-size: 14px;">📱 +58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if key != "No Laborando":
                        with st.expander("VER DATOS"):
                            st.markdown(f"<b style='color:#333'>💳 PAGO MÓVIL / DATOS:</b>", unsafe_allow_html=True)
                            st.code(fila['DATOSPAGO'], language=None) 
                            c1, c2 = st.columns(2)
                            with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                            with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                    else:
                        st.markdown("<div style='margin-bottom:25px;'></div>", unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="install-box"><p style="margin-bottom: 5px; font-weight: bold; color:#FF8C00;">📲 ¡INSTALA ESTA APP!</p><p style="font-size: 12px;">Toca los <b>3 puntos (⋮)</b> o <b>Compartir</b> y elige<br><b>"Agregar a pantalla de inicio"</b></p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("📩 CENTRAL DE RECLAMOS", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.markdown("<p style='text-align:center; color:#555; font-weight:bold;'>Sincronizando flota... Por favor espera.</p>", unsafe_allow_html=True)
    
