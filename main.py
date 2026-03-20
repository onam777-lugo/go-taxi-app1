import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz
# Instalación necesaria: pip install streamlit-js-eval
from streamlit_js_eval import get_geolocation

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
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    .brand-title { 
        text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); 
        margin-bottom: -10px; font-size: 42px; font-weight: 900; padding-top: 80px;
    }
    .brand-subtitle { 
        text-align: center; color: black !important; font-weight: 800; 
        font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; 
    }

    .tarifa-container {
        background-color: rgba(0, 0, 0, 0.5); color: white; padding: 8px 12px; 
        border-radius: 12px; text-align: center; margin-bottom: 25px; 
        border: 1px solid rgba(255,255,255,0.1); width: 50%; margin: 0 auto 25px auto;
    }

    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 15px; border-radius: 15px; border-left: 12px solid var(--status-color);
        margin-bottom: 15px; box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
    }
    
    .has-expander { border-radius: 15px 15px 0 0 !important; margin-bottom: -5px !important; }
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }
    .code-tag { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }
    
    .stExpander { background-color: #FEE0C0 !important; border: none !important; border-radius: 0 0 15px 15px !important; margin-bottom: 20px; }
    
    /* Forzar botones en fila para celular */
    [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }

    .stButton>button { 
        border-radius: 12px !important; height: 55px !important; 
        font-weight: 800 !important; text-transform: uppercase; width: 100%;
    }

    /* Estilo especial para el botón de GPS */
    .gps-btn button {
        background-color: #1a0f00 !important;
        color: #FF8C00 !important;
        border: 2px solid #FF8C00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">¡Go! TAXI</h1><p class="brand-subtitle">TU RUTA SEGURA EN PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div class="tarifa-container"><p style="margin:0; font-size:10px; font-weight:700; color:#FF8C00;">TARIFA MÍNIMA HOY</p><p style="margin:0; font-size:22px; font-weight:900;">Bs. {precio_vuelo}</p></div>', unsafe_allow_html=True)

    # --- NUEVA SECCIÓN DE UBICACIÓN GPS ---
    st.markdown('<p style="color: white; font-weight: 800; margin-left: 5px;">📍 ¿DÓNDE TE BUSCAMOS?</p>', unsafe_allow_html=True)
    
    # Obtener coordenadas
    loc = get_geolocation()
    map_link = ""
    
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        map_link = f"https://www.google.com/maps?q={lat},{lon}"
        st.success("✅ Ubicación GPS lista")
    else:
        st.warning("⚠️ Toca 'Permitir' para activar tu GPS o escribe abajo:")

    ref_manual = st.text_input("Referencia adicional (Ej: Casa frente al abasto)", placeholder="Escribe aquí...", label_visibility="collapsed")
    st.markdown("---")

    # Listado de Choferes
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
        grupo = df[df['ESTATUS'] == sec['key']] if 'ESTATUS' in df.columns else pd.DataFrame()
        if not grupo.empty:
            st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 5px; margin-bottom: 8px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Consultar."

                bloquear = (sec['key'] == "No Laborando")
                clase_tarjeta = "driver-card has-expander" if not bloquear else "driver-card"

                st.markdown(f'<div class="{clase_tarjeta}" style="--status-color: {sec["color"]};"><span class="name-text">{fila["NOMBRE"]} <span class="code-tag">#{codigo}</span></span><span style="color:#444; font-weight:600;">📱 +58 {telf_raw}</span></div>', unsafe_allow_html=True)

                if not bloquear:
                    with st.expander("SOLICITAR SERVICIO"):
                        st.write(f"💳 **PAGO MÓVIL:** {pago}")
                        
                        # Mensaje de WhatsApp con el link del mapa
                        msg_gps = f"📍 Mi mapa: {map_link}" if map_link else "(Te enviaré mi GPS ahora mismo)"
                        msg_ref = f" 🏠 Ref: {ref_manual}" if ref_manual else ""
                        msg_final = f"Hola, necesito un GO TAXI con el chofer #{codigo}. {msg_gps}{msg_ref} 🚕💨"
                        
                        c1, c2 = st.columns(2)
                        with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                        with c2: st.link_button("🟢 WHATSAPP", f"https://wa.me/58{telf_raw}?text={msg_final}", use_container_width=True)

except Exception as e:
    st.markdown("<p style='text-align:center; color:white;'>Cargando flota...</p>", unsafe_allow_html=True)
