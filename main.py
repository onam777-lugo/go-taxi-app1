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

# Estado para la ventana desplegada
if "id_chofer_abierto" not in st.session_state:
    st.session_state.id_chofer_abierto = None

# 2. DISEÑO DE INTERFAZ (Correcciones de espaciado y estilos)
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Títulos */
    .brand-title { text-align: center; color: white !important; font-size: 42px; font-weight: 900; padding-top: 80px; margin-bottom: -10px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Tarifa */
    .tarifa-box {
        background-color: rgba(0, 0, 0, 0.8); color: white; padding: 10px;
        border-radius: 15px; text-align: center; width: 80%; margin: 0 auto 20px auto;
    }

    /* CONTENEDOR DE BOTONES (Para reducir distancia entre ellos) */
    .element-container { margin-bottom: -10px !important; } 

    /* BOTÓN TIPO TARJETA */
    div.stButton > button {
        background-color: #FEE0C0 !important;
        border: none !important;
        border-left: 15px solid var(--status-color) !important; /* FRANJA AZUL MARCADA */
        border-radius: 15px !important;
        padding: 12px 15px !important;
        width: 100% !important;
        height: 90px !important;
        text-align: left !important;
        margin-bottom: 5px !important; /* DISTANCIA CORTA AMARILLA */
        box-shadow: 2px 4px 8px rgba(0,0,0,0.1) !important;
    }

    /* ESTILO DEL CÓDIGO (Fondo negro, letras crema) */
    .code-badge {
        background-color: #000000;
        color: #FEE0C0;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
        display: inline-block;
    }

    /* Ventana Desplegada */
    .pago-desplegado {
        background-color: #FEE0C0;
        padding: 15px;
        border-radius: 0 0 15px 15px;
        border: 2px solid black;
        border-top: none;
        margin-top: -15px;
        margin-bottom: 15px;
        color: black;
    }
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
                
                # Render del botón con el estilo solicitado
                st.markdown(f"<div style='--status-color: {sec['color']};'>", unsafe_allow_html=True)
                
                # Usamos st.button pero la etiqueta la manejamos para que parezca la original
                # Nota: Streamlit no permite HTML complejo dentro del label del botón, 
                # así que usamos negritas y el emoji para mantener la estructura.
                if st.button(f"👤 **{nombre}** #{cod}\n\n📱 +58 {telf}", key=f"btn_{cod}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_chofer_abierto = cod if st.session_state.id_chofer_abierto != cod else None
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

                if st.session_state.id_chofer_abierto == cod:
                    st.markdown(f"""
                        <div class="pago-desplegado">
                            <p style="font-weight:900; margin-bottom:5px;">💳 DATOS DE PAGO:</p>
                            <div style="background:rgba(0,0,0,0.05); padding:10px; border-radius:8px;"><b>{pago}</b></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                    c2.link_button("✅ WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)
                    if c3.button("❌ CERRAR", key=f"close_{cod}", use_container_width=True):
                        st.session_state.id_chofer_abierto = None
                        st.rerun()

except Exception as e:
    st.info("Sincronizando...")
                
