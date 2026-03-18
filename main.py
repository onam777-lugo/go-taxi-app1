import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

if "id_abierto" not in st.session_state:
    st.session_state.id_abierto = None

# 2. DISEÑO DE INTERFAZ PREMIUM
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Títulos */
    .brand-title { text-align: center; color: white !important; font-size: 42px; font-weight: 900; padding-top: 80px; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Tarifa */
    .tarifa-box { background-color: #1a0f00; color: white; padding: 15px; border-radius: 20px; text-align: center; width: 85%; margin: 0 auto 25px auto; }

    /* TARJETA CONTENEDORA */
    .driver-card {
        background-color: #FEE0C0;
        padding: 15px 20px; border-radius: 20px; 
        border-left: 15px solid var(--status-color);
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between; /* Alinea texto a la izquierda y botón a la derecha */
        align-items: center;
        margin-bottom: 8px !important; /* Distancia corta */
    }

    .driver-info { display: flex; flex-direction: column; }

    /* Código Fondo Negro Letras Crema */
    .code-tag {
        background-color: black; color: #FEE0C0; 
        padding: 2px 10px; border-radius: 8px; 
        font-size: 12px; font-weight: bold; margin-left: 10px;
    }

    .name-text { font-weight: 850; font-size: 20px; color: #1a1a1a; display: flex; align-items: center; }
    .phone-text { color: #333; font-weight: 600; font-size: 15px; margin-top: 5px; }

    /* BOTÓN DE DESPLIEGUE (Zona rallada roja) */
    .deploy-btn-zone {
        background-color: rgba(0,0,0,0.05);
        border: 2px dashed rgba(0,0,0,0.2);
        border-radius: 12px;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    /* Invisible pero funcional sobre la zona roja */
    div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #1a1a1a !important;
        font-size: 24px !important;
        width: 100% !important;
        height: 100% !important;
    }

    /* Ventana de Pago */
    .info-desplegada {
        background-color: #FEE0C0; padding: 20px; border-radius: 0 0 20px 20px;
        border: 3px solid #1a0f00; border-top: none; margin-top: -15px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0)
    
    precio = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div class="tarifa-box"><p style="margin:0; font-size:11px; color:#FF8C00; font-weight:bold;">TARIFA MÍNIMA HOY</p><p style="margin:0; font-size:32px; font-weight:900;">Bs. {precio}</p></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 10px; margin-top: 15px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                
                # --- TARJETA CON BOTÓN A LA DERECHA ---
                col_card, col_btn = st.columns([4, 1])
                
                with col_card:
                    st.markdown(f"""
                    <div style="--status-color: {sec['color']}; margin-right: -25px;">
                        <div class="driver-card">
                            <div class="driver-info">
                                <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></span>
                                <span class="phone-text">📱 +58 {telf[0:3]} {telf[3:6]} {telf[6:]}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_btn:
                    # Este botón ocupa el lugar del "rallado rojo"
                    if st.button("展开", key=f"btn_{cod}"): # Emoji o texto de despliegue
                        if sec['key'] != "No Laborando":
                            st.session_state.id_abierto = cod if st.session_state.id_abierto != cod else None
                            st.rerun()

                # --- DESPLIEGUE ---
                if st.session_state.id_abierto == cod:
                    st.markdown(f"""
                        <div class="info-desplegada">
                            <p style="font-weight:900; margin-bottom:10px;">💳 PAGO MÓVIL:</p>
                            <div style="background:rgba(0,0,0,0.08); padding:15px; border-radius:12px;">
                                <b style="font-size:16px; color:black;">{fila['DATOSPAGO']}</b>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                    c2.link_button("✅ WhatsApp", f"https://wa.me/58{telf}", use_container_width=True)
                    if c3.button("❌ Cerrar", key=f"close_{cod}", use_container_width=True):
                        st.session_state.id_abierto = None
                        st.rerun()

except Exception as e:
    st.info("Sincronizando...")
                    
