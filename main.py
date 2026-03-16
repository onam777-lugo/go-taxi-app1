import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración y Estilo Visual
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro */
    h2, p, b, span, label, .stMarkdown { color: black !important; }

    .block-container { padding: 1rem !important; max-width: 450px !important; }

    /* Tarjeta del Chofer (Simulada para evitar error de HTML en expander) */
    .driver-info {
        background-color: white;
        padding: 12px;
        border-radius: 12px 12px 0 0;
        border-left: 10px solid var(--status-color);
        margin-bottom: -5px;
    }

    .name-bold { font-weight: bold; font-size: 18px; display: block; }
    .phone-small { font-weight: normal; font-size: 13px; color: #444 !important; display: block; }

    /* Estilo del Expander (Donde van los botones y pago) */
    .stExpander {
        background-color: white !important;
        border: none !important;
        border-radius: 0 0 12px 12px !important;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        border-radius: 10px !important;
        height: 45px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)

try:
    # 2. Conexión a datos
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Buscador
    busqueda = st.text_input("", placeholder="🔍 Buscar por nombre...")
    if busqueda:
        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]

    # 4. Secciones
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
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Sin datos registrados."

                # Ficha visual (Nombre arriba en negrita, Telf abajo pequeño)
                st.markdown(f"""
                    <div class="driver-info" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                # El expander ahora contiene los botones y el pago
                with st.expander("Ver opciones de contacto y pago"):
                    st.markdown(f"**💳 PAGO MÓVIL:**\n\n{pago}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # Corregido: Paréntesis cerrado correctamente
                        st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                    with c2:
                        st.link_button("💬 WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                
except Exception as e:
    st.error("Conectando con la base de datos...")
