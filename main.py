import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

# Inicializar el estado de la ventana emergente
if "chofer_sel" not in st.session_state:
    st.session_state.chofer_sel = None

# 2. DISEÑO DE INTERFAZ (CSS Píritu Premium)
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #FF8C00; }
    
    /* Títulos */
    .brand-title { text-align: center; color: white; font-size: 42px; font-weight: 900; padding-top: 80px; margin-bottom: -10px; }
    .brand-subtitle { text-align: center; color: black; font-weight: 800; font-size: 14px; margin-bottom: 25px; }

    /* Tarifa Pequeña y Transparente */
    .tarifa-box {
        background-color: rgba(0, 0, 0, 0.7); color: white; padding: 8px;
        border-radius: 12px; text-align: center; width: 60%; margin: 0 auto 25px auto;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Estilo de las Tarjetas (Botones) */
    div.stButton > button {
        background-color: #FEE0C0 !important;
        color: #1a1a1a !important;
        border-radius: 15px !important;
        border: none !important;
        border-left: 12px solid var(--col) !important;
        padding: 15px !important;
        width: 100% !important;
        text-align: left !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1) !important;
        margin-bottom: 10px;
    }

    /* Ventana de Datos (Modal) */
    .modal-card {
        background-color: #FEE0C0;
        padding: 20px;
        border-radius: 20px;
        border: 2px solid black;
        color: black;
        margin-bottom: 20px;
    }
    
    .stLinkButton > a {
        border-radius: 12px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

def cerrar_ventana():
    st.session_state.chofer_sel = None

# --- CONTENIDO ---
st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7m (URL CORTA POR ESPACIO)"
    # Nota: Usa tu URL completa de siempre aquí
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0)
    
    # Tarifa desde J1
    precio = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div class="tarifa-box"><p style="margin:0; font-size:10px; color:#FF8C00;">TARIFA MÍNIMA</p><p style="margin:0; font-size:22px; font-weight:900;">Bs. {precio}</p></div>', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    # LÓGICA DE VENTANA ABIERTA
    if st.session_state.chofer_sel:
        c = st.session_state.chofer_sel
        st.markdown(f"""
            <div class="modal-card">
                <h2 style="margin:0;">{c['NOMBRE']}</h2>
                <code style="background:black; color:#FF8C00; padding:2px 5px; border-radius:5px;">CÓDIGO: #{c['CODIGO']}</code>
                <hr style="border:1px solid black;">
                <p style="font-weight:bold; margin-bottom:5px;">DATOS DE PAGO:</p>
                <div style="background:rgba(0,0,0,0.05); padding:10px; border-radius:10px;">{c['PAGO']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        col1.link_button("📞 LLAMAR", f"tel:{c['TELF']}", use_container_width=True)
        col2.link_button("✅ WHATSAPP", f"https://wa.me/58{c['TELF']}", use_container_width=True)
        if col3.button("❌ CERRAR", use_container_width=True):
            cerrar_ventana()
            st.rerun()
        st.markdown("---")

    # LISTADO DE FLOTA
    if es_noche:
        st.error("🌙 SERVICIO CERRADO (9PM - 6AM)")
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#777777"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color:white; font-weight:bold; margin-top:10px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                nombre = fila['NOMBRE']
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                
                # Crear botón con color de borde según estatus
                # Usamos una variable CSS para el color del borde izquierdo
                st.markdown(f"<div style='--col: {sec['color']};'>", unsafe_allow_html=True)
                if st.button(f"👤 {nombre}\n📱 +58 {telf}  |  #{cod}", key=f"btn_{cod}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.chofer_sel = {
                            "NOMBRE": nombre, "TELF": telf, 
                            "CODIGO": cod, "PAGO": fila['DATOSPAGO']
                        }
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.info("Sincronizando flota...")
