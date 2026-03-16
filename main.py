import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de pantalla y ESTILO FINAL PERSONALIZADO
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    /* Fondo Naranja Corporativo */
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro en toda la app para legibilidad total */
    h1, h2, h3, p, b, span, label, .stMarkdown { color: black !important; }

    /* Contenedor principal para móviles */
    .block-container { padding: 0.5rem !important; max-width: 420px !important; }

    /* Buscador redondeado */
    .stTextInput>div>div>input {
        background-color: white !important;
        color: black !important;
        border-radius: 15px !important;
        border: 1px solid #ccc !important;
    }

    /* Tarjeta Expandible (Expander) */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 12px !important;
        border-left: 10px solid var(--border-color) !important;
        padding: 10px !important;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.1) !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        border-radius: 0 0 12px 12px !important;
        padding: 15px !important;
        border: 1px solid #eee;
    }

    /* Estilo para el Nombre y Teléfono dentro del encabezado */
    .header-container { display: flex; flex-direction: column; }
    .name-text { font-weight: bold !important; font-size: 16px; margin: 0; }
    .phone-subtext { font-weight: normal !important; font-size: 13px; margin: 0; opacity: 0.8; }

    /* Botones de acción dentro de la tarjeta */
    .stButton>button {
        background-color: #f8f9fa !important;
        color: black !important;
        border: 1px solid #ddd !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 50px !important;
    }

    /* Títulos de sección (Disponibles, etc) */
    .section-label {
        color: white !important;
        font-weight: bold;
        margin: 15px 0 5px 10px;
        font-size: 14px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
    }
    
    /* Espaciado compacto */
    .stVerticalBlock { gap: 0.7rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin: 0;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)

try:
    # 2. Conexión a Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Buscador de Choferes
    busqueda = st.text_input("", placeholder="🔍 Buscar chofer por nombre...")

    if busqueda:
        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]

    # 4. Configuración de Estatus
    estatus_config = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    # 5. Renderizado de la lista
    for item in estatus_config:
        grupo = df[df['ESTATUS'] == item['key']]
        
        if not grupo.empty:
            st.markdown(f'<div class="section-label">{item["label"]}</div>', unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago_info = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "No hay datos registrados."

                # HTML para el encabezado de la tarjeta (Nombre negrita, Telf normal)
                header_html = f"""
                <div class="header-container">
                    <span class="name-text">{fila['NOMBRE']}</span>
                    <span class="phone-subtext">{telf_fmt}</span>
                </div>
                """

                # Tarjeta Expandible
                st.markdown(f'<div style="--border-color: {item["color"]};">', unsafe_allow_html=True)
                with st.expander(header_html):
                    # Sección de Pago Móvil
                    st.info(f"💳 **DATO PAGO MÓVIL:**\n\n{pago_info}")
                    
                    st.markdown("---")
                    
                    # Botones de Acción directos
                    col_call, col_wa = st.columns(2)
                    with col_call:
                        st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                    with col_wa:
                        st.link_button("💬 WHATSAPP", f"https://wa.me/58{telf_raw}?text=Hola,%20necesito%20un%20servicio%20de%20GO%20TAXI", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando base de datos...")
