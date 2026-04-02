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

# 2. DISEÑO DE INTERFAZ PREMIUM (VERSIÓN BLINDADA)
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader {
        display: none !important;
        visibility: hidden !important;
    }
    
    .stApp {
        background-color: #FF8C00;
        margin-top: -30px !important;
    }

    #MainMenu, footer { visibility: hidden; }
    
    .block-container { 
        padding-top: 1rem !important; 
        max-width: 450px !important; 
        padding-bottom: 5rem !important; /* Espacio extra al final */
    }

    .brand-title { 
        text-align: center; 
        color: white !important; 
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4); 
        margin-bottom: -10px; 
        font-size: 42px; 
        font-weight: 900; 
        padding-top: 80px;
    }
    .brand-subtitle { 
        text-align: center; 
        color: black !important; 
        font-weight: 800; 
        font-size: 14px; 
        letter-spacing: 2px; 
        margin-bottom: 25px; 
    }

    .tarifa-container {
        background-color: rgba(0, 0, 0, 0.5); 
        color: white; 
        padding: 8px 12px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 25px; 
        border: 1px solid rgba(255,255,255,0.1);
        width: 60%; 
        margin-left: auto; 
        margin-right: auto;
    }

    /* ESTILO DE TARJETAS CON BARRA DINÁMICA */
    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 0px !important; 
        border-radius: 15px; 
        margin-bottom: 15px; 
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
        display: flex;
        overflow: hidden;
        border: none !important;
        position: relative;
        z-index: 5; /* Asegura que cubra al expander */
    }
    
    .status-bar {
        width: 14px; 
        min-height: 100%;
    }

    .card-info {
        padding: 15px;
        flex-grow: 1;
    }
    
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }
    .code-tag { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }
    
    /* CORRECCIÓN FINAL DE LAS ESQUINAS Y BORDES */
    .stExpander { 
        background-color: #FEE0C0 !important; 
        border: none !important; 
        border-radius: 0 0 15px 15px !important; 
        margin-top: -26px !important; /* Solape perfecto */
        margin-bottom: 20px; 
        margin-left: 6px !important; 
        margin-right: 6px !important;
        z-index: 1;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    .stExpander details, .stExpander [data-testid="stExpanderDetails"] { 
        border: none !important; 
        padding: 0px !important;
    }

    .stExpander p { color: #FF8C00 !important; font-weight: 800 !important; text-transform: uppercase; margin-top: 5px; }
    .stExpander svg { fill: #FF8C00 !important; }
    
    .stButton>button { border-radius: 12px !important; height: 50px !important; font-weight: 700 !important; text-transform: uppercase; }
    
    .install-box {
        background-color: rgba(255,255,255,0.2); border: 1px dashed white;
        padding: 15px; border-radius: 15px; text-align: center; color: white; margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">¡Go! TAXI</h1><p class="brand-subtitle">TU RUTA SEGURA EN PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    # Obtener tarifa (Asumiendo que está en la columna J/9)
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "---"

    st.markdown(f'<div class="tarifa-container"><p style="margin:0; font-size:10px; font-weight:700; color:#FF8C00; letter-spacing:1px; line-height:1;">TARIFA MÍNIMA HOY</p><p style="margin:0; font-size:22px; font-weight:900; line-height:1;">Bs. {precio_vuelo}</p></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 22 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px;">🌙 SERVICIO CERRADO (9PM - 6AM)</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    # --- CONFIGURACIÓN DE COLORES DINÁMICOS ---
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},   
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},       
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"} 
    ]

    for sec in secciones:
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == sec['key']]
            if not grupo.empty:
                st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 5px; margin-bottom: 8px;'>{sec['label']}</p>", unsafe_allow_html=True)
                
                for _, fila in grupo.iterrows():
                    # Limpieza de teléfono para que el botón de llamada sea infalible
                    telf_raw = str(fila['TELEFONO']).split('.')[0].replace(" ", "").replace("-", "")
                    telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                    pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Consultar al chofer."
                    codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                    bloquear = (sec['key'] == "No Laborando")

                    # ESTRUCTURA DE TARJETA CON BARRA DE COLOR
                    st.markdown(f"""
                        <div class="driver-card">
                            <div class="status-bar" style="background-color: {sec['color']};"></div>
                            <div class="card-info">
                                <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{codigo}</span></span>
                                <span style="color:#444; font-weight:600;">📱 {telf_fmt}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    if not bloquear:
                        with st.expander("VER DATOS"):
                            st.markdown("**💳 PAGO MÓVIL / DATOS:**")
                            st.code(pago, language=None) 
                            c1, c2 = st.columns(2)
                            with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                            with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)

    # Footer de instalación y reclamos
    st.markdown('<div class="install-box"><p style="margin-bottom: 5px; font-weight: bold;">📲 ¡INSTALA ESTA APP!</p><p style="font-size: 12px;">Toca los <b>3 puntos (⋮)</b> o <b>Compartir</b> y elige<br><b>"Agregar a pantalla de inicio"</b></p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("📩 CENTRAL DE RECLAMOS", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    # Error amigable si el Excel no carga
    st.markdown("<p style='text-align:center; color:white; font-weight:bold;'>Sincronizando flota... Por favor espera.</p>", unsafe_allow_html=True)
                    
