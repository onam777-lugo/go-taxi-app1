import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(
    page_title="GO TAXI Píritu", 
    page_icon="logo.jpg", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicializar el estado de la ventana desplegada
if "id_chofer_abierto" not in st.session_state:
    st.session_state.id_chofer_abierto = None

# 2. DISEÑO DE INTERFAZ PREMIUM (Visión de Autor)
st.markdown("""
    <style>
    /* ELIMINAR INTERFAZ DE STREAMLIT */
    header, [data-testid="stHeader"], .stAppHeader { display: none !important; visibility: hidden !important; }
    #MainMenu, footer { visibility: hidden; }
    
    /* Fondo Naranja Vibrante y Espaciado */
    .stApp { background-color: #FF8C00; margin-top: -60px !important; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    /* Cabecera GO TAXI (Sombra sutil para elegancia) */
    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.3); margin-bottom: -10px; font-size: 48px; font-weight: 900; padding-top: 80px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: 800; font-size: 14px; letter-spacing: 2px; margin-bottom: 30px; }

    /* Tarifa Central (Negro Mate con borde naranja) */
    .tarifa-container {
        background-color: #1a0f00; color: white; padding: 18px;
        border-radius: 20px; text-align: center; width: 85%; margin: 0 auto 30px auto;
        border: 1px solid #FF8C00; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* TARJETA DE CHOFER ( Look Premium Crema ) */
    .driver-card-container { position: relative; margin-bottom: 8px !important; cursor: pointer; } 
    
    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 18px 22px; border-radius: 20px; 
        border-left: 15px solid var(--status-color); /* Franja de estatus bien marcada */
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        display: flex; flex-direction: column;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .driver-card:hover { transform: translateY(-2px); box-shadow: 6px 6px 15px rgba(0,0,0,0.15); }

    /* Código Fondo Negro Letras Crema (#TX-01) */
    .code-tag {
        background-color: black; color: #FEE0C0; 
        padding: 2px 10px; border-radius: 8px; 
        font-size: 12px; font-weight: bold; margin-left: 10px;
        vertical-align: middle;
    }

    .name-text { font-weight: 900; font-size: 22px; color: #1a1a1a; display: flex; align-items: center; }
    .phone-text { color: #333; font-weight: 600; font-size: 15px; margin-top: 8px; }

    /* Botón Invisible sobre la tarjeta (Toda la tarjeta es el botón) */
    div.stButton > button {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: transparent !important; border: none !important; color: transparent !important;
        z-index: 10; cursor: pointer;
    }

    /* Sección Desplegable de Pago (Modal integrado) */
    .info-desplegada {
        background-color: #FEE0C0; padding: 20px; border-radius: 0 0 20px 20px;
        border: 3px solid #1a0f00; border-top: none; margin-top: -20px; margin-bottom: 25px; color: black;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    .install-box { background-color: rgba(255,255,255,0.2); border: 2px dashed white; padding: 15px; border-radius: 20px; text-align: center; color: white; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# Encabezados Originales
st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0)
    
    # Tarifa Dinámica J1
    precio = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'''
        <div class="tarifa-container">
            <p style="margin:0; font-size:11px; color:#FF8C00; font-weight:bold; letter-spacing:1px;">TARIFA MÍNIMA HOY</p>
            <p style="margin:0; font-size:32px; font-weight:900;">Bs. {precio}</p>
        </div>
    ''', unsafe_allow_html=True)

    df.columns = df.columns.str.strip().str.upper()
    
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 10px; margin-bottom: 10px;'>{sec['label']}</p>", unsafe_allow_html=True)
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                cod = str(fila['CODIGO']).split('.')[0]
                
                # --- TARJETA VISUAL (Toda la tarjeta es el botón) ---
                st.markdown(f"""
                <div class="driver-card-container" style="--status-color: {sec['color']};">
                    <div class="driver-card">
                        <span class="name-text">{fila['NOMBRE']} <span class="code-tag">#{cod}</span></span>
                        <span class="phone-text">📱 +58 {telf[0:3]} {telf[3:6]} {telf[6:]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- ACCIÓN DE PULSAR ---
                if st.button("", key=f"btn_{cod}"):
                    if sec['key'] != "No Laborando":
                        st.session_state.id_chofer_abierto = cod if st.session_state.id_chofer_abierto != cod else None
                        st.rerun()

                # --- DESPLIEGUE DE PAGO MÓVIL Y BOTONES ---
                if st.session_state.id_chofer_abierto == cod:
                    with st.container():
                        st.markdown(f"""
                            <div class="info-desplegada">
                                <p style="font-weight:900; margin-bottom:10px;">💳 DATOS DE PAGO MÓVIL:</p>
                                <div style="background:rgba(0,0,0,0.08); padding:15px; border-radius:12px; font-family:monospace; font-size:15px; border: 1px solid rgba(0,0,0,0.1);">
                                    <b>{fila['DATOSPAGO']}</b>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)
                        col2.link_button("✅ WhatsApp", f"https://wa.me/58{telf}", use_container_width=True)
                        if col3.button("❌ Cerrar", key=f"close_{cod}", use_container_width=True):
                            st.session_state.id_chofer_abierto = None
                            st.rerun()

    st.markdown('<div class="install-box">📲 <b>¡INSTALA ESTA APP!</b><br><small>Toca los 3 puntos (⋮) o Compartir y elige "Agregar a pantalla de inicio"</small></div>', unsafe_allow_html=True)

except Exception as e:
    st.markdown("<p style='text-align:center; color:white;'>Sincronizando con la central de Píritu...</p>", unsafe_allow_html=True)
