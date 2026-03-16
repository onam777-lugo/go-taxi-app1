import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN
st.set_page_config(page_title="GO TAXI", page_icon="logo.jpg", layout="centered")

# 2. DISEÑO PREMIUM (Tu estilo original)
st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }
    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; font-size: 42px; font-weight: 900; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 15px; }
    
    .tarifa-container {
        background-color: black; color: white; padding: 12px; border-radius: 15px;
        text-align: center; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.2);
    }
    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0); padding: 15px;
        border-radius: 15px; border-left: 12px solid var(--status-color); margin-bottom: 15px;
    }
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; }
    .code-tag { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS (Optimizada para no trabarse)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    
    # LEEMOS TODO EL EXCEL DE UN SOLO GOLPE
    # Nota: Si esto falla, es que la hoja CONFIG o Sheet1 tienen nombres distintos en el Excel
    df_choferes = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    
    try:
        df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
        precio_hoy = str(df_config.iloc[0, 1])
    except:
        precio_hoy = "480" # Valor por defecto si falla la lectura de tarifa

    # Mostrar Tarifa
    st.markdown(f"""
        <div class="tarifa-container">
            <p style="margin:0; font-size:11px; font-weight:700; color:#FF8C00;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:26px; font-weight:900;">Bs. {precio_hoy}</p>
        </div>
    """, unsafe_allow_html=True)

    # 4. PROCESAR CHOFERES
    df_choferes.columns = df_choferes.columns.str.strip().str.upper()
    
    # Horario
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.error("🌙 SERVICIO CERRADO (6AM - 9PM)")
        df_choferes['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df_choferes[df_choferes['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color: white; font-weight: 800;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                
                st.markdown(f"""
                    <div class="driver-card" style="--status-color: {sec['color']};">
                        <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></span><br>
                        <span style="color:#444;">📱 +58 {telf}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if sec['key'] != "No Laborando":
                    with st.expander("OPCIONES"):
                        st.code(fila.get('DATOSPAGO', 'Sin datos'), language=None)
                        c1, c2 = st.columns(2)
                        c1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                        c2.link_button("WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)

except Exception as e:
    st.warning("Ajustando conexión... Por favor, verifica que las pestañas en Excel se llamen 'Sheet1' y 'CONFIG'.")
