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

# 2. DISEÑO DE INTERFAZ PREMIUM
st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; font-size: 42px; font-weight: 900; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Estilo para el pequeño banner de tarifa */
    .tarifa-mini-box {
        background-color: black;
        color: white;
        padding: 10px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 15px;
        border-radius: 15px;
        border-left: 12px solid var(--status-color);
        margin-bottom: 15px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
    }
    
    .has-expander { border-radius: 15px 15px 0 0 !important; margin-bottom: -5px !important; }
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }
    .code-tag { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; vertical-align: middle; }
    .phone-text { font-weight: 600; font-size: 14px; color: #444 !important; display: block; margin-top: 4px; }

    .stExpander {
        background-color: #FEE0C0 !important;
        border: none !important;
        border-radius: 0 0 15px 15px !important;
        margin-bottom: 20px;
    }
    
    .stButton>button { 
        border-radius: 12px !important; 
        height: 50px !important; 
        font-weight: 700 !important; 
        text-transform: uppercase;
        border: none !important;
    }
    
    .install-box {
        background-color: rgba(255,255,255,0.2);
        border: 1px dashed white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado
st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU</p>', unsafe_allow_html=True)

# Lógica de Horario Venezuela
tz = pytz.timezone('America/Caracas')
hora_actual = datetime.now(tz).hour
es_horario_nocturno = hora_actual >= 21 or hora_actual < 6

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    
    # --- CARGA DE TARIFA (Hoja CONFIG) ---
    try:
        df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
        tarifa_hoy = str(df_config.iloc[0, 1])
    except:
        tarifa_hoy = "Consultar"

    # Mostrar la tarifa justo aquí
    st.markdown(f"""
        <div class="tarifa-mini-box">
            <span style="font-size: 11px; color: #FF8C00; font-weight: bold;">TARIFA MÍNIMA HOY</span><br>
            <span style="font-size: 22px; font-weight: 900;">Bs. {tarifa_hoy}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- CARGA DE CHOFERES (Sheet1) ---
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0) 
    df.columns = df.columns.str.strip().str.upper()

    if es_horario_nocturno:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px;">🌙 SERVICIO CERRADO<br>Abrimos de 6:00 AM a 9:00 PM</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 5px; margin-bottom: 8px;'>{sec['label']}</p>", unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Sin datos registrados."
                codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                bloquear = (sec['key'] == "No Laborando")
                clase_tarjeta = "driver-card has-expander" if not bloquear else "driver-card"

                st.markdown(f"""
                    <div class="{clase_tarjeta}" style="--status-color: {sec['color']};">
                        <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{codigo}</span></span>
                        <span class="phone-text">📱 {telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                if not bloquear:
                    with st.expander("VER OPCIONES DE VIAJE"):
                        st.markdown("**💳 PAGO MÓVIL / DATOS:**")
                        st.code(pago, language=None) 
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                        with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)

    st.markdown("""
        <div class="install-box">
            <p style="margin-bottom: 5px; font-weight: bold;">📲 ¡INSTALA ESTA APP!</p>
            <p style="font-size: 12px;">Toca los <b>3 puntos (⋮)</b> o <b>Compartir</b> y elige<br><b>"Agregar a pantalla de inicio"</b></p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.link_button("📩 CENTRAL DE RECLAMOS", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.error("Sincronizando flota...")
