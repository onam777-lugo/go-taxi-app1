import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

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
    
    /* Tarjeta Color Crema */
    .driver-info { 
        background-color: #FEE0C0; 
        padding: 12px; 
        border-radius: 12px; /* Redondeado completo por defecto */
        border-left: 10px solid var(--status-color); 
        margin-bottom: 15px; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Si hay un expander debajo, quitamos el redondeo inferior de la tarjeta */
    .has-expander { border-radius: 12px 12px 0 0 !important; margin-bottom: -5px !important; }

    .name-bold { font-weight: bold; font-size: 18px; color: black !important; }
    .code-badge { background-color: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 5px; font-size: 12px; color: #555 !important; margin-left: 5px; vertical-align: middle; }
    .phone-small { font-weight: normal; font-size: 13px; color: #444 !important; display: block; margin-top: 2px; }
    
    .stExpander { background-color: #FEE0C0 !important; border: none !important; border-radius: 0 0 12px 12px !important; margin-bottom: 15px; }
    .stButton>button { border-radius: 10px !important; height: 45px !important; font-weight: bold !important; }
    .stMarkdown p, .stMarkdown b { color: black !important; }
    .offline-banner { background-color: #dc3545; color: white !important; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; border: 2px solid white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">🚖 GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

# Lógica de Horario Venezuela
tz = pytz.timezone('America/Caracas')
hora_actual = datetime.now(tz).hour
es_horario_nocturno = hora_actual >= 21 or hora_actual < 6

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    df.columns = df.columns.str.strip().str.upper()

    if es_horario_nocturno:
        st.markdown('<div class="offline-banner">🌙 HORARIO NOCTURNO<br>El servicio se activará a las 6:00 AM</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

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
                
                # DETERMINAR SI BLOQUEAMOS EL CONTACTO
                bloquear = (sec['key'] == "No Laborando")

                # Clase CSS condicional para el redondeo de la tarjeta
                clase_tarjeta = "driver-info has-expander" if not bloquear else "driver-info"

                st.markdown(f"""
                    <div class="{clase_tarjeta}" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="code-badge">#{codigo}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                # SOLO MOSTRAR DESPLEGABLE SI NO ESTÁ BLOQUEADO
                if not bloquear:
                    with st.expander(" "):
                        st.markdown("**💳 DATOS DE PAGO:**")
                        st.code(pago, language=None) 
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                        with c2: st.link_button("✅ WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)

    st.markdown("---")
    st.link_button("📩 ENVIAR RECLAMO", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.error("Sincronizando flota...")
