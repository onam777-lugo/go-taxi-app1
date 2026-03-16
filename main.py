import streamlit as st

import pandas as pd

from streamlit_gsheets import GSheetsConnection



# 1. Configuración de pantalla y ESTILO TIPO APP MODERNA

st.set_page_config(page_title="GO TAXI", page_icon="🚖")



st.markdown("""

    <style>

    .stApp { background-color: #FF8C00; }

    

    /* Forzar texto negro legible */

    h1, h2, h3, p, b, span, label, .stMarkdown { color: black !important; }



    /* Contenedor principal estrecho para móviles */

    .block-container { padding: 0.5rem !important; max-width: 400px !important; }



    /* Buscador estilizado */

    .stTextInput>div>div>input {

        background-color: white !important;

        color: black !important;

        border-radius: 20px !important;

    }



    /* Tarjeta que contiene todo (Expander) */

    .streamlit-expanderHeader {

        background-color: white !important;

        color: black !important;

        border-radius: 12px !important;

        border-left: 12px solid var(--border-color) !important;

        padding: 12px !important;

        font-weight: bold !important;

        font-size: 16px !important;

        box-shadow: 2px 2px 8px rgba(0,0,0,0.15) !important;

    }

    

    .streamlit-expanderContent {

        background-color: #ffffff !important;

        border-radius: 0 0 12px 12px !important;

        padding: 15px !important;

        border: 1px solid #eee;

    }



    /* Botones de acción dentro del expander */

    .stButton>button {

        background-color: #f0f0f0 !important;

        color: black !important;

        border: 1px solid #ddd !important;

        border-radius: 10px !important;

        font-weight: bold !important;

        height: 45px !important;

    }



    /* Títulos de sección compactos */

    .section-header {

        color: white !important;

        font-weight: bold;

        margin: 15px 0 5px 5px;

        font-size: 14px;

        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);

    }



    /* Espaciado */

    .stVerticalBlock { gap: 0.6rem !important; }

    </style>

    """, unsafe_allow_html=True)



st.markdown("<h2 style='text-align: center; margin: 0;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)



try:

    # 2. Conexión y Limpieza

    conn = st.connection("gsheets", type=GSheetsConnection)

    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"

    df = conn.read(spreadsheet=url)

    df.columns = df.columns.str.strip().str.upper()



    # 3. Buscador por nombre (Igual a tu referencia)

    busqueda = st.text_input("🔍 Buscar por nombre...", placeholder="Escribe el nombre del chofer")



    if busqueda:

        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]



    # 4. Secciones

    secciones = [

        {"nombre": "🟢 DISPONIBLES", "estatus": "Disponible", "color": "#28a745"},

        {"nombre": "🟡 OCUPADOS", "estatus": "Ocupado", "color": "#f1c40f"},

        {"nombre": "🔴 NO LABORANDO", "estatus": "No Laborando", "color": "#dc3545"}

    ]



    # 5. Lógica de visualización

    for sec in secciones:

        grupo = df[df['ESTATUS'] == sec['estatus']]

        if not grupo.empty:

            st.markdown(f'<div class="section-header">{sec["nombre"]}</div>', unsafe_allow_html=True)

            

            for _, fila in grupo.iterrows():

                telf = str(fila['TELEFONO']).split('.')[0]

                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "No registrado"



                # TARJETA ÚNICA: Todo aparece al abrir

                st.markdown(f'<div style="--border-color: {sec["color"]};">', unsafe_allow_html=True)

                with st.expander(f"👤 {fila['NOMBRE']}"):

                    # Datos de Pago

                    st.markdown(f"**💳 PAGO MÓVIL:**")

                    st.code(pago, language=None) # Estilo recuadro para copiar fácil

                    

                    st.markdown("---")

                    

                    # Botones de contacto internos

                    c1, c2 = st.columns(2)

                    with c1:

                        st.link_button("📞 LLAMAR", f"tel:{telf}", use_container_width=True)

                    with c2:

                        st.link_button("💬 WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)



except Exception as e:

    st.error("Sincronizando con Píritu...")

