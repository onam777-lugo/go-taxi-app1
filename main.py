import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la App
st.set_page_config(page_title="GO TAXI", page_icon="🚖")
st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🚖 GO TAXI</h1>", unsafe_allow_html=True)

try:
    # 2. Conexión al Excel
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    # Limpiamos nombres de columnas (quita espacios y pone en mayúsculas)
    df.columns = df.columns.str.strip().str.upper()

    # 3. Lógica de Orden (Disponible arriba)
    prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(prioridad).fillna(4)
    df = df.sort_values('Orden')

    # 4. Colores
    colores = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

    # 5. Dibujar las tarjetas
    for _, fila in df.iterrows():
        color = colores.get(fila['ESTATUS'], '#000000')
        # Limpiar el número de teléfono
        numero = str(fila['TELEFONO']).split('.')[0].replace(" ", "").replace("+", "")
        
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding: 15px; margin-bottom: 5px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin:0; color: #333;">{fila['NOMBRE']}</h3>
                <p style="color: {color}; font-weight: bold; margin: 5px 0;">● {fila['ESTATUS']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.link_button(f"📞 LLAMAR", f"tel:{numero}", use_container_width=True)
        with c2:
            st.link_button(f"💬 WHATSAPP", f"https://wa.me/{numero}?text=Hola,%20necesito%20un%20servicio%20de%20GO%20TAXI", use_container_width=True)
        st.markdown("---")

except Exception as e:
    st.warning("Configurando conexión... Por favor, añade el link del Excel en los Secrets de Streamlit.")
