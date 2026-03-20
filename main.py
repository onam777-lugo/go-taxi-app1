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

# 2. DISEÑO DE INTERFAZ PREMIUM (Píritu Style)
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

    /* Estilo del Buscador de Ubicación */
    .location-box {
        background-color: white; padding: 15px; border-radius: 15px;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
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
    
    /* Botones Forzados en Fila */
    [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }

    .stButton>button { 
        border-radius: 12px !important; height: 55px !important; 
        font-weight: 800 !important; text-transform: uppercase; width: 100%;
    }

    .install-box {
        background-color: rgba(255,255,255,0.2); border: 1px dashed white;
        padding: 15px; border-radius: 15px; text-align: center; color: white; margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">¡Go! TAXI</h1><p class="brand-subtitle">TU RUTA SEGURA EN PÍRITU</p>', unsafe_allow_html=True)

# 3. LÓGICA DE DATOS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    # Tarifa
    precio_vuelo = df.columns[9] if len(df.columns) > 9 else "---"
    st.markdown(f'<div class="tarifa-container"><p style="margin:0; font-size:10px; font-weight:700; color:#FF8C00;">TARIFA MÍNIMA HOY</p><p style="margin:0; font-size:22px; font-weight:900;">Bs. {precio_vuelo}</p></div>', unsafe_allow_html=True)

    # --- SECCIÓN DE UBICACIÓN ---
    st.markdown('<p style="color: white; font-weight: 800; margin-left: 5px;">📍 ¿DÓNDE TE BUSCAMOS?</p>', unsafe_allow_html=True)
    
    col_map1, col_map2 = st.columns([3, 1])
    with col_map1:
        punto_encuentro = st.text_input("Escribe dirección o referencia", placeholder="Ej: Plaza Bolívar, frente a...", label_visibility="collapsed")
    with col_map2:
        # Este enlace abre Google Maps para que el usuario vea dónde está y copie su ubicación si quiere
        st.markdown(f'''<a href="https://www.google.com/maps/search/?api=1&query=Piritu+Portuguesa" target="_blank"><button style="width:100%; height:42px; border-radius:10px; border:none; background-color:black; color:#FF8C00; font-weight:bold;">MAPA</button></a>''', unsafe_allow_html=True)

    st.markdown("---")

    # Lógica de Choferes
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
        if 'ESTATUS' in df.columns:
            grupo = df[df['ESTATUS'] == sec['key']]
            if not grupo.empty:
                st.markdown(f"<p style='color: white; font-weight: 800; margin-left: 5px; margin-bottom: 8px;'>{sec['label']}</p>", unsafe_allow_html=True)
                
                for _, fila in grupo.iterrows():
                    telf_raw = str(fila['TELEFONO']).split('.')[0]
                    telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                    pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Consultar al chofer."
                    codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                    bloquear = (sec['key'] == "No Laborando")
                    clase_tarjeta = "driver-card has-expander" if not bloquear else "driver-card"

                    st.markdown(f'<div class="{clase_tarjeta}" style="--status-color: {sec["color"]};"><span class="name-text">{fila["NOMBRE"]} <span class="code-tag">#{codigo}</span></span><span style="color:#444; font-weight:600;">📱 {telf_fmt}</span></div>', unsafe_allow_html=True)

                    if not bloquear:
                        with st.expander("SOLICITAR TAXI"):
                            st.markdown("**💳 DATOS DE PAGO:**")
                            st.code(pago, language=None) 
                            
                            # MENSAJE DE WHATSAPP DINÁMICO
                            texto_ubicacion = f" Mi ubicación es: {punto_encuentro}" if punto_encuentro else " (Te enviaré mi ubicación en el siguiente mensaje)"
                            msg_wa = f"Hola, necesito un servicio de GO TAXI con el chofer #{codigo}.{texto_ubicacion} 🚕💨"
                            
                            c1, c2 = st.columns(2)
                            with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                            with c2: st.link_button("🟢 WHATSAPP", f"https://wa.me/58{telf_raw}?text={msg_wa}", use_container_width=True)

    st.markdown('<div class="install-box"><p style="margin-bottom: 5px; font-weight: bold;">📲 ¡INSTALA ESTA APP!</p><p style="font-size: 12px;">Toca <b>Compartir</b> y elige <b>"Agregar a inicio"</b></p></div>', unsafe_allow_html=True)

except Exception as e:
    st.markdown("<p style='text-align:center; color:white;'>Sincronizando flota...</p>", unsafe_allow_html=True)
