import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

if "id_abierto" not in st.session_state:
    st.session_state.id_abierto = None

# 2. CSS PARA BLOQUES RECTANGULARES
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    
    /* Tarjeta Principal */
    .driver-card {
        background-color: #FEE0C0;
        border-radius: 15px 15px 0 0; /* Solo redondeado arriba */
        border-left: 15px solid var(--status-color);
        padding: 15px;
        box-shadow: 4px 0px 10px rgba(0,0,0,0.1);
        margin-bottom: 0px !important;
    }

    .name-text { font-weight: 850; font-size: 20px; color: #1a1a1a; display: flex; align-items: center; }
    .code-tag { background-color: black; color: #FEE0C0; padding: 2px 8px; border-radius: 6px; font-size: 11px; margin-left: 10px; }
    .phone-text { color: #333; font-weight: 600; font-size: 15px; margin-top: 5px; }

    /* PANEL DE DESPLIEGUE RECTANGULAR (El "Cuadrado") */
    .info-block {
        background-color: #FEE0C0;
        border: 2px solid #1a0f00;
        border-radius: 0px; /* Rectángulo perfecto */
        padding: 15px;
        margin-top: 0px;
        margin-bottom: 15px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }

    .pago-datos {
        background-color: rgba(0,0,0,0.05);
        padding: 10px;
        border-radius: 5px;
        font-weight: 900; /* Negrita total */
        font-size: 16px;
        color: black;
        border: 1px solid rgba(0,0,0,0.1);
    }

    /* Botones de acción */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    
    .reclamo-footer {
        background-color: white;
        color: #1a0f00;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-top: 40px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:white; font-weight:900; font-size:45px; margin-bottom:-10px;">GO TAXI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:black; font-weight:800; letter-spacing:2px;">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0)
    
    # Tarifa
    precio = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div style="background:#1a0f00; color:white; padding:10px; border-radius:15px; text-align:center; width:70%; margin:0 auto 25px auto;"><b>TARIFA MÍNIMA Bs. {precio}</b></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#777777"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color:white; font-weight:bold; margin-top:15px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                
                # --- TARJETA ---
                st.markdown(f"""
                <div style="--status-color: {sec['color']};">
                    <div class="driver-card">
                        <div class="name-text">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></div>
                        <div class="phone-text">📱 +58 {telf}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- BOTÓN DE CONTROL ---
                if st.button(f"VER OPCIONES - {fila['NOMBRE']}", key=f"btn_{cod}", use_container_width=True):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_abierto = cod if st.session_state.id_abierto != cod else None
                        st.rerun()

                # --- DESPLIEGUE RECTANGULAR ---
                if st.session_state.id_abierto == cod:
                    st.markdown(f"""
                        <div class="info-block">
                            <p style="margin-bottom:5px; font-size:12px; color:black; font-weight:bold;">💳 PAGO MÓVIL:</p>
                            <div class="pago-datos">{fila['DATOSPAGO']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                    c2.link_button("✅ WhatsApp", f"https://wa.me/58{telf}", use_container_width=True)
                    if c3.button("❌ CERRAR", key=f"close_{cod}", use_container_width=True):
                        st.session_state.id_abierto = None
                        st.rerun()

    # ZONA DE RECLAMO
    st.markdown('<div class="reclamo-footer">📩 CENTRAL DE RECLAMOS</div>', unsafe_allow_html=True)
    st.link_button("ENVIAR MENSAJE", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.info("Actualizando flota...")
    
