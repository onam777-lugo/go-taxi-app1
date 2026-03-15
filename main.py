import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="GO TAXI", page_icon="🚖")
st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🚖 GO TAXI - Píritu</h1>", unsafe_allow_html=True)

try:
    # 1. Conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    # Limpiamos los nombres de las columnas por si acaso (quita espacios y pone todo en mayúsculas)
    df.columns = df.columns.str.strip().str.upper()

    # 2. Ordenar (Disponible > Ocupado > No Laborando)
    # Si en tu Excel la columna se llama diferente, cámbiala aquí:
    col_estatus = 'ESTATUS' 
    col_nombre = 'NOMBRE'
    col_telf = 'TELEFONO'

    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df[col_estatus].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    # 3. Colores
    colores = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

    # 4. Mostrar Tarjetas
    for _, fila in df.iterrows():
        color = colores.get(fila[col_estatus], '#000000')
        # Limpiar el teléfono para que WhatsApp no falle
        numero = str(fila[col_telf]).split('.')[0].replace(" ", "").replace("+", "")
        
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding: 15px; margin-bottom: 5px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin:0; color: #333;">{fila[col_nombre]}</h3>
                <p style="color: {color}; font-weight: bold; margin: 5px 0;">● {fila[col_estatus]}</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button(f"📞 LLAMAR", f"tel:{numero}", use_container_width=True)
        with c2:
            st.link_button(f"💬 WHATSAPP", f"https://wa.me/{numero}", use_container_width=True)
        st.markdown("---")

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.info("Revisa que las columnas en tu Excel se llamen exactamente: NOMBRE, TELEFONO y ESTATUS")
