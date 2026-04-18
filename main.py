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

# 2. ESTILOS BASE (LOGO GRANDE Y PERSONALIZABLE)
st.markdown(f"""
    <style>
    header, [data-testid="stHeader"], .stAppHeader {{ display: none !important; }}
    
    .stApp {{ background-color: #FFFDF5 !important; }}

    .header-curva {{
        background-color: #FF8C00;
        height: 320px; /* Aumentado para dar espacio al logo grande */
        position: absolute;
        top: 0; left: 0; width: 100%;
        z-index: 0;
        clip-path: ellipse(120% 60% at 50% 40%);
    }}

    .block-container {{ 
        padding-top: 0rem !important; 
        max-width: 450px !important; 
        z-index: 1;
        position: relative;
    }}
    
    /* --- SECCIÓN DEL LOGO --- */
    .logo-container-stacked {{ 
        text-align: center; 
        padding-top: 40px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}

    .go-line {{ 
        color: white; 
        font-size: 110px; /* <--- AQUÍ CAMBIAS EL TAMAÑO DEL ¡Go! */
        font-weight: 900; 
        text-shadow: 4px 4px 8px rgba(0,0,0,0.3);
        margin-bottom: -25px; 
        line-height: 1;
    }}

    .taxi-box {{ 
        background-color: black; 
        color: white; 
        /* AJUSTE DE TAMAÑO DE LA ETIQUETA NEGRA: */
        padding: 2px 18px;  /* 1er num: alto / 2do num: ancho */
        font-size: 32px;    /* Tamaño de la letra TAXI */
        
        border-radius: 0px 12px 12px 12px; /* Esquina superior izq cuadrada */
        font-weight: 800; 
        text-transform: uppercase;
        letter-spacing: 2px;
        display: inline-block;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.2);
    }}
    
    .brand-subtitle {{ 
        text-align: center; 
        color: black !important; 
        font-weight: 800; 
        font-size: 14px; 
        letter-spacing: 3px; 
        margin-top: 15px; 
        margin-bottom: 25px; 
    }}
    
    /* Estilos de Tarjetas */
    .tarifa-container {{
        background-color: white; padding: 15px; border-radius: 20px; text-align: center; 
        margin-bottom: 30px; box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
        width: 90%; margin-left: auto; margin-right: auto;
    }}

    .driver-card {{
        padding: 0px; border-radius: 15px; display: flex;
        overflow: hidden; border: 1px solid rgba(0,0,0,0.03);
        background-color: white;
    }}
    .status-bar {{ width: 14px; min-height: 100%; }}
    .card-info {{ padding: 15px; flex-grow: 1; }}
    .name-text {{ font-weight: 800; font-size: 20px; color: #1a1a1a !important; }}
    .code-tag {{ background-color: black; color: white !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; margin-left: 5px; }}

    .stExpander {{ border: none !important; border-radius: 15px !important; margin-top: -12px !important; margin-bottom: 25px !important; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-curva"></div>', unsafe_allow_html=True)

# Logo con ¡Go! Gigante
st.markdown("""
    <div class="logo-container-stacked">
        <div class="go-line">¡Go!</div>
        <div class="taxi-line">
            <span class="taxi-box">TAXI</span>
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">TU RUTA SEGURA EN PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "---"
    
    st.markdown(f"""
        <div class="tarifa-container">
            <p style="margin:0; font-size:11px; font-weight:800; color:#888; letter-spacing:1px;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:36px; font-weight: 900; color:#1a1a1a;">Bs. {precio_vuelo}</p>
        </div>
    """, unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 22 or datetime.now(tz).hour < 6

    config_estatus = {
        "Disponible": {"bar": "#28a745", "emoji": "🟢"},
        "Ocupado": {"bar": "#f1c40f", "emoji": "🟡"},
        "No Laborando": {"bar": "#dc3545", "emoji": "🔴"}
    }

    for key, colores in config_estatus.items():
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == key]
            if not grupo.empty:
                st.markdown(f"<p style='font-weight:800; font-size:14px; margin-left:10px;'>{colores['emoji']} {key.upper()}</p>", unsafe_allow_html=True)
                for _, fila in grupo.iterrows():
                    telf_raw = str(fila['TELEFONO']).split('.')[0].replace(" ", "").replace("-", "")
                    codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"
                    
                    st.markdown(f"""
                        <div class="driver-card">
                            <div class="status-bar" style="background-color: {colores['bar']};"></div>
                            <div class="card-info">
                                <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{codigo}</span></span><br>
                                <span style="color:#666; font-weight:600; font-size: 14px;">📱 +58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("VER DATOS"):
                        st.code(fila['DATOSPAGO'], language=None) 
                        c1, c2 = st.columns(2)
                        with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                        with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)

except Exception as e:
    st.error("Error al cargar datos")
    
