import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA Y LIMPIEZA TOTAL
st.set_page_config(
    page_title="GO TAXI", 
    page_icon="🚖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* FONDO NARANJA */
    .stApp { background-color: #FF8C00; }
    
    /* ELIMINAR MENÚS Y BARRAS DE STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* AJUSTE DE CONTENEDOR */
    .block-container { 
        padding-top: 1rem !important; 
        max-width: 450px !important; 
    }

    /* ESTILO DEL NOMBRE (Sin caja blanca) */
    .brand-title {
        text-align: center;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0px;
    }
    .brand-subtitle {
        text-align: center;
        color: black !important;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }

    /* TARJETA DEL CHOFER */
    .driver-info {
        background-color: white;
        padding: 15px;
        border-radius: 12px 12px 0 0;
        border-left: 12px solid var(--status-color);
        margin-bottom: -5px;
    }
    .name-bold { font-weight: bold; font-size: 20px; color: black !important; display: block; }
    .phone-small { font-weight: normal; font-size: 14px; color: #444 !important; }

    /* DESPLEGABLE LIMPIO (Solo la flecha) */
    .stExpander {
        background-color: white !important;
        border: none !important;
        border-radius: 0 0 12px 12px !important;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    
    /* BOTONES */
    .stButton>button { 
        border-radius: 10px !important; 
        height: 45px !important; 
        font-weight: bold !important; 
    }
    
    /* Forzar color negro en textos dentro del expander */
    .stMarkdown p, .stMarkdown b { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado estilizado sin fondo blanco
st.markdown("""
    <h1 class="brand-title">🚖 GO TAXI</h1>
    <p class="brand-subtitle">PÍRITU - PORTUGUESA</p>
    """, unsafe_allow_html=True)

try:
    # 2. Conexión a los datos
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Buscador
    busqueda = st.text_input("", placeholder="🔍 Buscar chofer...")
    if busqueda:
        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]

    # 4. Listado por secciones
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<b style='color: white !important; text-shadow: 1px 1px 2px black;'>{sec['label']}</b>", unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Datos no registrados."

                # Ficha superior blanca
                st.markdown(f"""
                    <div class="driver-info" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                # Expander que completa la tarjeta
                with st.expander(" "):
                    st.markdown(f"**💳 PAGO MÓVIL:**\n\n{pago}")
                    c1, c2 = st.columns(2)
                    with c1: 
                        st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                    with c2: 
                        st.link_button("✅ WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                
except Exception as e:
    st.error("Sincronizando flota...")
