import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de pantalla y ESTILO ULTRA-COMPACTO
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro y legible */
    h1, h2, h3, p, b, span, label {
        color: black !important;
    }

    /* Contenedor principal estrecho para móviles */
    .block-container {
        padding: 0.5rem !important;
        max-width: 400px !important;
    }

    /* Estilo de la tarjeta del chofer (Expander) */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 10px !important;
        border-left: 12px solid var(--border-color) !important;
        padding: 8px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #FFF9F2 !important;
        border-radius: 0 0 10px 10px !important;
        color: black !important;
        border: 1px solid #ddd;
    }

    /* Botones de iconos pequeños */
    .stButton>button {
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 50% !important; /* Redondos como en tu imagen */
        width: 45px !important;
        height: 45px !important;
        padding: 0px !important;
    }

    /* Ajustar espacios */
    .stVerticalBlock { gap: 0.3rem !important; }
    hr { margin: 0.5rem 0 !important; border-top: 1px dashed rgba(0,0,0,0.2) !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin: 0;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px; margin-bottom: 10px;'>Píritu, Portuguesa</p>", unsafe_allow_html=True)

try:
    # 2. Conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Ordenar por Estatus
    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    colores = {'Disponible': '#28a745', 'Ocupado': '#f1c40f', 'No Laborando': '#dc3545'}

    # 4. Generar lista de choferes
    for _, fila in df.iterrows():
        status_color = colores.get(fila['ESTATUS'], '#6c757d')
        telf = str(fila['TELEFONO']).split('.')[0]
        pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "No registrado"

        # Título de la tarjeta: Nombre y Estatus
        label_chofer = f"{fila['NOMBRE']}  |  {fila['ESTATUS']}"
        
        st.markdown(f'<div style="--border-color: {status_color};">', unsafe_allow_html=True)
        with st.expander(label_chofer):
            st.markdown(f"**💳 Pago Móvil:**\n\n{pago}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Botones de contacto laterales
        col_espacio, col_call, col_wa = st.columns([2, 1, 1])
        with col_call:
            st.link_button("📞", f"tel:{telf}", use_container_width=True)
        with col_wa:
            st.link_button("💬", f"https://wa.me/58{telf}", use_container_width=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error("Cargando conductores...")
