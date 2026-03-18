import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

if "id_abierto" not in st.session_state:
    st.session_state.id_abierto = None

# 2. DISEÑO DE INTERFAZ (Respetando cada componente original)
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Títulos Originales */
    .brand-title { text-align: center; color: white !important; font-size: 42px; font-weight: 900; padding-top: 80px; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Tarifa */
    .tarifa-box { background-color: rgba(0, 0, 0, 0.8); color: white; padding: 10px; border-radius: 12px; text-align: center; width: 80%; margin: 0 auto 20px auto; }

    /* DISEÑO DE LA TARJETA (Botón Invisible sobre la Casilla) */
    .driver-container { position: relative; margin-bottom: 5px !important; } /* Distancia corta amarilla */
    
    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 15px; border-radius: 15px; 
        border-left: 15px solid var(--status-color); /* Franja azul marcada */
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
        display: block;
    }

    /* Código con fondo negro y letras crema */
    .code-tag {
        background-color: black; color: #FEE0C0; 
        padding: 2px 8px; border-radius: 6px; 
        font-size: 11px; font-weight: bold; margin-left: 8px;
    }

    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a; }
    .phone-text { color: #444; font-weight: 600; font-size: 14px; display: block; margin-top: 5px; }

    /* Hacer que el botón de Streamlit sea invisible pero cubra toda la tarjeta */
    div.stButton > button {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: transparent !important; border: none !important; color: transparent !important;
        z-index: 10;
    }
    div.stButton > button:hover { background: rgba(0,0,0,0.05) !important; }

    /* Ventana de Datos Desplegada */
    .info-desplegada {
        background-color: #FEE0C0; padding: 15px; border-radius: 0 0 15px 15px;
        border: 2px solid black; border-top: none; margin-top: -5px; margin-bottom: 15px; color: black;
    }

    .install-box { background-color: rgba(255,255,255,0.2); border: 1px dashed white; padding: 15px; border-radius: 15px; text-align: center; color: white; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0)
    
    precio = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div class="tarifa-box"><p style="margin:0; font-size:10px; color:#FF8C00; font-weight:bold;">TARIFA MÍNIMA HOY</p><p style="margin:0; font-size:24px; font-weight:900;">Bs. {precio}</p></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

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
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                
                # --- LA TARJETA VISUAL ---
                st.markdown(f"""
                <div class="driver-container" style="--status-color: {sec['color']};">
                    <div class="driver-card">
                        <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></span>
                        <span class="phone-text">📱 +58 {telf[0:3]} {telf[3:6]} {telf[6:]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- EL BOTÓN INVISIBLE (Encima de la tarjeta) ---
                if st.button("", key=f"btn_{cod}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_abierto = cod if st.session_state.id_abierto != cod else None
                        st.rerun()

                # --- VENTANA DE DATOS ---
                if st.session_state.id_abierto == cod:
                    st.markdown(f"""
                        <div class="info-desplegada">
                            <p style="font-weight:900; margin-bottom:5px;">💳 DATOS DE PAGO:</p>
                            <div style="background:rgba(0,0,0,0.1); padding:10px; border-radius:8px;"><b>{fila['DATOSPAGO']}</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                    c2.link_button("✅ WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)
                    if c3.button("❌ CERRAR", key=f"close_{cod}", use_container_width=True):
                        st.session_state.id_abierto = None
                        st.rerun()

    st.markdown('<div class="install-box">📲 <b>¡INSTALA ESTA APP!</b><br><small>Toca los 3 puntos (⋮) y elige "Agregar a pantalla de inicio"</small></div>', unsafe_allow_html=True)

except Exception as e:
    st.info("Sincronizando flota...")
                
