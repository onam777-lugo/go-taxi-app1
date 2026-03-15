import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de pantalla y ESTILO VISUAL REDISEÑADO (Ultra-Compacto)
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

# Este bloque de CSS fuerza el diseño compacto y la legibilidad
st.markdown("""
    <style>
    /* Fondo Naranja Corporativo */
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto NEGRO en ABSOLUTAMENTE TODO para modo oscuro */
    h1, h2, h3, h4, p, b, span, div, label, li, .stMarkdown, p, div, span, .st-b5, .st-b6, .st-c7, .st-c8 {
        color: black !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* Reducir márgenes del contenedor principal para móviles */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 380px !important; /* Más estrecho */
    }

    /* Ocultar elementos de Streamlit innecesarios */
    #MainMenu, footer, header {visibility: hidden;}

    /* Contenedor Compacto de Driver (Haciendo el expander parecer tarjeta) */
    .streamlit-expanderHeader {
        background-color: #FFF9F2 !important; /* Blanco crema */
        border-radius: 8px !important;
        border-left: 8px solid var(--border-color) !important;
        padding: 5px 10px !important; /* Padding ultra compacto */
        margin-bottom: -5px; /* Reducir espacio con botones */
    }
    
    .streamlit-expanderContent {
        background-color: white !important;
        border-radius: 0 0 8px 8px !important;
        padding: 5px 10px !important;
        border: 1px solid #eee;
        border-top: none;
    }

    /* Estilo para los botones de contacto pequeños y laterales */
    .stButton>button {
        background-color: #F0F0F0 !important;
        color: black !important;
        border: 1px solid #CCC !important;
        border-radius: 20px !important; /* Redondos */
        height: 28px !important; /* Bajos */
        font-size: 11px !important;
        padding: 0 8px !important;
        margin-top: -2px;
    }

    /* Reducir espacio entre columnas */
    [data-testid="column"] {
        padding: 0 2px !important;
    }

    /* Quitar espacios extra entre widgets */
    .stVerticalBlock { gap: 0.1rem !important; }
    hr { margin: 0.2rem 0 !important; border-top: 1px solid rgba(0,0,0,0.05) !important; }

    /* Estilo del texto del nombre dentro del header del expander */
    .driver-name {
        font-weight: bold;
        font-size: 14px;
        margin: 0;
    }
    .driver-phone {
        font-size: 10px;
        margin: 0;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado súper compacto
st.markdown("<h3 style='text-align: center; margin-bottom: 0; font-weight: bold;'>🚖 GO TAXI</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 10px; margin-top: -5px;'>Píritu, Portuguesa</p>", unsafe_allow_html=True)

try:
    # 2. Conexión compacta
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    
    # Limpiar columnas
    df.columns = df.columns.str.strip().str.upper()

    # 3. Ordenar (Disponible > Ocupado > No Laborando)
    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    colores = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

    # 4. Mostrar Lista Compacta
    for _, fila in df.iterrows():
        status_color = colores.get(fila['ESTATUS'], '#000000')
        telf_original = str(fila['TELEFONO']).split('.')[0]
        # Formatear teléfono para mostrar
        telf_display = f"+58 {telf_original[0:3]} {telf_original[3:6]} {telf_original[6:]}"
        
        # Datos de pago o mensaje por defecto
        pago_datos = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Datos de pago no registrados."

        # TARJETA INTEGRADA: El nombre ES el expander
        # Usamos CSS variable para pasar el color del borde al estilo de arriba
        st.markdown(f'<div style="--border-color: {status_color};">', unsafe_allow_html=True)
        
        # El título del expander contiene Nombre, Teléfono y Estado compactos
        header_html = f"""
            <div style="display: flex; flex-direction: column; align-items: flex-start; width: 100%;">
                <p class="driver-name">{fila['NOMBRE']}</p>
                <p class="driver-phone">{telf_display} | <span style='color: {status_color}; font-weight: bold;'>{fila['ESTATUS']}</span></p>
            </div>
        """
        
        with st.expander(header_html):
            # Contenido que se abre al pulsar el nombre: solo los datos de pago
            st.markdown(f"""
                <div style="padding: 5px; font-size: 12px; background-color: #f9f9f9; border-radius: 5px;">
                    <b style="font-size: 11px;">💳 Datos para Pago Móvil:</b><br>
                    <p style="margin: 0; font-size: 12px;">{pago_datos}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

        # Botones de contacto ultra compactos y laterales
        c1, c2, c3 = st.columns([2, 1, 1]) # Columnas asimétricas para botones pequeños
        with c2:
            # Botón Llamar con icono
            st.link_button(f"📞", f"tel:{telf_original}", use_container_width=True)
        with c3:
            # Botón WhatsApp con icono
            st.link_button(f"💬", f"https://wa.me/58{telf_original}", use_container_width=True)
        
        # Separador muy fino
        st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando datos...")
