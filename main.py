import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración y Estilo Visual (Fondo Naranja y Texto Negro)
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    .stApp {
        background-color: #FF8C00; /* Naranja de tu logo */
    }
    /* Forzar que todo el texto sea negro para que se vea en modo oscuro */
    h1, h2, h3, p, b, span, li, label, .stMarkdown {
        color: black !important;
    }
    /* Estilo de la tarjeta blanca del conductor */
    .driver-card {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    /* Estilo para los botones de Streamlit */
    .stButton>button {
        background-color: black !important;
        color: white !important;
        border-radius: 8px;
    }
    /* Estilo para el desplegable (expander) */
    .streamlit-expanderHeader {
        background-color: white !important;
        color: black !important;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>GO TAXI</h1>", unsafe_allow_html=True)

try:
    # 2. Conexión a los datos
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    
    # Limpiamos nombres de columnas (Quita espacios y pone en Mayúsculas)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Ordenar (Disponible arriba)
    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    # 4. Colores por estatus
    colores_status = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

    # 5. Mostrar Conductores
    for _, fila in df.iterrows():
        color_borde = colores_status.get(fila['ESTATUS'], '#000000')
        # Limpiar el teléfono para que no tenga decimales (.0)
        telf = str(fila['TELEFONO']).split('.')[0]
        
        # Tarjeta visual
        st.markdown(f"""
            <div class="driver-card" style="border-left: 10px solid {color_borde};">
                <h3 style="margin:0;"> {fila['NOMBRE']}</h3>
                <p style="color: {color_borde}; font-weight: bold; margin: 5px 0;">● {fila['ESTATUS']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones de contacto
        col1, col2 = st.columns(2)
        with col1:
            st.link_button(f"📞 LLAMAR", f"tel:{telf}", use_container_width=True)
        with col2:
            st.link_button(f"💬 WHATSAPP", f"https://wa.me/58{telf}?text=Hola,%20necesito%20un%20servicio%20de%20GO%20TAXI", use_container_width=True)
        
        # 6. DATOSPAGO (El desplegable que pediste)
        if 'DATOSPAGO' in df.columns and pd.notna(fila['DATOSPAGO']):
            with st.expander("💳 Ver Datos de Pago Móvil"):
                st.write(fila['DATOSPAGO'])
        
        st.markdown("---")

except Exception as e:
    st.error(f"Error: {e}")
