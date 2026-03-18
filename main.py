import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

if "id_abierto" not in st.session_state:
    st.session_state.id_abierto = None

# 2. CSS PARA POSICIONAR EL BOTÓN DENTRO
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    
    /* Contenedor de la Tarjeta */
    .card-wrapper {
        position: relative;
        background-color: #FEE0C0;
        border-radius: 20px;
        border-left: 15px solid var(--status-color);
        padding: 15px;
        margin-bottom: 5px !important; /* Distancia corta amarilla */
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        min-height: 110px;
    }

    .driver-name { font-weight: 850; font-size: 20px; color: #1a1a1a; display: flex; align-items: center; }
    .code-tag { background-color: black; color: #FEE0C0; padding: 2px 8px; border-radius: 6px; font-size: 11px; margin-left: 10px; }
    .phone-text { color: #333; font-weight: 600; font-size: 15px; margin-top: 5px; }

    /* EL BOTÓN DENTRO DE LA TARJETA */
    /* Forzamos al botón de Streamlit a posicionarse abajo a la derecha de la tarjeta */
    div.stButton > button {
        background-color: #1a0f00 !important;
        color: #FEE0C0 !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        font-weight: bold !important;
        height: 35px !important;
        width: 120px !important;
        border: none !important;
        margin-top: 10px !important;
    }

    /* Datos de Pago */
    .pago-desplegado {
        background-color: #FEE0C0;
        padding: 20px;
        border: 3px solid #1a0f00;
        border-top: none;
        border-radius: 0 0 20px 20px;
        margin-top: -15px;
        margin-bottom: 20px;
        color: black;
    }
    
    .zona-reclamo {
        background-color: #000;
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-top: 40px;
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
    st.markdown(f'<div style="background:#1a0f00; color:white; padding:10px; border-radius:15px; text-align:center; width:70%; margin:0 auto 20px auto;"><b>TARIFA MÍNIMA Bs. {precio}</b></div>', unsafe_allow_html=True)

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
                
                # --- RENDER DE LA TARJETA ---
                st.markdown(f"""
                <div class="card-wrapper" style="--status-color: {sec['color']};">
                    <div class="driver-name">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></div>
                    <div class="phone-text">📱 +58 {telf}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- BOTÓN "VER DATOS" REAL ---
                # Lo colocamos justo después del HTML anterior; el CSS se encarga de que parezca dentro.
                col1, col2 = st.columns([1, 1])
                with col2: # Lo ponemos en la columna derecha para que quede donde marcaste
                    st.markdown('<div style="margin-top: -55px; margin-bottom: 20px; padding-right: 10px; text-align: right;">', unsafe_allow_html=True)
                    if st.button("VER DATOS", key=f"btn_{cod}"):
                        if sec['key'] != "No Laborando":
                            st.session_state.id_abierto = cod if st.session_state.id_abierto != cod else None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                # --- DESPLIEGUE ---
                if st.session_state.id_abierto == cod:
                    st.markdown(f"""
                        <div class="pago-desplegado">
                            <p style="font-weight:900; margin-bottom:5px;">💳 PAGO MÓVIL:</p>
                            <div style="background:rgba(0,0,0,0.05); padding:10px; border-radius:10px;">
                                <b>{fila['DATOSPAGO']}</b>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                    c2.link_button("✅ WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)
                    if c3.button("❌ CERRAR", key=f"close_{cod}", use_container_width=True):
                        st.session_state.id_abierto = None
                        st.rerun()

    # ZONA DE RECLAMO
    st.markdown('<div class="zona-reclamo">⚠️ <b>ZONA DE RECLAMOS</b><br>Escríbenos si tienes algún inconveniente.</div>', unsafe_allow_html=True)
    st.link_button("📩 ENVIAR RECLAMO", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.info("Sincronizando...")
                         
