import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN Y ESTILO "PÍRITU PRO"
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro */
    h2, p, b, span, label { color: black !important; font-family: sans-serif; }

    .block-container { padding: 1rem !important; max-width: 450px !important; }

    /* TARJETA BLANCA DEL CHOFER */
    .driver-box {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 10px solid var(--status-color);
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }

    .name-bold { font-weight: bold; font-size: 18px; display: block; margin-bottom: 2px; }
    .phone-small { font-weight: normal; font-size: 13px; color: #555 !important; display: block; }

    /* ESTILO DEL DESPLEGABLE DE PAGO */
    .stExpander {
        background-color: white !important;
        border: none !important;
        border-radius: 10px !important;
        margin-top: 5px;
    }
    
    .stButton>button {
        border-radius: 10px !important;
        height: 45px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)

try:
    # 2. CONEXIÓN
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. BUSCADOR
    busqueda = st.text_input("", placeholder="🔍 Buscar chofer...")
    if busqueda:
        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]

    # 4. SECCIONES Y COLORES
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
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "No registrado"

                # DISEÑO DE LA FICHA (Nombre arriba, Telf abajo)
                st.markdown(f"""
                    <div class="driver-box" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                # BOTONES DE ACCIÓN Y PAGO
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("📞 LLAMAR", f"tel:{telf_raw}",
