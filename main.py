import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

# Estado para controlar qué ventana de chofer está abierta
if "id_abierto" not in st.session_state:
    st.session_state.id_abierto = None

# 2. DISEÑO DE INTERFAZ (Estética Original Píritu)
st.markdown("""
    <style>
    /* ELIMINAR INTERFAZ DE STREAMLIT */
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    #MainMenu, footer { visibility: hidden; }
    
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Títulos Originales */
    .brand-title { text-align: center; color: white !important; font-size: 42px; font-weight: 900; padding-top: 80px; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Tarifa Pequeña y Transparente */
    .tarifa-box {
        background-color: rgba(0, 0, 0, 0.7); color: white; padding: 8px;
        border-radius: 12px; text-align: center; width: 65%; margin: 0 auto 25px auto;
    }

    /* BOTONES DE CHOFERES (Tamaño uniforme y franja de color) */
    div.stButton > button {
        background-color: #FEE0C0 !important;
        color: black !important;
        border-radius: 15px !important;
        border: none !important;
        border-left: 12px solid var(--col) !important; /* La franja de Estatus */
        padding: 15px !important;
        width: 100% !important; /* Ancho uniforme */
        height: 85px !important; /* Altura uniforme para todos */
        text-align: left !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1) !important;
        display: block !important;
    }

    /* Elementos dentro del botón */
    .driver-name { font-weight: 900; font-size: 19px; color: black; display: inline-block; }
    .code-badge { background-color: black; color: #FF8C00; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-left: 10px; }
    .phone-sub { color: #444; font-size: 14px; font-weight: 700; display: block; margin-top: 5px; }

    /* VENTANA DESPLEGABLE DE DATOS */
    .info-desplegada {
        background-color: #FEE0C0;
        padding: 15px;
        border-radius: 0 0 15px 15px;
        border: 2px solid black;
        border-top: none;
        margin-top: -15px;
        margin-bottom: 20px;
    }

    /* Bloque de Pago Móvil (Oscuro con letras crema) */
    .pago-box {
        background-color: #1a1a1a !important;
        color: #FEE0C0 !important;
        padding: 12px;
        border-radius: 10px;
        font-family: monospace;
        font-size: 14px;
        border: 1px solid #FF8C00;
        margin-top: 10px;
        margin-bottom: 15px;
        white-space: pre-wrap;
    }
    
    .stLinkButton > a { border-radius: 12px !important; font-weight: bold !important; height: 45px !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO ---
st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0)
    
    # Tarifa J1
    precio = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div class="tarifa-box"><p style="margin:0; font-size:10px; color:#FF8C00; font-weight:bold;">TARIFA MÍNIMA</p><p style="margin:0; font-size:22px; font-weight:900;">Bs. {precio}</p></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:10px; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:20px; border:2px solid white;">🌙 SERVICIO CERRADO (9PM - 6AM)</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#777777"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color:white; font-weight:bold; margin-top:10px; margin-bottom:5px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                nombre = fila['NOMBRE']
                pago = str(fila['DATOSPAGO'])
                
                # Renderizado del Botón/Tarjeta con su franja de color
                st.markdown(f"<div style='--col: {sec['color']};'>", unsafe_allow_html=True)
                # Formato: Nombre Negrita + Badge Código / Debajo: Teléfono
                btn_label = f"**{nombre}** #{cod}\n\n📱 +58 {telf}"
                
                if st.button(btn_label, key=f"btn_{cod}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_abierto = cod if st.session_state.id_abierto != cod else None
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

                # VENTANA DESPLEGABLE (Debajo del chofer)
                if st.session_state.id_abierto == cod:
                    with st.container():
                        st.markdown(f"""
                            <div class="info-desplegada">
                                <p style="font-weight:bold; margin:0; font-size:13px; color:black;">💳 PAGO MÓVIL / DATOS:</p>
                                <div class="pago-box">{pago}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns(3)
                        c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                        c2.link_button("✅ WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)
                        if c3.button("❌ CERRAR", key=f"close_{cod}", use_container_width=True):
                            st.session_state.id_abierto = None
                            st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.info("Sincronizando flota de GO TAXI...")
    
