import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(
    page_title="GO TAXI", 
    page_icon="logo.jpeg", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. ESTILOS VISUALES (Diseño Limpio Píritu - Sin barra blanca)
st.markdown("""
    <style>
    /* Eliminar barra blanca superior y menús */
    header, [data-testid="stHeader"], .stAppHeader {
        display: none !important;
        visibility: hidden !important;
    }
    
    .stApp {
        background-color: #FF8C00;
        margin-top: -60px !important;
    }

    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 0px; font-size: 42px; font-weight: 900; padding-top: 40px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: bold; font-size: 14px; margin-bottom: 25px; letter-spacing: 1px; }

    /* Banner de Tarifa */
    .tarifa-box {
        background-color: black;
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Tarjeta Color Crema (#FEE0C0) */
    .driver-info {
        background-color: #FEE0C0;
        padding: 15px;
        border-radius: 15px;
        border-left: 10px solid var(--status-color);
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    
    .has-expander { border-radius: 15px 15px 0 0 !important; margin-bottom: -5px !important; }
    .name-bold { font-weight: 800; font-size: 20px; color: black !important; display: block; }
    .code-badge { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }
    .phone-small { font-weight: 600; font-size: 14px; color: #444 !important; display: block; margin-top: 4px; }

    .stExpander {
        background-color: #FEE0C0 !important;
        border: none !important;
        border-radius: 0 0 15px 15px !important;
        margin-bottom: 20px;
    }
    
    .stButton>button { border-radius: 12px !important; height: 50px !important; font-weight: bold !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    # 3. CONEXIÓN A GOOGLE SHEETS
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    
    # Leemos la hoja (Sheet1)
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0) 
    
    # --- LÓGICA DE TARIFA (CELDA J1 / Columna 10) ---
    try:
        # Buscamos el valor que está en el encabezado de la columna J
        precio_actual = df.columns[9] if len(df.columns) > 9 else "---"
    except:
        precio_actual = "Consultar"

    st.markdown(f"""
        <div class="tarifa-box">
            <p style="margin:0; font-size:11px; font-weight:700; color:#FF8C00; letter-spacing:1px;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:28px; font-weight:900;">Bs. {precio_actual}</p>
        </div>
    """, unsafe_allow_html=True)

    # 4. ORGANIZACIÓN DE FLOTA
    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; border: 2px solid white;">🌙 SERVICIO CERRADO (9PM - 6AM)</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == sec['key']]
            if not grupo.empty:
                st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 5px; margin-bottom: 8px;'>{sec['label']}</p>", unsafe_allow_html=True)
                
                for _, fila in grupo.iterrows():
                    telf = str(fila['TELEFONO']).split('.')[0]
                    cod = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"
                    pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Consultar al chofer."

                    bloquear = (sec['key'] == "No Laborando")
                    clase_css = "driver-info has-expander" if not bloquear else "driver-info"

                    st.markdown(f"""
                        <div class="{clase_css}" style="--status-color: {sec['color']};">
                            <span class="name-bold">{fila['NOMBRE']} <span class="code-badge">#{cod}</span></span>
                            <span class="phone-small">📱 +58 {telf}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    if not bloquear:
                        with st.expander("VER OPCIONES DE CONTACTO"):
                            st.markdown("**💳 DATOS DE PAGO:**")
                            st.code(pago, language=None) 
                            st.markdown("---")
                            c1, c2 = st.columns(2)
                            c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                            c2.link_button("✅ WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)

    st.markdown("---")
    st.caption("Central de Taxi Píritu - Portuguesa")

except Exception as e:
    st.markdown("<p style='text-align:center; color:white;'>Sincronizando flota...</p>", unsafe_allow_html=True)
