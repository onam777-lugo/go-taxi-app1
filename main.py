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

# 2. DISEÑO DE INTERFAZ (Estilo Original Recuperado)
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    
    /* Títulos Originales */
    .brand-title { text-align: center; color: white !important; font-size: 42px; font-weight: 900; padding-top: 80px; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Tarifa Transparente */
    .tarifa-box {
        background-color: rgba(0, 0, 0, 0.7); color: white; padding: 8px;
        border-radius: 12px; text-align: center; width: 65%; margin: 0 auto 25px auto;
    }

    /* Tarjetas Tipo Botón (Crema Original) */
    div.stButton > button {
        background-color: #FEE0C0 !important;
        color: black !important;
        border-radius: 15px !important;
        border: none !important;
        border-left: 12px solid var(--col) !important;
        padding: 10px 15px !important;
        width: 100% !important;
        text-align: left !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1) !important;
    }

    /* Elementos dentro de la tarjeta */
    .driver-name { font-weight: 900; font-size: 18px; color: black; }
    .code-badge { background-color: black; color: #FF8C00; padding: 2px 6px; border-radius: 5px; font-size: 12px; margin-left: 8px; vertical-align: middle; }
    .phone-sub { color: #444; font-size: 14px; font-weight: 600; display: block; margin-top: 2px; }

    /* Ventana de Datos Desplegada */
    .info-desplegada {
        background-color: #FEE0C0;
        padding: 15px;
        border-radius: 0 0 15px 15px;
        border: 2px solid black;
        border-top: none;
        margin-top: -15px;
        margin-bottom: 20px;
        color: black;
    }
    
    .stLinkButton > a { border-radius: 10px !important; font-weight: bold !important; }
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
    st.markdown(f'<div class="tarifa-box"><p style="margin:0; font-size:10px; color:#FF8C00;">TARIFA MÍNIMA</p><p style="margin:0; font-size:22px; font-weight:900;">Bs. {precio}</p></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:10px; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:20px;">🌙 SERVICIO CERRADO</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#777777"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color:white; font-weight:bold; margin-bottom:5px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                nombre = fila['NOMBRE']
                pago = str(fila['DATOSPAGO'])
                
                # Renderizado de la Tarjeta
                st.markdown(f"<div style='--col: {sec['color']};'>", unsafe_allow_html=True)
                # El botón ahora cambia el estado para abrir/cerrar la ventana del chofer específico
                if st.button(f"👤 **{nombre}** #{cod}\n\n📱 +58 {telf}", key=f"btn_{cod}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_abierto = cod if st.session_state.id_abierto != cod else None
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

                # VENTANA DESPLEGABLE (Solo si este chofer es el seleccionado)
                if st.session_state.id_abierto == cod:
                    st.markdown(f"""
                        <div class="info-desplegada">
                            <p style="font-weight:bold; margin-bottom:5px; font-size:14px;">💳 DATOS DE PAGO:</p>
                            <div style="background:rgba(0,0,0,0.05); padding:8px; border-radius:8px; font-size:13px; margin-bottom:15px;">{pago}</div>
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
    st.info("Sincronizando flota de Píritu...")
    
