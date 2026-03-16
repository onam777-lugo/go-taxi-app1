import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de pantalla y ESTILO FINAL PROFESIONAL
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    /* Fondo Naranja Global */
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro en toda la app */
    h1, h2, h3, p, b, span, label, .stMarkdown { color: black !important; }

    /* Contenedor estrecho para celulares */
    .block-container { padding: 0.5rem !important; max-width: 400px !important; }

    /* Estilo de Tarjeta Blanca (Expander) */
    .streamlit-expanderHeader {
        background-color: white !important;
        color: black !important;
        border-radius: 8px !important;
        border-left: 10px solid var(--border-color) !important;
        padding: 5px 10px !important;
        font-weight: bold !important;
    }
    
    .streamlit-expanderContent {
        background-color: #fcfcfc !important;
        color: black !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* Botones Circulares Pequeños */
    .stButton>button {
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        font-size: 18px !important;
        padding: 0px !important;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }

    /* Títulos de Sección (Disponibles, etc) */
    .section-header {
        background-color: rgba(0,0,0,0.1);
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 10px 0 5px 0;
        font-size: 14px;
        text-transform: uppercase;
    }

    /* Espaciado ultra compacto */
    .stVerticalBlock { gap: 0.2rem !important; }
    hr { margin: 0.3rem 0 !important; border-top: 1px solid rgba(0,0,0,0.05) !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin: 0;'>🚖 GO TAXI</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 11px; margin-top: -5px;'>Píritu, Portuguesa</p>", unsafe_allow_html=True)

try:
    # 2. Conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Definir secciones y colores
    secciones = [
        {"nombre": "🟢 DISPONIBLE", "estatus": "Disponible", "color": "#28a745"},
        {"nombre": "🟡 OCUPADO", "estatus": "Ocupado", "color": "#f1c40f"},
        {"nombre": "🔴 NO LABORANDO", "estatus": "No Laborando", "color": "#dc3545"}
    ]

    # 4. Mostrar por grupos
    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['estatus']]
        
        if not grupo.empty:
            st.markdown(f'<div class="section-header">{sec["nombre"]}</div>', unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf = str(fila['TELEFONO']).split('.')[0]
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Pago móvil no registrado."

                # Tarjeta del chofer
                st.markdown(f'<div style="--border-color: {sec["color"]};">', unsafe_allow_html=True)
                with st.expander(f"👤 {fila['NOMBRE']}"):
                    st.markdown(f"**💳 Datos de Pago:**\n\n{pago}")
                st.markdown('</div>', unsafe_allow_html=True)

                # Iconos de contacto a la derecha
                c_esp, c_call, c_wa = st.columns([3, 1, 1])
                with c_call:
                    st.link_button("📞", f"tel:{telf}", use_container_width=True)
                with c_wa:
                    st.link_button("💬", f"https://wa.me/58{telf}", use_container_width=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando choferes...")
