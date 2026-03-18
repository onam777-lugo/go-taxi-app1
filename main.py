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

# Inicializar el estado de la ventana desplegada
if "id_chofer_abierto" not in st.session_state:
    st.session_state.id_chofer_abierto = None

# 2. DISEÑO DE INTERFAZ PREMIUM (CSS Reconstruido)
st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    
    .stApp { background-color: #FF8C00; margin-top: -30px !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Títulos Principales */
    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.4); margin-bottom: -10px; font-size: 42px; font-weight: 900; padding-top: 80px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 25px; }

    /* Tarifa Pequeña y Transparente */
    .tarifa-box {
        background-color: rgba(0, 0, 0, 0.7); color: white; padding: 8px 12px;
        border-radius: 12px; text-align: center; width: 70%; margin: 0 auto 25px auto;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* EL BOTÓN-TARJETA (Aquí integramos la franja lateral) */
    div.stButton > button {
        background-color: #FEE0C0 !important; /* Fondo crema */
        color: #1a1a1a !important; /* Letras casi negras */
        padding: 15px !important;
        border-radius: 15px !important;
        border: none !important;
        border-left: 12px solid var(--status-color) !important; /* LA FRANJA DE COLOR */
        margin-bottom: 10px !important;
        width: 100% !important;
        text-align: left !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1) !important;
        height: auto !important;
        display: block !important;
    }

    /* Estilos internos para simular la tarjeta original */
    .name-text-bold { font-weight: 900; font-size: 19px; color: black; display: inline-block; }
    .code-tag-black { background-color: black; color: #FF8C00; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-left: 8px; vertical-align: middle; }
    .phone-text-small { font-weight: 600; font-size: 14px; color: #444; display: block; margin-top: 5px; }

    /* Ventana de Datos (Modal) */
    .pago-modal {
        background-color: #FEE0C0;
        padding: 18px;
        border-radius: 0 0 15px 15px;
        border: 2px solid black;
        border-top: none;
        margin-top: -20px;
        margin-bottom: 25px;
        color: black;
        box-shadow: 4px 8px 15px rgba(0,0,0,0.2);
    }

    .install-box {
        background-color: rgba(255,255,255,0.2); border: 1px dashed white;
        padding: 15px; border-radius: 15px; text-align: center; color: white; margin-top: 30px;
    }
    
    .stLinkButton > a { border-radius: 12px !important; font-weight: bold !important; height: 45px !important; }
    </style>
    """, unsafe_allow_html=True)

# Títulos
st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    # Tarifa J1
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "Consultar"
    st.markdown(f"""
        <div class="tarifa-box">
            <p style="margin:0; font-size:10px; font-weight:700; color:#FF8C00; letter-spacing:1px; line-height:1;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:22px; font-weight:900; line-height:1;">Bs. {precio_vuelo}</p>
        </div>
    """, unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    tz = pytz.timezone('America/Caracas')
    es_noche = datetime.now(tz).hour >= 21 or datetime.now(tz).hour < 6

    if es_noche:
        st.markdown('<div style="background-color:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:20px; border: 2px solid white;">🌙 SERVICIO CERRADO (9PM - 6AM)</div>', unsafe_allow_html=True)
        df['ESTATUS'] = 'No Laborando'

    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#777777"} # Gris neutro
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color: white; font-weight: bold; margin-left: 5px; margin-top: 15px; margin-bottom: 8px;'>{sec['label']}</p>", unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Consultar al chofer."
                codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                # Usamos una variable CSS para definir el color de la franja lateral
                st.markdown(f"<div style='--status-color: {sec['color']};'>", unsafe_allow_html=True)
                
                # Construimos la etiqueta del botón con HTML para simular el diseño original
                # Negrita para nombre, cuadro negro para código, y número debajo.
                label_boton = f"**{fila['NOMBRE']}** #{codigo}\n\n📱 {telf_fmt}"

                if st.button(label_boton, key=f"btn_{codigo}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_chofer_abierto = codigo if st.session_state.id_chofer_abierto != codigo else None
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

                # VENTANA DESPLEGADA (Solo si este chofer es el seleccionado)
                if st.session_state.id_chofer_abierto == codigo:
                    with st.container():
                        st.markdown(f"""
                            <div class="pago-modal">
                                <p style="font-weight:bold; margin:0; font-size:13px;">💳 PAGO MÓVIL / DATOS:</p>
                                <div style="background: rgba(0,0,0,0.06); padding: 12px; border-radius: 10px; margin-top: 10px; margin-bottom: 20px;">
                                    <b>{pago}</b>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Botones de acción (Llamar, WhatsApp, Cerrar)
                        c1, c2, c3 = st.columns(3)
                        with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                        with c2: st.link_button("✅ WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                        with c3:
                            if st.button("❌ CERRAR", key=f"close_{codigo}", use_container_width=True):
                                st.session_state.id_chofer_abierto = None
                                st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <div class="install-box">
            <p style="margin-bottom: 5px; font-weight: bold;">📲 ¡INSTALA ESTA APP!</p>
            <p style="font-size: 12px;">Toca los <b>3 puntos (⋮)</b> o <b>Compartir</b> y elige<br><b>"Agregar a pantalla de inicio"</b></p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.link_button("📩 CENTRAL DE RECLAMOS", "mailto:WorkflowDesignerOnam@gmail.com", use_container_width=True)

except Exception as e:
    st.markdown("<p style='text-align:center; color:white;'>Sincronizando flota de GO TAXI...</p>", unsafe_allow_html=True)
    
