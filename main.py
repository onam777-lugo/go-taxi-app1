import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="GO TAXI", page_icon="🚖")
st.title("🚖 GO TAXI - Píritu")

# Conexión directa
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Aquí forzamos el enlace directo por si los Secrets fallan
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url)

    # Ordenar por Estatus
    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    colores = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

    for _, fila in df.iterrows():
        color = colores.get(fila['ESTATUS'], '#000000')
        # Limpiar número para WhatsApp
        num = str(fila['TELEFONO']).split('.')[0]
        
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding: 15px; margin-bottom: 10px; border-radius: 10px; background-color: #f8f9fa;">
                <h3 style="margin:0;">{fila['NOMBRE']}</h3>
                <p style="color: {color}; font-weight: bold; margin: 5px 0;">● {fila['ESTATUS']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button(f"📞 LLAMAR", f"tel:{num}", use_container_width=True)
        with c2:
            st.link_button(f"💬 WHATSAPP", f"https://wa.me/58{num}", use_container_width=True)

except Exception as e:
    st.error(f"Error de conexión: {e}")
