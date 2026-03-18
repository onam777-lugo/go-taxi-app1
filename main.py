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

# Inicializar el estado para saber qué chofer está expandido
if "chofer_abierto" not in st.session_state:
    st.session_state.chofer_abierto = None

# 2. DISEÑO DE INTERFAZ PREMIUM
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; visibility: hidden !important; }
    
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; font-size: 42px; font-weight: 900; padding-top: 80px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    .tarifa-container {
        background-color: rgba(0, 0, 0, 0.8); color: white; padding: 8px 12px;
        border-radius: 12px; text-align: center; width: 80%; margin: 0 auto 25px auto;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* ESTILO DE BOTÓN-TARJETA (Respetando tu diseño original) */
    div.stButton > button {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0) !important;
        padding: 15px !important;
        border-radius: 15px !important;
        border: none !important;
        border-left: 12px solid var(--status-color) !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        text-align: left !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15) !important;
        color: #1a1a1a !important;
        height: auto !important;
    }

    /* Ajuste para que el texto dentro del botón se vea como el original */
    .driver-btn-content { pointer-events: none; }
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a; display: block; }
    .code-tag { background-color: black; color: #FF8C00; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }
    .phone-text { font-weight: 600; font-size: 14px; color: #444; display: block; margin-top: 4px; }

    /* Ventana de Datos (Modal debajo del botón) */
    .pago-desplegado {
        background-color: #FEE0C0;
        padding: 15px;
        border-radius: 0 0 15px 15px;
        border: 2px solid black;
        border-top: none;
        margin-top: -20px;
        margin-bottom: 20px;
        color: black;
    }

    .install-box {
        background-color: rgba(255,255,255,0.2); border: 1px dashed white;
        padding: 15px; border-radius: 15px; text-align: center; color: white; margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    # Tarifa J1
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "Consultar"
    st.markdown(f"""
        <div class="tarifa-container">
            <p style="margin:0; font-size:10px; font-weight:700; color:#FF8C00; letter-spacing:1px; line-height:1;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:22px; font-weight:900; line-height:1;">Bs. {precio_vuelo}</p>
        </div>
    """, unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px;">🌙 SERVICIO CERRADO (9PM - 6AM)</div>', unsafe_allow_html=True)
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
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Consultar al chofer."
                codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                # Renderizar botón con estilo de tarjeta
                st.markdown(f"<div style='--status-color: {sec['color']};'>", unsafe_allow_html=True)
                # Formato visual del botón (Nombre + Código y Teléfono)
                if st.button(f"👤 {fila['NOMBRE']} #{codigo} \n\n 📱 {telf_fmt}", key=f"btn_{codigo}"):
                    if sec['key'] != "No Laborando":
                        # Si ya estaba abierto, se cierra; si no, se abre
                        st.session_state.chofer_abierto = codigo if st.session_state.chofer_abierto != codigo else None
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

                # Si el chofer está seleccionado, mostrar detalles justo debajo
                if st.session_state.chofer_abierto == codigo:
                    with st.container():
                        st.markdown(f"""
                            <div class="pago-desplegado">
                                <b>💳 PAGO MÓVIL / DATOS:</b><br>
                                <div style="background: rgba(0,0,0,0.05); padding: 10px; border-radius: 8px; margin: 10px 0;">
                                    <b>{pago}</b>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        c1, c2, c3 = st.columns(3)
                        c1.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                        c2.link_button("✅ WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                        if c3.button("❌ CERRAR", key=f"close_{codigo}", use_container_width=True):
                            st.session_state.chofer_abierto = None
                            st.rerun()

    st.markdown("""
        <div class="install-box">
            <p style="margin-bottom: 5px; font-weight: bold;">📲 ¡INSTALA ESTA APP!</p>
            <p style="font-size: 12px;">Toca los <b>3 puntos (⋮)</b> o <b>Compartir</b> y elige<br><b>"Agregar a pantalla de inicio"</b></p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.link_button("📩 CENTRAL DE RECLAMOS", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.markdown("<p style='text-align:center; color:white;'>Sincronizando flota...</p>", unsafe_allow_html=True)
    
