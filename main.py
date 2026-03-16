import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz # Para manejar la hora de Venezuela

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="GO TAXI", page_icon="🚖", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }
    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 0px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: bold; font-size: 12px; margin-bottom: 20px; }
    .driver-info { background-color: #FEE0C0; padding: 12px; border-radius: 12px 12px 0 0; border-left: 10px solid var(--status-color); margin-bottom: -5px; }
    .name-bold { font-weight: bold; font-size: 18px; color: black !important; }
    .code-badge { background-color: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 5px; font-size: 12px; color: #555 !important; margin-left: 5px; vertical-align: middle; }
    .phone-small { font-weight: normal; font-size: 13px; color: #444 !important; display: block; margin-top: 2px; }
    .stExpander { background-color: #FEE0C0 !important; border: none !important; border-radius: 0 0 12px 12px !important; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); }
    .stButton>button { border-radius: 10px !important; height: 45px !important; font-weight: bold !important; }
    .stMarkdown p, .stMarkdown b { color: black !important; }
    
    /* Banner de fuera de horario */
    .offline-banner { background-color: #dc3545; color: white !important; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; border: 2px solid white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU</p>', unsafe_allow_html=True)

# --- LÓGICA DE HORARIO ---
tz = pytz.timezone('America/Caracas')
hora_actual = datetime.now(tz).hour
# Es horario nocturno si es después de las 21 (9pm) o antes de las 6am
es_horario_nocturno = hora_actual >= 21 or hora_actual < 6

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    df.columns = df.columns.str.strip().str.upper()

    if es_horario_nocturno:
        st.markdown('<div class="offline-banner">🌙 HORARIO NOCTURNO<br>El servicio se activará a las 6:00 AM</div>', unsafe_allow_html=True)
        # Forzamos a que todos los que estaban disponibles u ocupados pasen a "No Laborando" visualmente
        df['ESTATUS'] = 'No Laborando'

    # 3. SECCIONES
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<b style='color: white !important; text-shadow: 1px 1px 2px black; margin-left: 5px;'>{sec['label']}</b>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Datos no registrados."
                codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                st.markdown(f"""
                    <div class="driver-info" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="code-badge">#{codigo}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander(" "):
                    st.markdown("**💳 DATOS DE PAGO:**")
                    st.code(pago, language=None) 
                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                    with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)

    # Botón de reclamos
    st.markdown("---")
    st.link_button("📩 ENVIAR RECLAMO", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.error("Error conectando con la flota...")
