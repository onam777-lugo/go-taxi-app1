import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración y Estilos de Marca
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    
    /* Forzar texto negro */
    h1, h2, p, b, span, label, .stMarkdown { color: black !important; }

    .block-container { padding: 1rem !important; max-width: 450px !important; }

    /* Logo / Encabezado */
    .brand-header {
        text-align: center;
        background-color: white;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }

    /* Tarjeta del Chofer */
    .driver-info {
        background-color: white;
        padding: 15px;
        border-radius: 12px 12px 0 0;
        border-left: 12px solid var(--status-color);
        margin-bottom: -5px;
    }

    .name-bold { font-weight: bold; font-size: 20px; display: block; }
    .phone-small { font-weight: normal; font-size: 14px; color: #444 !important; display: block; }

    /* Estilo del Expander (Sin texto, solo la flecha) */
    .stExpander {
        background-color: white !important;
        border: none !important;
        border-radius: 0 0 12px 12px !important;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Botones de acción */
    .btn-call {
        background-color: #e0e0e0 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 50px !important;
    }
    
    /* Botón de WhatsApp con su color oficial */
    .btn-whatsapp {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 50px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado (Aquí puedes poner la URL de tu logo si lo tienes en internet)
st.markdown("""
    <div class="brand-header">
        <h1 style="margin:0; font-size: 28px;">🚖 GO TAXI</h1>
        <p style="margin:0; font-size: 14px; font-weight: bold;">PÍRITU - PORTUGUESA</p>
    </div>
    """, unsafe_allow_html=True)

try:
    # 2. Datos
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Buscador
    busqueda = st.text_input("", placeholder="🔍 Buscar chofer por nombre...")
    if busqueda:
        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]

    # 4. Listado por Secciones
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        grupo = df[df['ESTATUS'] == sec['key']]
        if not grupo.empty:
            st.markdown(f"<b style='color: white !important; text-shadow: 1px 1px 2px black; margin-left: 10px;'>{sec['label']}</b>", unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Datos no registrados."

                # Ficha Blanca
                st.markdown(f"""
                    <div class="driver-info" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                # Expander vacío (solo flecha)
                with st.expander(" "):
                    st.markdown(f"**💳 PAGO MÓVIL:**\n\n{pago}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                    with c2:
                        # Botón estilizado de WhatsApp
                        st.link_button("✅ WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)
                
except Exception as e:
    st.error("Sincronizando con la flota...")
