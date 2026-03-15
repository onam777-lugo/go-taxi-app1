import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de pantalla y Estilos Compactos
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro en todo para evitar errores en modo oscuro */
    h1, h2, h3, p, b, span, div, label, .stMarkdown {
        color: black !important;
        line-height: 1.2 !important;
    }

    /* Hacer el contenedor principal más estrecho para móviles */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 400px !important;
    }

    /* Estilo para los botones compactos */
    .stButton>button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
        height: 35px !important;
        font-size: 14px !important;
        font-weight: bold !important;
    }

    /* Estilo del Expander para que parezca una tarjeta */
    .streamlit-expanderHeader {
        background-color: #FFF9F2 !important; /* Blanco crema */
        border-radius: 10px !important;
        border-left: 10px solid var(--border-color) !important;
        padding: 10px !important;
    }
    
    .streamlit-expanderContent {
        background-color: white !important;
        border-radius: 0 0 10px 10px !important;
        color: black !important;
    }

    /* Quitar espacio extra entre elementos */
    .stVerticalBlock { gap: 0.5rem !important; }
    hr { margin: 0.5em 0 !important; border-top: 1px solid rgba(0,0,0,0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Píritu, Portuguesa</p>", unsafe_allow_html=True)

try:
    # 2. Conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Ordenar
    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    colores = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

    # 4. Lista de Conductores
    for _, fila in df.iterrows():
        status_color = colores.get(fila['ESTATUS'], '#000000')
        telf = str(fila['TELEFONO']).split('.')[0]
        pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "No disponible"

        # Tarjeta Expandible: El nombre ahora es el botón
        # Usamos CSS variable para pasar el color del borde al estilo de arriba
        st.markdown(f'<div style="--border-color: {status_color};">', unsafe_allow_html=True)
        with st.expander(f"👤 {fila['NOMBRE']}  |  {fila['ESTATUS']}"):
            st.write(f"**Datos de Pago:**")
            st.info(pago)
        st.markdown('</div>', unsafe_allow_html=True)

        # Botones de acción compactos
        c1, c2 = st.columns(2)
        with c1:
            st.link_button(f"📞 LLAMAR", f"tel:{telf}", use_container_width=True)
        with c2:
            st.link_button(f"💬 WHATSAPP", f"https://wa.me/58{telf}", use_container_width=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando datos...")
